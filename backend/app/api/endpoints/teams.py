from typing import List
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.engine import get_session
from backend.app.models.teams import Team

router = APIRouter()


@router.post("/import")
async def import_teams(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a CSV file."
        )

    content = await file.read()
    decoded_content = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(decoded_content))

    imported_count = 0
    for row in csv_reader:
        try:
            team_id = int(row.get("id") or row.get("team_number") or 0)
            if team_id == 0:
                continue

            # Check if team exists
            db_team = await session.get(Team, team_id)
            if db_team:
                # Update existing
                for key, value in row.items():
                    if hasattr(db_team, key) and value:
                        # Handle boolean conversion
                        if key in ["yellow_card", "has_connected"]:
                            value = str(value).lower() in ["true", "1", "yes"]
                        # Handle int conversion
                        elif key in ["rookie_year"]:
                            try:
                                value = int(value)
                            except ValueError:
                                continue
                        setattr(db_team, key, value)
            else:
                # Create new
                team_data = {}
                for key, value in row.items():
                    # Map CSV columns to model fields if needed, or assume matching names
                    if key == "team_number":
                        key = "id"

                    # Simple type conversion
                    if key in ["yellow_card", "has_connected"]:
                        value = str(value).lower() in ["true", "1", "yes"]
                    elif key in ["rookie_year", "id"]:
                        try:
                            value = int(value)
                        except ValueError:
                            value = 0

                    team_data[key] = value

                if "id" not in team_data:
                    team_data["id"] = team_id

                team = Team(**team_data)
                session.add(team)

            imported_count += 1
        except Exception as e:
            print(f"Error importing row {row}: {e}")
            continue

    await session.commit()
    return {"message": f"Successfully imported {imported_count} teams"}


@router.get("/export")
async def export_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team))
    teams = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = [field for field in Team.model_fields.keys()]
    writer.writerow(header)

    # Write data
    for team in teams:
        writer.writerow([getattr(team, field) for field in header])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teams.csv"},
    )


@router.get("/", response_model=List[Team])
async def read_teams(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    return teams


@router.post("/", response_model=Team)
async def create_team(team: Team, session: AsyncSession = Depends(get_session)):
    db_team = await session.get(Team, team.id)
    if db_team:
        raise HTTPException(status_code=400, detail="Team with this ID already exists")
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


@router.get("/{team_id}", response_model=Team)
async def read_team(team_id: int, session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.patch("/{team_id}", response_model=Team)
async def update_team(
    team_id: int, team_update: Team, session: AsyncSession = Depends(get_session)
):
    db_team = await session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    team_data = team_update.model_dump(exclude_unset=True)
    # Remove id from update data to prevent changing primary key
    team_data.pop("id", None)

    for key, value in team_data.items():
        setattr(db_team, key, value)

    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    return db_team


@router.delete("/{team_id}")
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await session.delete(team)
    await session.commit()
    return {"ok": True}
