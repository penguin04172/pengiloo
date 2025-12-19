from enum import IntEnum
from typing import Optional

from sqlmodel import Field, SQLModel, Session, select
from pydantic import BaseModel

import game
from .base import engine

class PlayoffType(IntEnum):
    DOUBLE_ELIMINATION = 0
    SINGLE_ELIMINATION = 1

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = 'Untitled Event'
    playoff_type: int = PlayoffType.DOUBLE_ELIMINATION
    num_playoff_alliances: int = 8
    selection_round_2_order: str = 'L'
    selection_round_3_order: Optional[str] = None
    selection_show_unpicked_teams: bool = True
    tba_download_enabled: bool = True
    tba_publishing_enabled: bool = False
    tba_event_code: Optional[str] = None
    tba_secret_id: Optional[str] = None
    tba_secret: Optional[str] = None
    nexus_enabled: bool = False
    network_security_enabled: bool = False
    ap_address: Optional[str] = None
    ap_password: Optional[str] = None
    ap_channel: int = 36
    switch_address: Optional[str] = None
    switch_password: Optional[str] = None
    plc_address: Optional[str] = None
    admin_password: Optional[str] = None
    team_sign_red_1_id: int = 0
    team_sign_red_2_id: int = 0
    team_sign_red_3_id: int = 0
    team_sign_red_timer_id: int = 0
    team_sign_blue_1_id: int = 0
    team_sign_blue_2_id: int = 0
    team_sign_blue_3_id: int = 0
    team_sign_blue_timer_id: int = 0
    blackmagic_address: Optional[str] = None
    warmup_duration_sec: int = game.timing.warmup_duration_sec
    auto_duration_sec: int = game.timing.auto_duration_sec
    pause_duration_sec: int = game.timing.pause_duration_sec
    teleop_duration_sec: int = game.timing.teleop_duration_sec
    warning_remaining_duration_sec: int = game.timing.warning_remaining_duration_sec
    auto_bonus_coral_threshold: int = game.specific.coral_bonus_num_threshold
    coral_bonus_num_threshold: int = game.specific.coral_bonus_num_threshold
    coral_bonus_level_threshold_without_coop: int = game.specific.coral_bonus_level_threshold_without_coop
    coral_bonus_level_threshold_with_coop: int = game.specific.coral_bonus_level_threshold_with_coop
    barge_bonus_point_threshold: int = game.specific.barge_bonus_point_threshold

def read_event_settings() -> Event:
    with Session(engine) as session:
        statement = select(Event)
        results = session.exec(statement)
        event = results.first()
        
        if not event:
            event = Event()
            session.add(event)
            session.commit()
            session.refresh(event)
            
        return event

def update_event_settings(event_settings: Event) -> Event:
    with Session(engine) as session:
        statement = select(Event)
        event = session.exec(statement).first()
        
        if not event:
            event = Event()
            session.add(event)
        
        event_dict = event_settings.model_dump(exclude_unset=True)
        for key, value in event_dict.items():
            if key != 'id':
                setattr(event, key, value)
        
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
