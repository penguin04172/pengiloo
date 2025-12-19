from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Session, select
from pydantic import BaseModel

from .base import engine
from .match import MatchType


class ScheduledBreak(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_type: int
    type_order_before: int
    time: datetime
    duration_sec: int
    description: Optional[str] = None


def create_scheduled_break(scheduled_break: ScheduledBreak) -> Optional[ScheduledBreak]:
    with Session(engine) as session:
        if scheduled_break.id and session.get(ScheduledBreak, scheduled_break.id):
            return None
        session.add(scheduled_break)
        session.commit()
        session.refresh(scheduled_break)
        return scheduled_break


def read_scheduled_breaks_by_match_type(match_type: int) -> List[ScheduledBreak]:
    with Session(engine) as session:
        statement = select(ScheduledBreak).where(ScheduledBreak.match_type == match_type)
        return list(session.exec(statement).all())


def read_scheduled_break_by_id(id: int) -> Optional[ScheduledBreak]:
    with Session(engine) as session:
        return session.get(ScheduledBreak, id)


def read_scheduled_break_by_match_type_order(match_type: int, type_order: int) -> Optional[ScheduledBreak]:
    with Session(engine) as session:
        statement = select(ScheduledBreak).where(
            ScheduledBreak.match_type == match_type,
            ScheduledBreak.type_order_before == type_order
        )
        return session.exec(statement).first()


def update_scheduled_break(scheduled_break: ScheduledBreak) -> Optional[ScheduledBreak]:
    with Session(engine) as session:
        sb_db = session.get(ScheduledBreak, scheduled_break.id)
        if not sb_db:
            return None
        
        data = scheduled_break.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(sb_db, key, value)
            
        session.add(sb_db)
        session.commit()
        session.refresh(sb_db)
        return sb_db


def delete_scheduled_breaks_by_match_type(match_type: int):
    with Session(engine) as session:
        statement = select(ScheduledBreak).where(ScheduledBreak.match_type == match_type)
        results = session.exec(statement)
        for sb in results:
            session.delete(sb)
        session.commit()


def truncate_scheduled_breaks():
    with Session(engine) as session:
        statement = select(ScheduledBreak)
        results = session.exec(statement)
        for sb in results:
            session.delete(sb)
        session.commit()
