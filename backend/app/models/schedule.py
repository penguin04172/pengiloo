from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from backend.app.models.match import MatchType


class ScheduleBlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Morning Block")
    type: MatchType = Field(default=MatchType.QUALIFICATION)
    start_time: datetime
    end_time: datetime
    match_interval_sec: int = Field(default=420)  # 7 minutes
