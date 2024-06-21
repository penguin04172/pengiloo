from pydantic import BaseModel
import random

class RankingField(BaseModel):
    ranking_points: int = 0
    coopertition_points: int = 0
    match_points: int = 0
    auto_points: int = 0
    stage_points: int = 0
    random: float = random.random()
    wins: int = 0
    losses: int = 0
    ties: int = 0
    disqualifications: int = 0
    played: int = 0

class Ranking(BaseModel):
    team_id: int
    rank: int
    previous_rank: int = 0
    fields: RankingField = RankingField()

    class Config:
        from_attributes = True