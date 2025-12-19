from typing import Optional, List

from sqlmodel import Field, SQLModel, Session, select

from .base import engine


class SponsorSlide(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subtitle: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    image: Optional[str] = None
    display_time_sec: int = 0
    display_order: Optional[int] = None


def create_sponsor_slide(sponsor_slide: SponsorSlide) -> Optional[SponsorSlide]:
    with Session(engine) as session:
        if sponsor_slide.id and session.get(SponsorSlide, sponsor_slide.id):
            return None
        session.add(sponsor_slide)
        session.commit()
        session.refresh(sponsor_slide)
        return sponsor_slide


def read_all_sponsor_slides() -> List[SponsorSlide]:
    with Session(engine) as session:
        statement = select(SponsorSlide).order_by(SponsorSlide.display_order)
        return list(session.exec(statement).all())


def read_sponsor_slide_by_id(id: int) -> Optional[SponsorSlide]:
    with Session(engine) as session:
        return session.get(SponsorSlide, id)


def update_sponsor_slide(sponsor_slide: SponsorSlide) -> Optional[SponsorSlide]:
    with Session(engine) as session:
        sponsor_slide_db = session.get(SponsorSlide, sponsor_slide.id)
        if not sponsor_slide_db:
            return None

        ss_dict = sponsor_slide.model_dump(exclude_unset=True)
        for key, value in ss_dict.items():
            setattr(sponsor_slide_db, key, value)

        session.add(sponsor_slide_db)
        session.commit()
        session.refresh(sponsor_slide_db)
        return sponsor_slide_db


def delete_sponsor_slide(id: int):
    with Session(engine) as session:
        sponsor_slide = session.get(SponsorSlide, id)
        if sponsor_slide:
            session.delete(sponsor_slide)
            session.commit()


def truncate_sponsor_slides():
    with Session(engine) as session:
        statement = select(SponsorSlide)
        results = session.exec(statement)
        for sponsor_slide in results:
            session.delete(sponsor_slide)
        session.commit()


def read_next_sponsor_slide_display_order() -> int:
    slides = read_all_sponsor_slides()
    return 1 if len(slides) == 0 else (slides[-1].display_order or 0) + 1
