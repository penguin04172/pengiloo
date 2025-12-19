from enum import IntEnum
from typing import Optional, List

from sqlmodel import Field, SQLModel, Session, select
from pydantic import BaseModel

from .base import engine


class AwardType(IntEnum):
    judged_award = 0
    finalist_award = 1
    winner_award = 2


class Award(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: int
    award_name: Optional[str] = None
    team_id: Optional[int] = None
    person_name: Optional[str] = None


def create_award(award: Award) -> Award:
    with Session(engine) as session:
        session.add(award)
        session.commit()
        session.refresh(award)
        return award


def read_award_by_id(id: int) -> Optional[Award]:
    with Session(engine) as session:
        return session.get(Award, id)


def update_award(award: Award) -> Optional[Award]:
    with Session(engine) as session:
        data = session.get(Award, award.id)
        if not data:
            return None
        
        award_dict = award.model_dump(exclude_unset=True)
        for key, value in award_dict.items():
            setattr(data, key, value)
            
        session.add(data)
        session.commit()
        session.refresh(data)
        return data


def delete_award(id: int):
    with Session(engine) as session:
        award = session.get(Award, id)
        if award:
            session.delete(award)
            session.commit()


def truncate_awards():
    with Session(engine) as session:
        statement = select(Award)
        results = session.exec(statement)
        for award in results:
            session.delete(award)
        session.commit()


def read_all_awards() -> List[Award]:
    with Session(engine) as session:
        statement = select(Award).order_by(Award.id)
        return list(session.exec(statement).all())


def read_awards_by_type(award_type: int) -> List[Award]:
    with Session(engine) as session:
        statement = select(Award).where(Award.type == award_type)
        return list(session.exec(statement).all())
