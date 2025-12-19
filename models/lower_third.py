from typing import Optional, List
from sqlmodel import Field, SQLModel, Session, select
from pydantic import BaseModel

from .base import engine


class LowerThird(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    top_text: Optional[str] = None
    bottom_text: Optional[str] = None
    display_order: int
    award_id: Optional[int] = None


def create_lower_third(lower_third: LowerThird) -> LowerThird:
    with Session(engine) as session:
        session.add(lower_third)
        session.commit()
        session.refresh(lower_third)
        return lower_third


def read_lower_third_by_id(id: int) -> Optional[LowerThird]:
    with Session(engine) as session:
        return session.get(LowerThird, id)


def update_lower_third(lower_third: LowerThird) -> Optional[LowerThird]:
    with Session(engine) as session:
        data = session.get(LowerThird, lower_third.id)
        if not data:
            return None

        lt_dict = lower_third.model_dump(exclude_unset=True)
        for key, value in lt_dict.items():
            setattr(data, key, value)
            
        session.add(data)
        session.commit()
        session.refresh(data)
        return data


def delete_lower_third(id: int):
    with Session(engine) as session:
        lt = session.get(LowerThird, id)
        if lt:
            session.delete(lt)
            session.commit()


def truncate_lower_thirds():
    with Session(engine) as session:
        statement = select(LowerThird)
        results = session.exec(statement)
        for lt in results:
            session.delete(lt)
        session.commit()


def read_all_lower_thirds() -> List[LowerThird]:
    with Session(engine) as session:
        statement = select(LowerThird).order_by(LowerThird.display_order)
        return list(session.exec(statement).all())


def read_lower_third_by_award_id(award_id: int) -> List[LowerThird]:
    with Session(engine) as session:
        statement = select(LowerThird).where(LowerThird.award_id == award_id)
        return list(session.exec(statement).all())


def read_next_lower_third_display_order() -> int:
    lower_third_list = read_all_lower_thirds()
    if len(lower_third_list) == 0:
        return 1
    return lower_third_list[-1].display_order + 1
