from enum import IntEnum

from pony.orm import Optional, PrimaryKey, Required, db_session
from pydantic import BaseModel

import game

from .base import db


class PlayoffType(IntEnum):
    DOUBLE_ELIMINATION = 0
    SINGLE_ELIMINATION = 1


class Event(BaseModel):
    name: str = 'Untitled Event'
    playoff_type: int = PlayoffType.DOUBLE_ELIMINATION
    num_playoff_alliances: int = 8
    selection_round_2_order: str = 'L'
    selection_round_3_order: str = ''
    selection_show_unpicked_teams: bool = True
    tba_download_enabled: bool = False
    tba_publishing_enabled: bool = False
    tba_event_code: str = ''
    tba_secret_id: str = ''
    tba_secret: str = ''
    nexus_enabled: bool = False
    network_security_enabled: bool = False
    ap_address: str = ''
    ap_password: str = ''
    ap_channel: int = 36
    switch_address: str = ''
    switch_password: str = ''
    plc_address: str = ''
    admin_password: str = ''
    team_sign_red_1_id: int = 0
    team_sign_red_2_id: int = 0
    team_sign_red_3_id: int = 0
    team_sign_red_timer_id: int = 0
    team_sign_blue_1_id: int = 0
    team_sign_blue_2_id: int = 0
    team_sign_blue_3_id: int = 0
    team_sign_blue_timer_id: int = 0
    blackmagic_address: str = ''
    warmup_duration_sec: int = game.timing.warmup_duration_sec
    auto_duration_sec: int = game.timing.auto_duration_sec
    pause_duration_sec: int = game.timing.pause_duration_sec
    teleop_duration_sec: int = game.timing.teleop_duration_sec
    warning_remaining_duration_sec: int = game.timing.warning_remaining_duration_sec
    auto_bonus_coral_threshold: int = game.specific.auto_bonus_coral_threshold
    coral_bonus_num_threshold: int = game.specific.coral_bonus_num_threshold
    coral_bonus_level_threshold_without_coop: int = (
        game.specific.coral_bonus_level_threshold_without_coop
    )
    coral_bonus_level_threshold_with_coop: int = game.specific.coral_bonus_level_threshold_with_coop
    barge_bonus_point_threshold: int = game.specific.barge_bonus_point_threshold

    class Config:
        from_attributes = True


class EventDB(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, default='Untitled Event')
    playoff_type = Required(int, default=PlayoffType.DOUBLE_ELIMINATION)
    num_playoff_alliances = Required(int, default=8)
    selection_round_2_order = Required(str, default='L')
    selection_round_3_order = Optional(str)
    selection_show_unpicked_teams = Required(bool, default=True)
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
    team_sign_red_1_id = Required(int, default=0)
    team_sign_red_2_id = Required(int, default=0)
    team_sign_red_3_id = Required(int, default=0)
    team_sign_red_timer_id = Required(int, default=0)
    team_sign_blue_1_id = Required(int, default=0)
    team_sign_blue_2_id = Required(int, default=0)
    team_sign_blue_3_id = Required(int, default=0)
    team_sign_blue_timer_id = Required(int, default=0)
    blackmagic_address = Optional(str)
    warmup_duration_sec = Required(int, default=game.timing.warmup_duration_sec)
    auto_duration_sec = Required(int, default=game.timing.auto_duration_sec)
    pause_duration_sec = Required(int, default=game.timing.pause_duration_sec)
    teleop_duration_sec = Required(int, default=game.timing.teleop_duration_sec)
    warning_remaining_duration_sec = Required(
        int, default=game.timing.warning_remaining_duration_sec
    )
    auto_bonus_coral_threshold = Required(int, default=game.specific.coral_bonus_num_threshold)
    coral_bonus_num_threshold = Required(int, default=game.specific.coral_bonus_num_threshold)
    coral_bonus_level_threshold_without_coop = Required(
        int, default=game.specific.coral_bonus_level_threshold_without_coop
    )
    coral_bonus_level_threshold_with_coop = Required(
        int, default=game.specific.coral_bonus_level_threshold_with_coop
    )
    barge_bonus_point_threshold = Required(int, default=game.specific.barge_bonus_point_threshold)


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
