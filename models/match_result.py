from pony.orm import Json, Optional, PrimaryKey, Required, db_session, desc
from pydantic import BaseModel

from game.score import Score

from .base import db
from .match import MatchType


class MatchResult(BaseModel):
    id: int = None
    match_id: int
    play_number: int = 0
    match_type: MatchType
    red_score: Score = Score()
    blue_score: Score = Score()
    red_cards: dict[str, str] = {}
    blue_cards: dict[str, str] = {}

    class Config:
        from_attributes = True

    def red_score_summary(self):
        return self.red_score.summarize(self.blue_score)

    def blue_score_summary(self):
        return self.blue_score.summarize(self.red_score)

    def correct_playoff_score(self):
        self.red_score.playoff_dq = (
            'red' in self.red_cards.values() or 'dq' in self.red_cards.values()
        )
        self.blue_score.playoff_dq = (
            'red' in self.blue_cards.values() or 'dq' in self.blue_cards.values()
        )


class MatchResultDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    match_id = Optional(int)
    play_number = Optional(int)
    match_type = Required(int)
    red_score = Optional(Json)
    blue_score = Optional(Json)
    red_cards = Optional(Json)
    blue_cards = Optional(Json)


@db_session
def create_match_result(match_result: MatchResult):
    return MatchResult(**MatchResultDB(**match_result.model_dump(exclude_none=True)).to_dict())


@db_session
def read_match_result_for_match(match_id: int):
    result_list = MatchResultDB.select(match_id=match_id)
    if len(result_list) == 0:
        return None

    match_result = result_list.order_by(desc(MatchResultDB.play_number)).first()
    return MatchResult(**match_result.to_dict())


@db_session
def update_match_result(match_result: MatchResult):
    result = MatchResultDB.get(match_id=match_result.match_id, play_number=match_result.play_number)
    if result is None:
        return None
    result.set(**match_result.model_dump(exclude_none=True))
    return MatchResult(**result.to_dict())


@db_session
def delete_match_result(id: int):
    MatchResultDB[id].delete()


def truncate_match_results():
    db.drop_table(table_name=MatchResultDB._table_, with_all_data=True)
    db.create_tables()
