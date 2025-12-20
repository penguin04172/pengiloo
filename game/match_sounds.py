from pydantic import BaseModel

from .match_timing import timing


class MatchSound(BaseModel):
    name: str
    file_extension: str
    match_time_sec: float


class MatchSounds:
    _instance = None  # 存放唯一的 arena 實例

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError('Arena is not initialized yet!')
        return cls._instance

    @classmethod
    def set_instance(cls, sounds):
        cls._instance = sounds


def get_sounds() -> MatchSounds | None:
    return MatchSounds.get_instance()


def get_sounds_list() -> list[dict[str, str]]:
    """
    Get a static list of match sounds for web pages.
    This function doesn't require Arena initialization.
    
    **修改聲音列表請在這裡編輯**
    """
    return [
        {'name': 'start', 'file_extension': 'wav'},
        {'name': 'end', 'file_extension': 'wav'},
        {'name': 'resume', 'file_extension': 'wav'},
        {'name': 'warning_sonar', 'file_extension': 'wav'},
        {'name': 'abort', 'file_extension': 'wav'},
        {'name': 'match_result', 'file_extension': 'wav'},
    ]


def update_match_sounds():
    MatchSounds.set_instance(
        [
            MatchSound(name='start', file_extension='wav', match_time_sec=0),
            MatchSound(
                name='end', file_extension='wav', match_time_sec=float(timing.auto_duration_sec)
            ),
            MatchSound(
                name='resume',
                file_extension='wav',
                match_time_sec=float(timing.auto_duration_sec + timing.pause_duration_sec),
            ),
            MatchSound(
                name='warning_sonar',
                file_extension='wav',
                match_time_sec=float(
                    timing.auto_duration_sec
                    + timing.pause_duration_sec
                    + timing.teleop_duration_sec
                    - timing.warning_remaining_duration_sec
                ),
            ),
            MatchSound(
                name='end',
                file_extension='wav',
                match_time_sec=float(
                    timing.auto_duration_sec
                    + timing.pause_duration_sec
                    + timing.teleop_duration_sec
                ),
            ),
            MatchSound(name='abort', file_extension='wav', match_time_sec=-1),
            MatchSound(name='match_result', file_extension='wav', match_time_sec=-1),
        ]
    )
