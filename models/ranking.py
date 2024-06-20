from pony.orm import *
from pydantic import BaseModel
from typing import List
import random
from .database import db

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

class Ranking(RankingField):
    team_id: int
    rank: int
    previous_rank: int = 0
    ranking_field: RankingField = RankingField()

    class Config:
        from_attributes = True

class RankingDB(db.Entity):
    team_id = PrimaryKey(int, auto=False)
    rank = Optional(int)
    previous_rank = Optional(int)
    ranking_fields = Required(Json)

@db_session
def create_ranking(ranking: Ranking):
    return Ranking(**RankingDB(**ranking.model_dump(exclude_none=True)).to_dict())

@db_session
def read_ranking_for_team(team_id: int):
    ranking = RankingDB.get(team_id=team_id)
    return None if ranking is None else Ranking(**ranking.to_dict())

@db_session
def update_ranking(ranking: Ranking):
    ranking = RankingDB.get(team_id=ranking.team_id)
    if ranking is None:
        return None
    
    ranking.set(**ranking.model_dump(exclude_none=True))
    return Ranking(**ranking.to_dict())

@db_session
def delete_ranking(team_id: int):
    RankingDB[team_id].delete()

def truncate_ranking():
    db.drop_table(RankingDB._table_, with_all_data=True)
    db.create_tables(True)

@db_session
def read_all_rankings():
    rankings = RankingDB.select().order_by(RankingDB.rank)
    
    return [Ranking(**rank.to_dict()) for rank in rankings]

def replace_all_rankings(rankings: List[Ranking]):
    truncate_ranking()

    for rank in rankings:
        create_ranking(rank)