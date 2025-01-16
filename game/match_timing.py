from pydantic import BaseModel


class MatchTiming(BaseModel):
    warmup_duration_sec: int = 0
    auto_duration_sec: int = 15
    pause_duration_sec: int = 3
    teleop_duration_sec: int = 135
    warning_remaining_duration_sec: int = 20
    timeout_duration_sec: int = 0

    def get_duration_to_auto_end(self):
        return self.warmup_duration_sec + self.auto_duration_sec

    def get_duration_to_teleop_start(self):
        return self.warmup_duration_sec + self.auto_duration_sec + self.pause_duration_sec

    def get_duration_to_teleop_end(self):
        return (
            self.warmup_duration_sec
            + self.auto_duration_sec
            + self.pause_duration_sec
            + self.teleop_duration_sec
        )


timing = MatchTiming()
