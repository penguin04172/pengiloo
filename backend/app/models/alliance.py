from typing import Optional
from sqlmodel import SQLModel, Field


class Alliance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="")  # e.g. "Alliance 1"
    captain_team_id: Optional[int] = Field(default=None)
    pick1_team_id: Optional[int] = Field(default=None)
    pick2_team_id: Optional[int] = Field(default=None)
    pick3_team_id: Optional[int] = Field(default=None)  # Backup
