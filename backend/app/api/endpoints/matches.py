from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from backend.app.db.engine import get_session
from backend.app.models.match import Match, MatchType, MatchStatus
from backend.app.models.teams import Team
from backend.app.models.schedule import ScheduleBlock
from backend.app.services.tournament.scheduler import Scheduler
from backend.app.services.tournament.advancement import BracketAdvancement
from backend.app.models.alliance import Alliance
from backend.app.models.event import Event, PlayoffType
from backend.app.services.tournament.bracket import BracketGenerator

router = APIRouter()


class ScheduleRequest(BaseModel):
    total_matches: Optional[int] = None
    matches_per_team: Optional[int] = None
    teams_per_alliance: int = 3


@router.post("/generate", response_model=List[Match])
async def generate_schedule(
    request: ScheduleRequest, session: AsyncSession = Depends(get_session)
):
    # 1. Get all teams
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    team_ids = [t.id for t in teams]

    if not team_ids:
        raise HTTPException(status_code=400, detail="No teams found in database")

    if len(team_ids) < request.teams_per_alliance * 2:
        raise HTTPException(
            status_code=400, detail="Not enough teams to generate schedule"
        )

    # Determine total matches
    if request.matches_per_team:
        needed = (len(team_ids) * request.matches_per_team) / (
            2 * request.teams_per_alliance
        )
        total_matches = math.ceil(needed)
    elif request.total_matches:
        total_matches = request.total_matches
    else:
        raise HTTPException(
            status_code=400, detail="Must provide total_matches or matches_per_team"
        )

    # 2. Generate Schedule
    scheduler = Scheduler(team_ids, request.teams_per_alliance)
    try:
        new_matches = scheduler.generate(total_matches)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Assign Times based on Schedule Blocks
    blocks_result = await session.execute(
        select(ScheduleBlock).where(ScheduleBlock.type == MatchType.QUALIFICATION)
    )
    blocks = blocks_result.scalars().all()

    if blocks:
        scheduler.assign_times(new_matches, blocks)

    # 4. Clear existing Qualification matches
    await session.execute(delete(Match).where(Match.type == MatchType.QUALIFICATION))

    # 5. Save new matches
    for match in new_matches:
        session.add(match)

    await session.commit()

    return new_matches


@router.post("/generate_playoffs", response_model=List[Match])
async def generate_playoffs(session: AsyncSession = Depends(get_session)):
    # 1. Get Event Settings
    event_res = await session.execute(select(Event))
    event = event_res.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Get Alliances
    alliances_res = await session.execute(select(Alliance))
    alliances = sorted(
        alliances_res.scalars().all(),
        key=lambda a: int(a.name.split()[-1]) if a.name.split()[-1].isdigit() else a.id,
    )

    if len(alliances) != 8:
        raise HTTPException(
            status_code=400, detail="Currently only supports 8 alliances"
        )

    # 3. Generate Bracket
    if event.playoff_type == PlayoffType.DOUBLE_ELIMINATION:
        new_matches = BracketGenerator.generate_double_elimination_8(alliances)
    elif event.playoff_type == PlayoffType.SINGLE_ELIMINATION:
        new_matches = BracketGenerator.generate_single_elimination_8(alliances)
    else:
        raise HTTPException(status_code=400, detail="Unsupported playoff type")

    # 4. Clear existing Playoff matches
    await session.execute(delete(Match).where(Match.type == MatchType.PLAYOFF))

    # 5. Save new matches
    for match in new_matches:
        session.add(match)

    await session.commit()
    return new_matches


@router.get("/", response_model=List[Match])
async def read_matches(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Match))
    matches = result.scalars().all()
    return matches


@router.post("/", response_model=Match)
async def create_match(match: Match, session: AsyncSession = Depends(get_session)):
    session.add(match)
    await session.commit()
    await session.refresh(match)
    return match


@router.get("/{match_id}", response_model=Match)
async def read_match(match_id: int, session: AsyncSession = Depends(get_session)):
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.patch("/{match_id}", response_model=Match)
async def update_match(
    match_id: int, match_update: Match, session: AsyncSession = Depends(get_session)
):
    db_match = await session.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    match_data = match_update.model_dump(exclude_unset=True)
    match_data.pop("id", None)

    for key, value in match_data.items():
        setattr(db_match, key, value)

    # Check for Playoff Advancement
    if db_match.type == MatchType.PLAYOFF and db_match.status in [
        MatchStatus.RED_WON_MATCH,
        MatchStatus.BLUE_WON_MATCH,
    ]:
        await BracketAdvancement.advance_playoff(session, db_match)

    session.add(db_match)
    await session.commit()
    await session.refresh(db_match)
    return db_match


@router.delete("/{match_id}")
async def delete_match(match_id: int, session: AsyncSession = Depends(get_session)):
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    await session.delete(match)
    await session.commit()
    return {"ok": True}
