from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from .base import db


class LowerThird(BaseModel):
    id: int | None = None
    top_text: str | None = None
    bottom_text: str | None = None
    display_order: int = 0
    award_id: int | None = None


class LowerThirdDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    top_text = Optional(str)
    bottom_text = Optional(str)
    display_order = Required(int)
    award_id = Optional(int)


@db_session
def create_lower_third(lower_third: LowerThird):
    return LowerThird(**LowerThirdDB(**lower_third.model_dump(exclude_none=True)).to_dict())


@db_session
def read_lower_third_by_id(id: int):
    lower_third = LowerThirdDB.get(id=id)
    return None if lower_third is None else LowerThird(**lower_third.to_dict())


@db_session
def update_lower_third(lower_third: LowerThird):
    data = LowerThirdDB.get(id=lower_third.id)
    if data is None:
        return None

    data.set(**lower_third.model_dump(exclude_none=True))
    return LowerThird(**data.to_dict())


@db_session
def delete_lower_third(id: int):
    LowerThirdDB[id].delete()


def truncate_lower_thirds():
    db.drop_table(LowerThirdDB._table_, with_all_data=True)
    db.create_tables(True)


@db_session
def read_all_lower_thirds():
    lower_third_list = LowerThirdDB.select().order_by(LowerThirdDB.display_order)
    return [LowerThird(**lower_third.to_dict()) for lower_third in lower_third_list]


@db_session
def read_lower_third_by_award_id(award_id: int):
    lower_third_list = LowerThirdDB.select(award_id=award_id)
    return [LowerThird(**lower_third.to_dict()) for lower_third in lower_third_list]


@db_session
def read_next_lower_third_display_order() -> int:
    lower_third_list = read_all_lower_thirds()
    if len(lower_third_list) == 0:
        return 1
    return lower_third_list[-1].display_order + 1
