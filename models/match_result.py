from typing import Optional, Dict, List
from sqlmodel import Field, SQLModel, Session, select, JSON, Column, desc
from pydantic import BaseModel

from game.score import Score
from .base import engine
from .match import MatchType


class MatchResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: Optional[int] = None
    play_number: Optional[int] = 0
    match_type: int
    red_score: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    blue_score: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    red_cards: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    blue_cards: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))

    def get_red_score(self) -> Score:
        return Score(**self.red_score)

    def get_blue_score(self) -> Score:
        return Score(**self.blue_score)

    def red_score_summary(self):
        return self.get_red_score().summarize(self.get_blue_score())

    def blue_score_summary(self):
        return self.get_blue_score().summarize(self.get_red_score())

    def correct_playoff_score(self):
        # This method modifies the score objects in place, but since we store them as dicts,
        # we need to be careful. This method seems to be used before saving or for calculation.
        # If we want to update the stored dicts, we need to convert back.
        
        r_score = self.get_red_score()
        b_score = self.get_blue_score()
        
        r_score.playoff_dq = (
            'red' in self.red_cards.values() or 'dq' in self.red_cards.values()
        )
        b_score.playoff_dq = (
            'red' in self.blue_cards.values() or 'dq' in self.blue_cards.values()
        )
        
        self.red_score = r_score.model_dump()
        self.blue_score = b_score.model_dump()


def create_match_result(match_result: MatchResult) -> MatchResult:
    with Session(engine) as session:
        # Ensure dicts are dumped if they are objects (though type hint says Dict)
        if hasattr(match_result.red_score, 'model_dump'):
             match_result.red_score = match_result.red_score.model_dump()
        if hasattr(match_result.blue_score, 'model_dump'):
             match_result.blue_score = match_result.blue_score.model_dump()

        session.add(match_result)
        session.commit()
        session.refresh(match_result)
        return match_result


def read_match_result_for_match(match_id: int) -> Optional[MatchResult]:
    with Session(engine) as session:
        statement = select(MatchResult).where(MatchResult.match_id == match_id).order_by(desc(MatchResult.play_number))
        return session.exec(statement).first()


def update_match_result(match_result: MatchResult) -> Optional[MatchResult]:
    with Session(engine) as session:
        statement = select(MatchResult).where(
            MatchResult.match_id == match_result.match_id, 
            MatchResult.play_number == match_result.play_number
        )
        result = session.exec(statement).first()
        
        if not result:
            return None
            
        data = match_result.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(result, key, value)
            
        session.add(result)
        session.commit()
        session.refresh(result)
        return result


def delete_match_result(id: int):
    with Session(engine) as session:
        result = session.get(MatchResult, id)
        if result:
            session.delete(result)
            session.commit()


def truncate_match_results():
    with Session(engine) as session:
        statement = select(MatchResult)
        results = session.exec(statement)
        for result in results:
            session.delete(result)
        session.commit()
