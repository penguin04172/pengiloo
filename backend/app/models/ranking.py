from sqlmodel import SQLModel, Field


class Ranking(SQLModel, table=True):
    team_id: int = Field(primary_key=True)
    rank: int = Field(default=0)
    ranking_points: int = Field(default=0)
    matches_played: int = Field(default=0)
    average_rp: float = Field(default=0.0)
    total_score: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    ties: int = Field(default=0)
    dq: int = Field(default=0)
