
from pydantic import BaseModel

from .match_timing import match_timing


class MatchSound(BaseModel):
	name: str
	file_extension: str
	match_time_sec: float


match_sounds: list[MatchSound]


def update_match_sounds():
	global match_sounds
	match_sounds = [
		MatchSound(name='start', file_extension='wav', match_time_sec=0),
		MatchSound(
			name='end', file_extension='wav', match_time_sec=float(match_timing.auto_duration_sec)
		),
		MatchSound(
			name='resume',
			file_extension='wav',
			match_time_sec=float(match_timing.auto_duration_sec + match_timing.pause_duration_sec),
		),
		MatchSound(
			name='warning_gituar',
			file_extension='wav',
			match_time_sec=float(
				match_timing.auto_duration_sec
				+ match_timing.pause_duration_sec
				+ match_timing.teleop_duration_sec
				- match_timing.warning_remaining_duration_sec
			),
		),
		MatchSound(
			name='end',
			file_extension='wav',
			match_time_sec=float(
				match_timing.auto_duration_sec
				+ match_timing.pause_duration_sec
				+ match_timing.teleop_duration_sec
			),
		),
		MatchSound(name='abort', file_extension='wav', match_time_sec=-1),
		MatchSound(name='match_result', file_extension='wav', match_time_sec=-1),
	]
