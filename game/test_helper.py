from .foul import Foul
from .score import CageStatus, EndgameStatus, Score
from .score_elements import ScoreElements


def score_1() -> Score:
    return Score(
        fouls=[
            Foul(is_major=True, team_id=7641, rule_id=13),
            Foul(is_major=False, team_id=6998, rule_id=14),
            Foul(is_major=False, team_id=6998, rule_id=14),
            Foul(is_major=True, team_id=7641, rule_id=15),
            Foul(is_major=True, team_id=7641, rule_id=15),
            Foul(is_major=True, team_id=7641, rule_id=15),
            Foul(is_major=True, team_id=7641, rule_id=15),
        ],
        leave_statuses=[True, True, False],
        score_elements=score_elements_1(),
        cage_statuses=[CageStatus.SHALLOW, CageStatus.SHALLOW, CageStatus.DEEP],
        endgame_statuses=[EndgameStatus.PARK, EndgameStatus.NONE, EndgameStatus.CAGE_LEFT],
        playoff_dq=False,
    )


def score_2() -> Score:
    return Score(
        leave_statuses=[True, True, False],
        bypass_statuses=[False, False, True],
        score_elements=score_elements_2(),
        cage_statuses=[CageStatus.SHALLOW, CageStatus.SHALLOW, CageStatus.DEEP],
        endgame_statuses=[EndgameStatus.PARK, EndgameStatus.NONE, EndgameStatus.CAGE_RIGHT],
        playoff_dq=False,
    )


def score_elements_1():
    return ScoreElements(
        auto_net_algae=2,
        auto_processor_algae=1,
        teleop_net_algae=0,
        teleop_processor_algae=1,
        auto_trough_coral=0,
        teleop_trough_coral=2,
        auto_scoring=[
            [True, False, False],
            [True, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
        ],
        branches=[
            [True, False, False],
            [True, False, False],
            [True, False, False],
            [True, False, False],
            [True, False, False],
            [True, False, False],
            [True, False, False],
            [False, True, False],
            [False, True, False],
            [False, True, False],
            [False, True, False],
            [False, True, False],
        ],
        branch_algaes=[
            [True, False],
            [False, False],
            [False, False],
            [False, False],
            [False, False],
            [False, False],
        ],
    )


def score_elements_2():
    return ScoreElements(
        auto_net_algae=0,
        auto_processor_algae=0,
        teleop_net_algae=0,
        teleop_processor_algae=0,
        auto_trough_coral=2,
        teleop_trough_coral=3,
        auto_scoring=[
            [True, True, True],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [False, False, False],
        ],
        branches=[
            [True, True, True],
            [True, False, False],
            [True, False, False],
            [True, True, True],
            [True, False, False],
            [False, True, False],
            [False, False, True],
            [False, False, False],
            [False, True, False],
            [False, False, True],
            [False, True, True],
            [False, False, False],
        ],
        branch_algaes=[
            [False, False],
            [False, False],
            [False, False],
            [False, False],
            [False, False],
            [False, False],
        ],
    )
