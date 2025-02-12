from enum import IntEnum

from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from .base import db


class AwardType(IntEnum):
    judged_award = 0
    finalist_award = 1
    winner_award = 2


class Award(BaseModel):
    id: int | None = None
    type: AwardType = AwardType.judged_award
    award_name: str = ''
    team_id: int = 0
    person_name: str = ''


class AwardDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(int)
    award_name = Optional(str)
    team_id = Optional(int)
    person_name = Optional(str)


@db_session
def create_award(award: Award):
    return Award(**AwardDB(**award.model_dump(exclude_none=True)).to_dict())


@db_session
def read_award_by_id(id: int):
    award = AwardDB.get(id=id)
    return None if award is None else Award(**award.to_dict())


@db_session
def update_award(award: Award):
    data = AwardDB.get(id=award.id)
    if data is None:
        return None
    data.set(**award.model_dump(exclude_none=True))
    return Award(**data.to_dict())


@db_session
def delete_award(id: int):
    AwardDB[id].delete()


def truncate_awards():
    db.drop_table(AwardDB._table_, with_all_data=True)
    db.create_tables(True)


@db_session
def read_all_awards():
    awards = AwardDB.select().order_by(AwardDB.id)
    return [Award(**award.to_dict()) for award in awards]


@db_session
def read_awards_by_type(award_type: AwardType):
    awards = AwardDB.select(type=award_type)
    return [Award(**award.to_dict()) for award in awards]
