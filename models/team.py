from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from .base import db


class Team(BaseModel):
    id: int
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

    class Config:
        from_attributes = True


class TeamDB(db.Entity):
    id = PrimaryKey(int, auto=False)
    name = Optional(str)
    nickname = Optional(str)
    city = Optional(str)
    state_prov = Optional(str)
    country: str = Optional(str)
    school_name = Optional(str)
    rookie_year = Optional(int)
    robot_name = Optional(str)
    accomplishments = Optional(str)
    wpakey = Optional(str)
    yellow_card = Required(bool, default=False)
    has_connected = Required(bool, default=False)
    fta_notes = Optional(str)


@db_session
def read_all_teams():
    return [Team(**t.to_dict()) for t in TeamDB.select()]


@db_session
def read_team_by_id(id: int):
    team = TeamDB.get(id=id)
    if team is None:
        return None

    return Team(**team.to_dict())


@db_session
def create_team(team: Team):
    if TeamDB.get(id=team.id) is not None:
        return None
    team = TeamDB(**team.model_dump(exclude_none=True))
    return Team(**team.to_dict())


@db_session
def update_team(team: Team):
    team_db = TeamDB.get(id=team.id)
    if team_db is None:
        return None
    team_db.set(**team.model_dump(exclude_none=True))
    return Team(**team_db.to_dict())


@db_session
def delete_team(id: int):
    TeamDB[id].delete()


def truncate_teams():
    db.drop_table(table_name=TeamDB._table_, with_all_data=True)
    db.create_tables()
