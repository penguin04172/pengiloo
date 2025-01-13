from .amp_speaker import AmpSpeaker
from .foul import Foul
from .score import ENDGAME_STATUS, Score


def score_1() -> Score:
    return Score(
        fouls=[
            Foul(is_technical=True, team_id=7641, rule_id=13),
            Foul(is_technical=False, team_id=6998, rule_id=14),
            Foul(is_technical=False, team_id=6998, rule_id=14),
            Foul(is_technical=True, team_id=7641, rule_id=15),
            Foul(is_technical=True, team_id=7641, rule_id=15),
            Foul(is_technical=True, team_id=7641, rule_id=15),
            Foul(is_technical=True, team_id=7641, rule_id=15),
        ],
        leave_statuses=[True, True, False],
        amp_speaker=AmpSpeaker(
            coop_activated=True,
            auto_amp_notes=1,
            teleop_amp_notes=4,
            auto_speaker_notes=6,
            teleop_unamplified_speaker_notes=1,
            teleop_amplified_speaker_notes=5,
        ),
        endgame_statuses=[ENDGAME_STATUS.park, ENDGAME_STATUS.none, ENDGAME_STATUS.stage_left],
        microphone_statuses=[False, True, True],
        trap_statuses=[True, True, False],
        playoff_dq=False,
    )


def score_2() -> Score:
    return Score(
        leave_statuses=[False, True, False],
        amp_speaker=AmpSpeaker(
            coop_activated=False,
            auto_amp_notes=0,
            teleop_amp_notes=51,
            auto_speaker_notes=8,
            teleop_unamplified_speaker_notes=3,
            teleop_amplified_speaker_notes=23,
        ),
        endgame_statuses=[
            ENDGAME_STATUS.stage_left,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_center,
        ],
        microphone_statuses=[False, True, True],
        trap_statuses=[False, False, False],
        fouls=[],
        playoff_dq=False,
    )
