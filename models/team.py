from pony.orm import *
from .database import db

class Team(db.Entity):
    id = PrimaryKey(int, auto=False)
    name = Required(str)
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