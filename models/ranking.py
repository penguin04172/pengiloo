from typing import Optional, List
from sqlmodel import Field, SQLModel, Session, select
from game.ranking import RankingField
from .base import engine

class Ranking(RankingField, SQLModel, table=True):
    team_id: int = Field(primary_key=True)
    rank: Optional[int] = None
    previous_rank: Optional[int] = None
    
    # Explicitly redeclare fields if needed for SQLModel to pick them up as columns correctly,
    # but usually inheritance works. However, for clarity and to ensure they are columns:
    ranking_points: int = Field(default=0)
    coopertition_points: int = Field(default=0)
    match_points: int = Field(default=0)
    auto_points: int = Field(default=0)
    barge_points: int = Field(default=0)
    rand: float = Field(default=0.0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    ties: int = Field(default=0)
    disqualifications: int = Field(default=0)
    played: int = Field(default=0)


def create_ranking(ranking: Ranking) -> Optional[Ranking]:
    with Session(engine) as session:
        if session.get(Ranking, ranking.team_id):
            return None
        session.add(ranking)
        session.commit()
        session.refresh(ranking)
        return ranking


def read_ranking_for_team(team_id: int) -> Optional[Ranking]:
    with Session(engine) as session:
        return session.get(Ranking, team_id)


def update_ranking(ranking: Ranking) -> Optional[Ranking]:
    with Session(engine) as session:
        ranking_data = session.get(Ranking, ranking.team_id)
        if not ranking_data:
            return None
        
        data = ranking.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(ranking_data, key, value)
            
        session.add(ranking_data)
        session.commit()
        session.refresh(ranking_data)
        return ranking_data


def delete_ranking(team_id: int):
    with Session(engine) as session:
        ranking = session.get(Ranking, team_id)
        if ranking:
            session.delete(ranking)
            session.commit()


def truncate_ranking():
    with Session(engine) as session:
        statement = select(Ranking)
        results = session.exec(statement)
        for ranking in results:
            session.delete(ranking)
        session.commit()


def read_all_rankings() -> List[Ranking]:
    with Session(engine) as session:
        statement = select(Ranking).order_by(Ranking.rank)
        return list(session.exec(statement).all())


def replace_all_rankings(rankings: List[Ranking]):
    # This needs to be atomic ideally
    with Session(engine) as session:
        # Truncate
        statement = select(Ranking)
        results = session.exec(statement)
        for ranking in results:
            session.delete(ranking)
        
        # Insert new
        for rank in rankings:
            session.add(rank)
        
        session.commit()
