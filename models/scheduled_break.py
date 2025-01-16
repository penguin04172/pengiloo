from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from .base import db
from .match import MatchType


class ScheduledBreak(BaseModel):
    id: int | None = None
    match_type: MatchType
    type_order_before: int
    time: datetime
    duration_sec: int
    description: str = ''

    class Config:
        from_attributes = True


class ScheduledBreakDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    match_type = Required(int)
    type_order_before = Required(int)
    time = Required(datetime)
    duration_sec = Required(int)
    description = Optional(str)


@db_session
def create_scheduled_break(scheduled_break: ScheduledBreak):
    if ScheduledBreakDB.get(id=scheduled_break.id) is not None:
        return None
    scheduled_break = ScheduledBreakDB(**scheduled_break.model_dump(exclude_none=True))
    return ScheduledBreak(**scheduled_break.to_dict())


@db_session
def read_scheduled_breaks_by_match_type(match_type: MatchType):
    return [
        ScheduledBreak(**t.to_dict())
        for t in ScheduledBreakDB.select()
        if t.match_type == match_type
    ]


@db_session
def read_scheduled_break_by_id(id: int):
    scheduled_break = ScheduledBreakDB.get(id=id)
    if scheduled_break is None:
        return None
    return ScheduledBreak(**scheduled_break.to_dict())


@db_session
def read_scheduled_break_by_match_type_order(match_type: MatchType, type_order: int):
    scheduled_break = ScheduledBreakDB.get(match_type=match_type, type_order_before=type_order)
    if scheduled_break is None:
        return None
    return ScheduledBreak(**scheduled_break.to_dict())


@db_session
def update_scheduled_break(scheduled_break: ScheduledBreak):
    scheduled_break_db = ScheduledBreakDB.get(id=scheduled_break.id)
    if scheduled_break_db is None:
        return None
    scheduled_break_db.set(**scheduled_break.model_dump(exclude_none=True))
    return ScheduledBreak(**scheduled_break_db.to_dict())


@db_session
def delete_scheduled_breaks_by_match_type(match_type: MatchType):
    ScheduledBreakDB.select(match_type=match_type.value).delete(bulk=True)


def truncate_scheduled_breaks():
    db.drop_table(ScheduledBreakDB._table_, with_all_data=True)
    db.create_tables()
