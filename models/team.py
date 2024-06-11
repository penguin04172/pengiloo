from pony.orm import *
from pydantic import BaseModel
from .database import db

class Team(BaseModel):
    id: int
    name: str | None = None
    nickname: str | None = None
    city: str | None = None
    state_prov: str | None = None
    school_name: str | None = None
    rookie_year: int | None = None
    robot_name: str | None = None
    accomplishments: str | None = None
    wpakey: str | None = None
    yellow_card: bool | None = None
    has_connected: bool | None = None
    fta_notes: str | None = None

class TeamDB(db.Entity):
    id = PrimaryKey(int, auto=False)
    name = Optional(str)
    nickname = Optional(str)
    city = Optional(str)
    state_prov = Optional(str)
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
    return list(TeamDB.select())

@db_session
def read_team_by_id(id: int):
    return TeamDB[id].to_dict()

@db_session
def create_team(team: Team):
    if TeamDB.get(id=team.id) is not None:
        return None
    team = TeamDB(**team.model_dump(exclude_none=True))
    return team.to_dict()

@db_session
def update_team(team: Team):
    TeamDB[team.id].set(**team.model_dump(exclude_none=True))
    return TeamDB[team.id].to_dict()

@db_session
def delete_team(id: int):
    TeamDB[id].delete()

@db_session
def truncate_teams():
    db.drop_table(table_name=str(TeamDB), with_all_data=True)
    db.create_tables()