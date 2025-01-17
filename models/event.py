from enum import IntEnum

from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

import game

from .base import db


class PlayoffType(IntEnum):
    DOUBLE_ELIMINATION = 0
    SINGLE_ELIMINATION = 1


class Event(BaseModel):
    name: str | None = None
    playoff_type: int | None = None
    num_playoff_alliance: int = 8
    selection_round_2_order: str | None = None
    selection_round_3_order: str | None = None
    tba_download_enabled: bool | None = None
    tba_publishing_enabled: bool | None = None
    tba_event_code: str | None = None
    tba_secret_id: str | None = None
    tba_secret: str | None = None
    nexus_enabled: bool | None = None
    network_security_enabled: bool | None = None
    ap_address: str | None = None
    ap_password: str | None = None
    ap_channel: int | None = None
    switch_address: str | None = None
    switch_password: str | None = None
    plc_address: str | None = None
    admin_password: str | None = None
    team_sign_red_1_id: int = 0
    team_sign_red_2_id: int = 0
    team_sign_red_3_id: int = 0
    team_sign_red_timer_id: int = 0
    team_sign_blue_1_id: int = 0
    team_sign_blue_2_id: int = 0
    team_sign_blue_3_id: int = 0
    team_sign_blue_timer_id: int = 0
    warmup_duration_sec: int | None = None
    auto_duration_sec: int | None = None
    pause_duration_sec: int | None = None
    teleop_duration_sec: int | None = None
    warning_remaining_duration_sec: int | None = None
    melody_bonus_threshold_without_coop: int | None = None
    melody_bonus_threshold_with_coop: int | None = None
    amplification_note_limit: int | None = None
    amplification_duration_sec: int | None = None

    class Config:
        from_attributes = True


class EventDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default='Untitled Event')
    playoff_type = Required(int, default=PlayoffType.DOUBLE_ELIMINATION)
    num_playoff_alliance = Required(int, default=8)
    selection_round_2_order = Required(str, default='L')
    selection_round_3_order = Optional(str)
    tba_download_enabled = Required(bool, default=True)
    tba_publishing_enabled = Required(bool, default=False)
    tba_event_code = Optional(str)
    tba_secret_id = Optional(str)
    tba_secret = Optional(str)
    nexus_enabled = Required(bool, default=False)
    network_security_enabled = Required(bool, default=False)
    ap_address = Optional(str)
    ap_password = Optional(str)
    ap_channel = Optional(int, default=36)
    switch_address = Optional(str)
    switch_password = Optional(str)
    plc_address = Optional(str)
    admin_password = Optional(str)
    team_sign_red_1_id = Optional(int, default=0)
    team_sign_red_2_id = Optional(int, default=0)
    team_sign_red_3_id = Optional(int, default=0)
    team_sign_red_timer_id = Optional(int, default=0)
    team_sign_blue_1_id = Optional(int, default=0)
    team_sign_blue_2_id = Optional(int, default=0)
    team_sign_blue_3_id = Optional(int, default=0)
    team_sign_blue_timer_id = Optional(int, default=0)
    warmup_duration_sec = Required(int, default=game.timing.warmup_duration_sec)
    auto_duration_sec = Required(int, default=game.timing.auto_duration_sec)
    pause_duration_sec = Required(int, default=game.timing.pause_duration_sec)
    teleop_duration_sec = Required(int, default=game.timing.teleop_duration_sec)
    warning_remaining_duration_sec = Required(
        int, default=game.timing.warning_remaining_duration_sec
    )
    melody_bonus_threshold_without_coop = Required(
        int, default=game.specific.melody_bonus_threshold_without_coop
    )
    melody_bonus_threshold_with_coop = Required(
        int, default=game.specific.melody_bonus_threshold_with_coop
    )
    amplification_note_limit = Required(int, default=game.specific.amplification_note_limit)
    amplification_duration_sec = Required(int, default=game.specific.amplification_duration_sec)


@db_session
def read_event_settings():
    all_event_settings = EventDB.select()

    if len(all_event_settings) == 1:
        return Event(**all_event_settings.first().to_dict())

    event_settings = EventDB()
    return Event(**event_settings.to_dict())


@db_session
def update_event_settings(event_settings: Event):
    event = EventDB.select().first()
    event.set(**event_settings.model_dump(exclude_none=True))
    return Event(**event.to_dict())
