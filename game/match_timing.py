from pydantic import BaseModel


class MatchTiming(BaseModel):
	warmup_duration_sec: int = 0
	auto_duration_sec: int = 15
	pause_duration_sec: int = 3
	teleop_duration_sec: int = 135
	warning_remaining_duration_sec: int = 20
	timeout_duration_sec: int = 0


match_timing = MatchTiming()


def get_duration_to_auto_end():
	return match_timing.warmup_duration_sec + match_timing.auto_duration_sec


def get_duration_to_teleop_start():
	return (
		match_timing.warmup_duration_sec
		+ match_timing.auto_duration_sec
		+ match_timing.pause_duration_sec
	)


def get_duration_to_teleop_end():
	return (
		match_timing.warmup_duration_sec
		+ match_timing.auto_duration_sec
		+ match_timing.pause_duration_sec
		+ match_timing.teleop_duration_sec
	)
