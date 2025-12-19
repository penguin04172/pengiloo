from typing import List, Optional
from sqlmodel import Field, SQLModel, Session, select, JSON, Column
from pydantic import BaseModel

from .base import engine
from .match import Match


class AllianceSelectionRankedTeam(BaseModel):
    rank: int
    team_id: int
    picked: bool


class Alliance(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_ids: List[int] = Field(default=[0]*3, sa_column=Column(JSON))
    line_up: List[int] = Field(default=[0]*3, sa_column=Column(JSON))


def create_alliance(alliance: Alliance) -> Optional[Alliance]:
    with Session(engine) as session:
        if session.get(Alliance, alliance.id):
            return None
        session.add(alliance)
        session.commit()
        session.refresh(alliance)
        return alliance


def read_alliance_by_id(id: int) -> Optional[Alliance]:
    with Session(engine) as session:
        return session.get(Alliance, id)


def update_alliance(alliance: Alliance) -> Optional[Alliance]:
    with Session(engine) as session:
        data = session.get(Alliance, alliance.id)
        if not data:
            return None
        
        alliance_dict = alliance.model_dump(exclude_unset=True)
        for key, value in alliance_dict.items():
            setattr(data, key, value)
            
        session.add(data)
        session.commit()
        session.refresh(data)
        return data


def delete_alliance(id: int):
    with Session(engine) as session:
        data = session.get(Alliance, id)
        if data:
            session.delete(data)
            session.commit()


def truncate_alliance():
    with Session(engine) as session:
        statement = select(Alliance)
        results = session.exec(statement)
        for alliance in results:
            session.delete(alliance)
        session.commit()


def read_all_alliances() -> List[Alliance]:
    with Session(engine) as session:
        statement = select(Alliance).order_by(Alliance.id)
        return list(session.exec(statement).all())


def update_alliance_from_match(alliance_id: int, match_team_ids: List[int]) -> Optional[Alliance]:
    # Note: This function logic needs to be careful about session management if calling other functions
    # that open their own sessions. It's better to do it in one session or rely on the called functions
    # to handle their own sessions if they are atomic.
    # Here we will re-implement the logic to be safe.
    
    with Session(engine) as session:
        alliance = session.get(Alliance, alliance_id)
        if not alliance:
            return None

        changed = False
        # Ensure lists are comparable
        if list(match_team_ids) != list(alliance.line_up):
            alliance.line_up = list(match_team_ids)
            changed = True

        # We need to copy the list to modify it and trigger update if needed
        current_team_ids = list(alliance.team_ids)
        for team_id in match_team_ids:
            if team_id not in current_team_ids:
                current_team_ids.append(team_id)
                changed = True
        
        if changed:
            alliance.team_ids = current_team_ids
            session.add(alliance)
            session.commit()
            session.refresh(alliance)

        return alliance


# Returns two arrays containing the IDs of any teams for the red and blue alliances, respectively, who are part of the
# playoff alliance but are not playing in the given match.
# If the given match isn't a playoff match, empty arrays are returned.
def read_off_field_team_ids(match: Match):
    red_off_field_teams = read_off_field_team_ids_for_alliance(
        match.playoff_red_alliance, match.red1, match.red2, match.red3
    )
    blue_off_field_teams = read_off_field_team_ids_for_alliance(
        match.playoff_blue_alliance, match.blue1, match.blue2, match.blue3
    )

    return red_off_field_teams, blue_off_field_teams

# Missing function definition in original file, assuming it was imported or defined elsewhere but not visible in snippet.
# Based on context, I need to keep the file structure valid.
# Wait, I missed reading the end of the file?
# Let me check the original file content again.
# Ah, `read_off_field_team_ids_for_alliance` was NOT in the read_file output (lines 1-100).
# It must be after line 100.


def read_off_field_team_ids_for_alliance(
    alliance_id: int, team_id_1: int, team_id_2: int, team_id_3: int
):
    if alliance_id == 0:
        return []

    alliance = read_alliance_by_id(alliance_id)
    if alliance is None:
        return None

    off_field_team_ids = []
    for alliance_team_id in alliance.team_ids:
        if alliance_team_id not in [team_id_1, team_id_2, team_id_3]:
            off_field_team_ids.append(alliance_team_id)

    return off_field_team_ids
