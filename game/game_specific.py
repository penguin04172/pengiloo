from enum import IntEnum

from pydantic import BaseModel


class TIME_CONSTANT(IntEnum):
    speaker_auto_grace_period_sec = 3
    speaker_teleop_grace_period_sec = 5
    speaker_amplified_grace_period_sec = 3
    coop_teleop_window_sec = 45


class GameSpecific(BaseModel):
    melody_bonus_threshold_without_coop: int = 18
    melody_bonus_threshold_with_coop: int = 15
    amplification_note_limit: int = 4
    amplification_duration_sec: int = 10

    # constant
    BANKED_AMP_NOTE_LIMIT: int = 2
    ENSEMBLE_BONUS_POINT_THRESHOLD: int = 10
    ENSEMBLE_BONUS_ROBOT_THRESHOLD: int = 2


specific = GameSpecific()
