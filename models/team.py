from typing import Optional, List
from sqlmodel import Field, SQLModel, Session, select
from .base import engine

class Team(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = ''
    nickname: str = ''
    city: str = ''
    state_prov: str = ''
    country: str = ''
    school_name: str = ''
    rookie_year: int = 0
    robot_name: str = ''
    accomplishments: str = ''
    wpakey: str = ''
    yellow_card: bool = False
    has_connected: bool = False
    fta_notes: str = ''

def read_all_teams() -> List[Team]:
    with Session(engine) as session:
        statement = select(Team)
        results = session.exec(statement)
        return list(results.all())

def read_team_by_id(id: int) -> Optional[Team]:
    if not id:
        return None
    with Session(engine) as session:
        return session.get(Team, id)

def create_team(team: Team) -> Optional[Team]:
    with Session(engine) as session:
        if session.get(Team, team.id):
            return None
        session.add(team)
        session.commit()
        session.refresh(team)
        return team

def update_team(team: Team) -> Optional[Team]:
    with Session(engine) as session:
        team_db = session.get(Team, team.id)
        if not team_db:
            return None
        team_data = team.model_dump(exclude_unset=True)
        for key, value in team_data.items():
            setattr(team_db, key, value)
        session.add(team_db)
        session.commit()
        session.refresh(team_db)
        return team_db

def delete_team(id: int):
    with Session(engine) as session:
        team = session.get(Team, id)
        if team:
            session.delete(team)
            session.commit()

def truncate_teams():
    with Session(engine) as session:
        statement = select(Team)
        results = session.exec(statement)
        for team in results:
            session.delete(team)
        session.commit()
