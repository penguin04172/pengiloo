from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from pydantic import BaseModel
from backend.app.models.match import MatchType


class Score(BaseModel):
    # Placeholder for score details.
    # In a real implementation, this would contain all scoring fields.
    auto_points: int = 0
    teleop_points: int = 0
    total_points: int = 0
    ranking_points: int = 0
    fouls: int = 0
    tech_fouls: int = 0
    playoff_dq: bool = False

    def summarize(self, opponent_score: "Score") -> Dict[str, Any]:
        return {
            "total_points": self.total_points,
            "ranking_points": self.ranking_points,
        }


class MatchResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(index=True)
    play_number: int = Field(default=0)
    match_type: MatchType = Field(default=MatchType.TEST)

    # Store complex objects as JSON
    red_score: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    blue_score: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    red_cards: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    blue_cards: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))

    def get_red_score_obj(self) -> Score:
        return Score(**self.red_score)

    def get_blue_score_obj(self) -> Score:
        return Score(**self.blue_score)

    def red_score_summary(self):
        return self.get_red_score_obj().summarize(self.get_blue_score_obj())

    def blue_score_summary(self):
        return self.get_blue_score_obj().summarize(self.get_red_score_obj())

    def correct_playoff_score(self):
        # This logic would need to update the JSON dicts
        red_obj = self.get_red_score_obj()
        blue_obj = self.get_blue_score_obj()

        red_obj.playoff_dq = (
            "red" in self.red_cards.values() or "dq" in self.red_cards.values()
        )
        blue_obj.playoff_dq = (
            "red" in self.blue_cards.values() or "dq" in self.blue_cards.values()
        )

        self.red_score = red_obj.model_dump()
        self.blue_score = blue_obj.model_dump()
