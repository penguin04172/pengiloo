from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.engine import get_session
from backend.app.models.alliance import Alliance
from backend.app.models.event import Event
from backend.app.models.ranking import Ranking
from backend.app.models.teams import Team

router = APIRouter()


@router.get("/", response_model=List[Alliance])
async def read_alliances(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Alliance))
    return result.scalars().all()


@router.post("/init")
async def init_alliances(session: AsyncSession = Depends(get_session)):
    """Initialize alliances based on Event settings and Rankings (for Captains)."""
    # 1. Get Event Settings
    result = await session.execute(select(Event))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    num_alliances = event.num_playoff_alliances

    # 2. Clear existing
    await session.execute(delete(Alliance))

    # 3. Get Top N Rankings for Captains
    # Note: In real FRC, captains can decline. Here we assume auto-assignment for simplicity,
    # or create empty alliances and let user fill captain.
    # Let's create empty alliances first.

    for i in range(num_alliances):
        alliance = Alliance(name=f"Alliance {i + 1}")
        session.add(alliance)

    await session.commit()
    return {"message": "Alliances initialized"}


@router.get("/status")
async def get_selection_status(session: AsyncSession = Depends(get_session)):
    """
    Returns the current state of selection:
    - current_round: str (Captain, Round 2, Round 3, Complete)
    - current_alliance_id: int (The Alliance ID currently picking)
    - current_alliance_index: int (0-based index)
    - available_teams: List[Team] (Teams not yet selected)
    """
    # 1. Get Event & Alliances
    event_res = await session.execute(select(Event))
    event = event_res.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Event settings not found")

    alliances_res = await session.execute(select(Alliance))
    alliances = sorted(
        alliances_res.scalars().all(),
        key=lambda a: int(a.name.split()[-1]) if a.name.split()[-1].isdigit() else a.id,
    )

    if not alliances:
        return {"status": "Not Initialized"}

    num_alliances = len(alliances)

    # 2. Determine Current Slot
    current_slot = None  # (alliance_obj, field_name)
    round_name = "Complete"

    # Check Captains (Round 1) - Always 1 -> N
    for i in range(num_alliances):
        if not alliances[i].captain_team_id:
            current_slot = (alliances[i], "captain_team_id")
            round_name = "Captain"
            break

    if not current_slot:
        # Check Round 2 (Pick 1)
        order = (
            range(num_alliances)
            if event.selection_round_2_order != "L"
            else range(num_alliances - 1, -1, -1)
        )
        for i in order:
            if not alliances[i].pick1_team_id:
                current_slot = (alliances[i], "pick1_team_id")
                round_name = "Round 2 (Pick 1)"
                break

    if not current_slot:
        # Check Round 3 (Pick 2)
        order = (
            range(num_alliances)
            if event.selection_round_3_order != "L"
            else range(num_alliances - 1, -1, -1)
        )
        for i in order:
            if not alliances[i].pick2_team_id:
                current_slot = (alliances[i], "pick2_team_id")
                round_name = "Round 3 (Pick 2)"
                break

    # 3. Get Available Teams
    # Get all picked team IDs
    picked_ids = set()
    for a in alliances:
        if a.captain_team_id:
            picked_ids.add(a.captain_team_id)
        if a.pick1_team_id:
            picked_ids.add(a.pick1_team_id)
        if a.pick2_team_id:
            picked_ids.add(a.pick2_team_id)
        if a.pick3_team_id:
            picked_ids.add(a.pick3_team_id)

    # Get all teams from Ranking (sorted)
    rankings_res = await session.execute(select(Ranking).order_by(Ranking.rank))
    rankings = rankings_res.scalars().all()

    # If no rankings, fallback to Team table? No, selection needs rankings.
    # But we return Team objects
    available_teams = []

    # Map team_id to Team object
    teams_res = await session.execute(select(Team))
    teams_map = {t.id: t for t in teams_res.scalars().all()}

    for r in rankings:
        if r.team_id not in picked_ids:
            if r.team_id in teams_map:
                available_teams.append(teams_map[r.team_id])

    # Also add teams that might not be in ranking (unlikely but safe)
    # ... skip for now

    return {
        "round": round_name,
        "current_alliance": current_slot[0] if current_slot else None,
        "current_field": current_slot[1] if current_slot else None,
        "available_teams": available_teams,
        "alliances": alliances,
    }


@router.post("/pick")
async def make_pick(team_id: int, session: AsyncSession = Depends(get_session)):
    status = await get_selection_status(session)
    if status.get("status") == "Not Initialized":
        raise HTTPException(status_code=400, detail="Alliances not initialized")

    if not status["current_alliance"]:
        raise HTTPException(status_code=400, detail="Selection is complete")

    alliance = status["current_alliance"]
    field = status["current_field"]

    # Update DB
    # We need to fetch the alliance again to attach to session?
    # status['current_alliance'] is a Pydantic model or SQLModel instance?
    # It was returned by get_selection_status which fetched it.
    # But it might be detached. Safer to re-fetch.

    db_alliance = await session.get(Alliance, alliance.id)
    setattr(db_alliance, field, team_id)

    session.add(db_alliance)
    await session.commit()

    return {"ok": True}


@router.post("/undo")
async def undo_pick(session: AsyncSession = Depends(get_session)):
    """Undo the last pick."""
    # To undo, we need to find the *last filled slot*.
    # Reverse logic of get_status

    event_res = await session.execute(select(Event))
    event = event_res.scalars().first()
    alliances_res = await session.execute(select(Alliance))
    alliances = sorted(
        alliances_res.scalars().all(),
        key=lambda a: int(a.name.split()[-1]) if a.name.split()[-1].isdigit() else a.id,
    )
    num_alliances = len(alliances)

    target_slot = None  # (alliance, field)

    # Check Round 3 (Pick 2) - Reverse Order
    # If Order was L (8->1), last pick was 1. So we check 1->8.
    # If Order was Normal (1->8), last pick was 8. So we check 8->1.

    # Actually, we just need to find the "latest" filled slot.
    # Let's check in reverse order of rounds.

    # Round 3
    order = (
        range(num_alliances - 1, -1, -1)
        if event.selection_round_3_order != "L"
        else range(num_alliances)
    )
    for i in order:
        if alliances[i].pick2_team_id:
            target_slot = (alliances[i], "pick2_team_id")
            break

    if not target_slot:
        # Round 2
        order = (
            range(num_alliances - 1, -1, -1)
            if event.selection_round_2_order != "L"
            else range(num_alliances)
        )
        for i in order:
            if alliances[i].pick1_team_id:
                target_slot = (alliances[i], "pick1_team_id")
                break

    if not target_slot:
        # Captains
        for i in range(num_alliances - 1, -1, -1):
            if alliances[i].captain_team_id:
                target_slot = (alliances[i], "captain_team_id")
                break

    if target_slot:
        alliance, field = target_slot
        setattr(alliance, field, None)
        session.add(alliance)
        await session.commit()
        return {"message": "Undone"}

    return {"message": "Nothing to undo"}
