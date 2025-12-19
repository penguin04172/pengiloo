from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel, Session, select

from .base import engine


class ScheduleBlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_type: int
    start_time: datetime
    num_matches: int
    match_spacing_sec: int


def read_schedule_blocks_by_match_type(match_type: int) -> List[ScheduleBlock]:
    with Session(engine) as session:
        statement = select(ScheduleBlock).where(ScheduleBlock.match_type == match_type)
        return list(session.exec(statement).all())


def create_schedule_block(schedule_block: ScheduleBlock) -> Optional[ScheduleBlock]:
    with Session(engine) as session:
        if schedule_block.id and session.get(ScheduleBlock, schedule_block.id):
            return None
        session.add(schedule_block)
        session.commit()
        session.refresh(schedule_block)
        return schedule_block


def delete_schedule_block_by_match_type(match_type: int):
    with Session(engine) as session:
        statement = select(ScheduleBlock).where(ScheduleBlock.match_type == match_type)
        results = session.exec(statement)
        for sb in results:
            session.delete(sb)
        session.commit()


def truncate_schedule_blocks():
    with Session(engine) as session:
        statement = select(ScheduleBlock)
        results = session.exec(statement)
        for sb in results:
            session.delete(sb)
        session.commit()
