from pony.orm import Optional, PrimaryKey, db_session
from pydantic import BaseModel

from .base import db


class SponsorSlide(BaseModel):
    id: int | None = None
    subtitle: str = ''
    line1: str = ''
    line2: str = ''
    image: str = ''
    display_time_sec: int = 0
    display_order: int = None

    class Config:
        from_attributes = True


class SponsorSlideDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    subtitle = Optional(str)
    line1 = Optional(str)
    line2 = Optional(str)
    image = Optional(str)
    display_time_sec = Optional(int)
    display_order = Optional(int)


@db_session
def create_sponsor_slide(sponsor_slide: SponsorSlide):
    if SponsorSlideDB.get(id=sponsor_slide.id) is not None:
        return None
    sponsor_slide = SponsorSlideDB(**sponsor_slide.model_dump(exclude_none=True))
    return SponsorSlide(**sponsor_slide.to_dict())


@db_session
def read_all_sponsor_slides():
    sponsor_slide_list = SponsorSlideDB.select().order_by(SponsorSlideDB.display_order)
    return [SponsorSlide(**s.to_dict()) for s in sponsor_slide_list]


@db_session
def read_sponsor_slide_by_id(id: int):
    sponsor_slide = SponsorSlideDB.get(id=id)
    if sponsor_slide is None:
        return None
    return SponsorSlide(**sponsor_slide.to_dict())


@db_session
def update_sponsor_slide(sponsor_slide: SponsorSlide):
    sponsor_slide_db = SponsorSlideDB.get(id=sponsor_slide.id)
    if sponsor_slide_db is None:
        return None
    sponsor_slide_db.set(**sponsor_slide.model_dump(exclude_none=True))
    return SponsorSlide(**sponsor_slide_db.to_dict())


@db_session
def delete_sponsor_slide(id: int):
    sponsor_slide = SponsorSlideDB.get(id=id)
    if sponsor_slide is None:
        return None
    sponsor_slide.delete()


def truncate_sponsor_slides():
    db.drop_table(table_name=SponsorSlideDB._table_, with_all_data=True)
    db.create_tables()


@db_session
def read_next_sponsor_slide_display_order() -> int:
    sponsor_slide_list = list(SponsorSlideDB.select().order_by(SponsorSlideDB.display_order))
    return 1 if len(sponsor_slide_list) == 0 else sponsor_slide_list[-1].display_order + 1
