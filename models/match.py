from datetime import datetime
from enum import IntEnum

from pony.orm import Json, Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

from game.match_status import MATCH_STATUS

from .base import db


class MATCH_TYPE(IntEnum):
    test = 0
    pratice = 1
    qualification = 2
    playoff = 3


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
    scheduled_time = Optional(datetime, volatile=True)
    long_name = Optional(str)
    short_name = Optional(str)
    name_detail = Optional(str)
    playoff_match_group_id = Optional(str)
    playoff_red_alliance = Optional(int)
    playoff_blue_alliance = Optional(int)
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
    started_at = Optional(datetime, default=datetime(1970, 1, 1, 0, 0), volatile=True)
    score_commit_at = Optional(datetime, default=datetime(1970, 1, 1, 0, 0), volatile=True)
    field_ready_at = Optional(datetime, default=datetime(1970, 1, 1, 0, 0), volatile=True)
    status = Required(int, default=MATCH_STATUS.match_scheduled)
    use_tiebreak_criteria = Optional(bool)
    tba_match_key = Optional(Json)


class Match(BaseModel):
    type: MATCH_TYPE
    type_order: int
    long_name: str | None = None
    short_name: str | None = None
    scheduled_time: datetime | None = None
    name_detail: str | None = None
    playoff_match_group_id: str | None = None
    playoff_red_alliance: int | None = None
    playoff_blue_alliance: int | None = None
    red1: int | None = None
    red1_is_surrogate: bool | None = None
    red2: int | None = None
    red2_is_surrogate: bool | None = None
    red3: int | None = None
    red3_is_surrogate: bool | None = None
    blue1: int | None = None
    blue1_is_surrogate: bool | None = None
    blue2: int | None = None
    blue2_is_surrogate: bool | None = None
    blue3: int | None = None
    blue3_is_surrogate: bool | None = None
    started_at: datetime | None = None
    score_commit_at: datetime | None = None
    field_ready_at: datetime | None = None
    status: MATCH_STATUS | None = None
    use_tiebreak_criteria: bool | None = None
    tba_match_key: TbaMatchKey | None = None

    class Config:
        from_attributes = True


class MatchOut(Match):
    id: int

    def is_complete(self) -> bool:
        return (
            self.status == MATCH_STATUS.red_won_match
            or self.status == MATCH_STATUS.blue_won_match
            or self.status == MATCH_STATUS.tie_match
        )

    def should_allow_substitution(self) -> bool:
        return self.type != MATCH_TYPE.qualification

    def should_allow_nexus_substitution(self) -> bool:
        return self.type == MATCH_TYPE.pratice or self.type == MATCH_TYPE.playoff

    def should_update_cards(self) -> bool:
        return self.type == MATCH_TYPE.qualification or self.type == MATCH_TYPE.playoff

    def should_update_ranking(self) -> bool:
        return self.type == MATCH_TYPE.qualification

    def should_update_playoff_matches(self) -> bool:
        return self.type == MATCH_TYPE.playoff


@db_session
def create_match(match_data: Match):
    match = MatchDB(**match_data.model_dump(exclude_none=True, exclude=['scheduled_time']))
    match.scheduled_time = match_data.scheduled_time
    return MatchOut(**match.to_dict())


@db_session
def read_match_by_id(id: int):
    match = MatchDB.get(id=id)
    return None if match is None else MatchOut(**match.to_dict())


@db_session
def update_match(match_data: Match):
    target = MatchDB.select(type=match_data.type, type_order=match_data.type_order)
    if len(target) == 0:
        return None

    target = target.first()
    target.set(**match_data.model_dump(exclude_none=True))
    return MatchOut(**target.to_dict())


@db_session
def delete_match(id: int):
    MatchDB[id].delete()


def truncate_matches():
    db.drop_table(table_name=MatchDB._table_, with_all_data=True)
    db.create_tables()


@db_session
def read_all_matches():
    return [MatchOut(**m.to_dict()) for m in MatchDB.select()]


@db_session
def read_matches_by_type(match_type: MATCH_TYPE, include_hidden: bool = False):
    matches = MatchDB.select()
    return [
        MatchOut(**m.to_dict())
        for m in matches
        if m.type == match_type and (include_hidden or m.status != MATCH_STATUS.match_hidden)
    ]


@db_session
def read_match_by_type_order(match_type: MATCH_TYPE, type_order: int):
    match = MatchDB.select(type=match_type, type_order=type_order)
    if len(match) == 0:
        return None

    return MatchOut(**match.first().to_dict())
