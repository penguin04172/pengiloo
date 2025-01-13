from datetime import datetime

from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from .base import db
from .match import MATCH_TYPE


class ScheduleBlock(BaseModel):
    id: int | None = None
    match_type: MATCH_TYPE
    start_time: datetime
    num_matches: int
    match_spacing_sec: int

    class Config:
        from_attributes = True


class ScheduleBlockDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    match_type = Required(int)
    start_time = Required(datetime)
    num_matches = Required(int)
    match_spacing_sec = Required(int)


@db_session
def read_schedule_blocks_by_match_type(match_type: MATCH_TYPE):
    return [
        ScheduleBlock(**t.to_dict()) for t in ScheduleBlockDB.select() if t.match_type == match_type
    ]


@db_session
def create_schedule_block(schedule_block: ScheduleBlock):
    if ScheduleBlockDB.get(id=schedule_block.id) is not None:
        return None
    schedule_block = ScheduleBlockDB(**schedule_block.model_dump(exclude_none=True))
    return ScheduleBlock(**schedule_block.to_dict())


@db_session
def delete_schedule_block_by_match_type(match_type: MATCH_TYPE):
    ScheduleBlockDB.select(match_type=match_type.value).delete(bulk=True)


def truncate_schedule_blocks():
    db.drop_table(table_name=ScheduleBlockDB._table_, with_all_data=True)
    db.create_tables()
