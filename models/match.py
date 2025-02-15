from datetime import datetime
from enum import IntEnum

from pony.orm import Json, Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from game.score_summary import MatchStatus

from .base import db


class MatchType(IntEnum):
    TEST = 0
    PRACTICE = 1
    QUALIFICATION = 2
    PLAYOFF = 3


class TbaMatchKey(BaseModel):
    comp_level: str = ''
    set_number: int = 0
    match_number: int = 0

    def __str__(self):
        if self.set_number == 0:
            return f'{self.comp_level}{self.match_number}'
        return f'{self.comp_level}{self.set_number}m{self.match_number}'


class MatchDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(int)
    type_order = Required(int)
    scheduled_time = Required(datetime, volatile=True)
    long_name = Optional(str)
    short_name = Optional(str)
    name_detail = Optional(str)
    playoff_match_group_id = Optional(str)
    playoff_red_alliance = Required(int, default=0)
    playoff_blue_alliance = Required(int, default=0)
    red1 = Optional(int)
    red1_is_surrogate = Optional(bool)
    red2 = Optional(int)
    red2_is_surrogate = Optional(bool)
    red3 = Optional(int)
    red3_is_surrogate = Optional(bool)
    blue1 = Optional(int)
    blue1_is_surrogate = Optional(bool)
    blue2 = Optional(int)
    blue2_is_surrogate = Optional(bool)
    blue3 = Optional(int)
    blue3_is_surrogate = Optional(bool)
    started_at = Optional(datetime, volatile=True)
    score_commit_at = Optional(datetime, volatile=True)
    field_ready_at = Optional(datetime, volatile=True)
    status = Required(int, default=MatchStatus.MATCH_SCHEDULE)
    use_tiebreak_criteria = Optional(bool)
    tba_match_key = Optional(Json)


class Match(BaseModel):
    type: MatchType
    type_order: int
    long_name: str = ''
    short_name: str = ''
    scheduled_time: datetime = datetime.fromtimestamp(0)
    name_detail: str = ''
    playoff_match_group_id: str = ''
    playoff_red_alliance: int = 0
    playoff_blue_alliance: int = 0
    red1: int = 0
    red1_is_surrogate: bool = False
    red2: int = 0
    red2_is_surrogate: bool = False
    red3: int = 0
    red3_is_surrogate: bool = False
    blue1: int = 0
    blue1_is_surrogate: bool = False
    blue2: int = 0
    blue2_is_surrogate: bool = False
    blue3: int = 0
    blue3_is_surrogate: bool = False
    started_at: datetime | None = None
    score_commit_at: datetime | None = None
    field_ready_at: datetime | None = None
    status: MatchStatus = None
    use_tiebreak_criteria: bool | None = None
    tba_match_key: TbaMatchKey = TbaMatchKey()
    id: int = None

    class Config:
        from_attributes = True

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
            'type': self.type,
            'type_order': self.type_order,
            'long_name': self.long_name,
            'short_name': self.short_name,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'name_detail': self.name_detail,
            'playoff_match_group_id': self.playoff_match_group_id,
            'playoff_red_alliance': self.playoff_red_alliance,
            'playoff_blue_alliance': self.playoff_blue_alliance,
            'red1': self.red1,
            'red1_is_surrogate': self.red1_is_surrogate,
            'red2': self.red2,
            'red2_is_surrogate': self.red2_is_surrogate,
            'red3': self.red3,
            'red3_is_surrogate': self.red3_is_surrogate,
            'blue1': self.blue1,
            'blue1_is_surrogate': self.blue1_is_surrogate,
            'blue2': self.blue2,
            'blue2_is_surrogate': self.blue2_is_surrogate,
            'blue3': self.blue3,
            'blue3_is_surrogate': self.blue3_is_surrogate,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'score_commit_at': self.score_commit_at.isoformat() if self.score_commit_at else None,
            'field_ready_at': self.field_ready_at.isoformat() if self.field_ready_at else None,
            'status': self.status,
            'use_tiebreak_criteria': self.use_tiebreak_criteria,
            'tba_match_key': self.tba_match_key.model_dump(),
            'id': self.id,
        }


@db_session
def create_match(match_data: Match):
    match = MatchDB(**match_data.model_dump(exclude_none=True, exclude=['scheduled_time']))
    match.scheduled_time = match_data.scheduled_time
    return Match(**match.to_dict())


@db_session
def read_match_by_id(id: int):
    match = MatchDB.get(id=id)
    return None if match is None else Match(**match.to_dict())


@db_session
def update_match(match_data: Match):
    target = MatchDB.select(type=match_data.type, type_order=match_data.type_order)
    if len(target) == 0:
        return None

    target = target.first()
    target.set(**match_data.model_dump(exclude_none=True))
    return Match(**target.to_dict())


@db_session
def delete_match(id: int):
    MatchDB[id].delete()


def truncate_matches():
    db.drop_table(table_name=MatchDB._table_, with_all_data=True)
    db.create_tables()


@db_session
def read_all_matches():
    return [Match(**m.to_dict()) for m in MatchDB.select()]


@db_session
def read_matches_by_type(match_type: MatchType, include_hidden: bool = False):
    matches = MatchDB.select()
    return sorted(
        [
            Match(**m.to_dict())
            for m in matches
            if m.type == match_type and (include_hidden or m.status != MatchStatus.MATCH_HIDDEN)
        ],
        key=lambda m: m.type_order,
    )


@db_session
def read_match_by_type_order(match_type: MatchType, type_order: int):
    match = MatchDB.select(type=match_type, type_order=type_order)
    if len(match) == 0:
        return None

    return Match(**match.first().to_dict())
