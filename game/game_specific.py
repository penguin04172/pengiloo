from enum import IntEnum

from pydantic import BaseModel


class TimeConstant(IntEnum):
    auto_grace_period_sec = 3
    teleop_grace_period_sec = 3
    cage_grace_period_sec = 3


class GameSpecific(BaseModel):
    coral_bonus_num_threshold: int = 5
    coral_bonus_level_threshold_without_coop: int = 4
    coral_bonus_level_threshold_with_coop: int = 3

    auto_bonus_robot_threshold: int = 3
    auto_bonus_coral_threshold: int = 1

    barge_bonus_point_threshold: int = 14

    coop_bonus_algae_threshold: int = 2


specific = GameSpecific()
