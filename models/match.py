from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Any, Dict

from sqlmodel import Field, SQLModel, Session, select, JSON, Column
from pydantic import BaseModel

from game.score_summary import MatchStatus
from .base import engine

class MatchType(IntEnum):
    TEST = 0
    PRACTICE = 1
    QUALIFICATION = 2
    PLAYOFF = 3

class TbaMatchKey(BaseModel):
    comp_level: str = ''
    set_number: int = 0
    match_number: int = 0

    def __str__(self):
        if self.set_number == 0:
            return f'{self.comp_level}{self.match_number}'
        return f'{self.comp_level}{self.set_number}m{self.match_number}'

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: int
    type_order: int
    scheduled_time: datetime
    long_name: Optional[str] = None
    short_name: Optional[str] = None
    name_detail: Optional[str] = None
    playoff_match_group_id: Optional[str] = None
    playoff_red_alliance: int = 0
    playoff_blue_alliance: int = 0
    red1: Optional[int] = None
    red1_is_surrogate: Optional[bool] = None
    red2: Optional[int] = None
    red2_is_surrogate: Optional[bool] = None
    red3: Optional[int] = None
    red3_is_surrogate: Optional[bool] = None
    blue1: Optional[int] = None
    blue1_is_surrogate: Optional[bool] = None
    blue2: Optional[int] = None
    blue2_is_surrogate: Optional[bool] = None
    blue3: Optional[int] = None
    blue3_is_surrogate: Optional[bool] = None
    started_at: Optional[datetime] = None
    score_commit_at: Optional[datetime] = None
    field_ready_at: Optional[datetime] = None
    status: int = MatchStatus.MATCH_SCHEDULE
    use_tiebreak_criteria: Optional[bool] = None
    tba_match_key: Dict = Field(default_factory=dict, sa_column=Column(JSON))

    def is_complete(self) -> bool:
        return (
            self.status == MatchStatus.RED_WON_MATCH
            or self.status == MatchStatus.BLUE_WON_MATCH
            or self.status == MatchStatus.TIE_MATCH
        )

    def should_allow_substitution(self) -> bool:
        return self.type != MatchType.QUALIFICATION

    def should_allow_nexus_substitution(self) -> bool:
        return self.type == MatchType.PRACTICE or self.type == MatchType.PLAYOFF

    def should_update_cards(self) -> bool:
        return self.type == MatchType.QUALIFICATION or self.type == MatchType.PLAYOFF

    def should_update_ranking(self) -> bool:
        return self.type == MatchType.QUALIFICATION

    def should_update_playoff_matches(self) -> bool:
        return self.type == MatchType.PLAYOFF
    
    def get_tba_match_key(self) -> TbaMatchKey:
        return TbaMatchKey(**self.tba_match_key)

def create_match(match_data: Match) -> Match:
    with Session(engine) as session:
        session.add(match_data)
        session.commit()
        session.refresh(match_data)
        return match_data

def read_match_by_id(id: int) -> Optional[Match]:
    with Session(engine) as session:
        return session.get(Match, id)

def update_match(match_data: Match) -> Optional[Match]:
    with Session(engine) as session:
        statement = select(Match).where(Match.type == match_data.type, Match.type_order == match_data.type_order)
        results = session.exec(statement)
        target = results.first()
        
        if not target:
            return None
        
        match_dict = match_data.model_dump(exclude_unset=True)
        for key, value in match_dict.items():
            setattr(target, key, value)
            
        session.add(target)
        session.commit()
        session.refresh(target)
        return target

def delete_match(id: int):
    with Session(engine) as session:
        match = session.get(Match, id)
        if match:
            session.delete(match)
            session.commit()

def truncate_matches():
    with Session(engine) as session:
        statement = select(Match)
        results = session.exec(statement)
        for match in results:
            session.delete(match)
        session.commit()

def read_all_matches() -> List[Match]:
    with Session(engine) as session:
        statement = select(Match)
        return list(session.exec(statement).all())

def read_matches_by_type(match_type: int, include_hidden: bool = False) -> List[Match]:
    with Session(engine) as session:
        statement = select(Match).where(Match.type == match_type)
        results = session.exec(statement).all()
        filtered = [
            m for m in results
            if include_hidden or m.status != MatchStatus.MATCH_HIDDEN
        ]
        return sorted(filtered, key=lambda m: m.type_order)

def read_match_by_type_order(match_type: int, type_order: int) -> Optional[Match]:
    with Session(engine) as session:
        statement = select(Match).where(Match.type == match_type, Match.type_order == type_order)
        return session.exec(statement).first()
