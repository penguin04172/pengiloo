from pydantic import BaseModel

from .match_timing import timing


class MatchSounds(BaseModel):
    name: str
    file_extension: str
    match_time_sec: float


sounds = list[MatchSounds]()


def update_match_sounds():
    global sounds
    sounds = [
        MatchSounds(name='start', file_extension='wav', match_time_sec=0),
        MatchSounds(
            name='end', file_extension='wav', match_time_sec=float(timing.auto_duration_sec)
        ),
        MatchSounds(
            name='resume',
            file_extension='wav',
            match_time_sec=float(timing.auto_duration_sec + timing.pause_duration_sec),
        ),
        MatchSounds(
            name='warning_gituar',
            file_extension='wav',
            match_time_sec=float(
                timing.auto_duration_sec
                + timing.pause_duration_sec
                + timing.teleop_duration_sec
                - timing.warning_remaining_duration_sec
            ),
        ),
        MatchSounds(
            name='end',
            file_extension='wav',
            match_time_sec=float(
                timing.auto_duration_sec + timing.pause_duration_sec + timing.teleop_duration_sec
            ),
        ),
        MatchSounds(name='abort', file_extension='wav', match_time_sec=-1),
        MatchSounds(name='match_result', file_extension='wav', match_time_sec=-1),
    ]
