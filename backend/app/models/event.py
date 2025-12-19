from enum import IntEnum
from typing import Optional
from sqlmodel import SQLModel, Field


class PlayoffType(IntEnum):
    SINGLE_ELIMINATION = 0
    DOUBLE_ELIMINATION = 1
    ROUND_ROBIN = 2


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Untitled Event")
    playoff_type: int = Field(default=PlayoffType.DOUBLE_ELIMINATION)
    num_playoff_alliances: int = Field(default=8)
    selection_round_2_order: str = Field(default="L")
    selection_round_3_order: str = Field(default="")
    selection_show_unpicked_teams: bool = Field(default=True)
    tba_download_enabled: bool = Field(default=False)
    tba_publishing_enabled: bool = Field(default=False)
    tba_event_code: str = Field(default="")
    tba_secret_id: str = Field(default="")
    tba_secret: str = Field(default="")
    nexus_enabled: bool = Field(default=False)
    network_security_enabled: bool = Field(default=False)
    ap_address: str = Field(default="")
    ap_password: str = Field(default="")
    ap_channel: int = Field(default=36)
    switch_address: str = Field(default="")
    switch_password: str = Field(default="")
    plc_address: str = Field(default="")
    admin_password: str = Field(default="")
    team_sign_red_1_id: int = Field(default=0)
    team_sign_red_2_id: int = Field(default=0)
    team_sign_red_3_id: int = Field(default=0)
    team_sign_red_timer_id: int = Field(default=0)
    team_sign_blue_1_id: int = Field(default=0)
    team_sign_blue_2_id: int = Field(default=0)
    team_sign_blue_3_id: int = Field(default=0)
    team_sign_blue_timer_id: int = Field(default=0)
    blackmagic_address: str = Field(default="")

    # Game specific timing defaults (Replaced game.timing.* with defaults)
    warmup_duration_sec: int = Field(default=0)
    auto_duration_sec: int = Field(default=15)
    pause_duration_sec: int = Field(default=3)
    teleop_duration_sec: int = Field(default=135)
    warning_remaining_duration_sec: int = Field(default=20)

    # Game specific scoring defaults (Replaced game.specific.* with defaults)
    auto_bonus_coral_threshold: int = Field(default=0)
    coral_bonus_num_threshold: int = Field(default=0)
    coral_bonus_level_threshold_without_coop: int = Field(default=0)
    coral_bonus_level_threshold_with_coop: int = Field(default=0)
    barge_bonus_point_threshold: int = Field(default=0)
