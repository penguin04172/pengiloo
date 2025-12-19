from enum import IntEnum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from sqlalchemy import JSON, Column


class MatchType(IntEnum):
    TEST = 0
    PRACTICE = 1
    QUALIFICATION = 2
    PLAYOFF = 3


class MatchStatus(IntEnum):
    PRE_MATCH = 0
    START_MATCH = 1
    AUTO_PERIOD = 2
    PAUSE_PERIOD = 3
    TELEOP_PERIOD = 4
    END_MATCH = 5
    RED_WON_MATCH = 6
    BLUE_WON_MATCH = 7
    TIE_MATCH = 8
    ABORTED_MATCH = 9


class TbaMatchKey(BaseModel):
    event_key: str = ""
    match_level: str = ""
    match_number: int = 0
    set_number: int = 0


class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: MatchType = Field(default=MatchType.TEST)
    type_order: int = Field(default=0)
    long_name: str = Field(default="")
    short_name: str = Field(default="")
    scheduled_time: datetime = Field(default_factory=lambda: datetime.fromtimestamp(0))
    name_detail: str = Field(default="")
    playoff_match_group_id: str = Field(default="")
    playoff_red_alliance: int = Field(default=0)
    playoff_blue_alliance: int = Field(default=0)

    # Source for playoff progression (e.g. "W_M1", "L_M2", "A_1")
    red_source: str = Field(default="")
    blue_source: str = Field(default="")

    red1: int = Field(default=0)
    red1_is_surrogate: bool = Field(default=False)
    red2: int = Field(default=0)
    red2_is_surrogate: bool = Field(default=False)
    red3: int = Field(default=0)
    red3_is_surrogate: bool = Field(default=False)
    blue1: int = Field(default=0)
    blue1_is_surrogate: bool = Field(default=False)
    blue2: int = Field(default=0)
    blue2_is_surrogate: bool = Field(default=False)
    blue3: int = Field(default=0)
    blue3_is_surrogate: bool = Field(default=False)
    started_at: Optional[datetime] = Field(default=None)
    score_commit_at: Optional[datetime] = Field(default=None)
    field_ready_at: Optional[datetime] = Field(default=None)
    status: Optional[MatchStatus] = Field(default=None)
    use_tiebreak_criteria: Optional[bool] = Field(default=None)
    tba_match_key: dict = Field(default_factory=dict, sa_column=Column(JSON))

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

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "type_order": self.type_order,
            "long_name": self.long_name,
            "short_name": self.short_name,
            "scheduled_time": self.scheduled_time.isoformat()
            if self.scheduled_time
            else None,
            "name_detail": self.name_detail,
            "playoff_match_group_id": self.playoff_match_group_id,
            "playoff_red_alliance": self.playoff_red_alliance,
            "playoff_blue_alliance": self.playoff_blue_alliance,
            "red1": self.red1,
            "red1_is_surrogate": self.red1_is_surrogate,
            "red2": self.red2,
            "red2_is_surrogate": self.red2_is_surrogate,
            "red3": self.red3,
            "red3_is_surrogate": self.red3_is_surrogate,
            "blue1": self.blue1,
            "blue1_is_surrogate": self.blue1_is_surrogate,
            "blue2": self.blue2,
            "blue2_is_surrogate": self.blue2_is_surrogate,
            "blue3": self.blue3,
            "blue3_is_surrogate": self.blue3_is_surrogate,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "score_commit_at": self.score_commit_at.isoformat()
            if self.score_commit_at
            else None,
            "field_ready_at": self.field_ready_at.isoformat()
            if self.field_ready_at
            else None,
            "status": self.status,
            "use_tiebreak_criteria": self.use_tiebreak_criteria,
            "tba_match_key": self.tba_match_key,
            "id": self.id,
        }
