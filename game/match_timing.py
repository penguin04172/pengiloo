from pydantic import BaseModel


class MatchTiming(BaseModel):
    warmup_duration_sec: int = 0
    auto_duration_sec: int = 15
    pause_duration_sec: int = 3
    teleop_duration_sec: int = 135
    warning_remaining_duration_sec: int = 20
    timeout_duration_sec: int = 0

    @classmethod
    def get_duration_to_auto_end(cls):
        return cls.warmup_duration_sec + cls.auto_duration_sec

    @classmethod
    def get_duration_to_teleop_start(cls):
        return cls.warmup_duration_sec + cls.auto_duration_sec + cls.pause_duration_sec

    @classmethod
    def get_duration_to_teleop_end(cls):
        return (
            cls.warmup_duration_sec
            + cls.auto_duration_sec
            + cls.pause_duration_sec
            + cls.teleop_duration_sec
        )


timing = MatchTiming()
