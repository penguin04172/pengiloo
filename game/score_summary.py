from enum import IntEnum

from pydantic import BaseModel


class ScoreSummary(BaseModel):
    leave_points: int = 0
    auto_points: int = 0
    coral_points: int = 0
    algae_points: int = 0
    cage_points: int = 0
    barge_points: int = 0
    match_points: int = 0
    foul_points: int = 0
    score: int = 0
    coopertition_criteria_met: bool = False
    coopertition_bonus: bool = False
    num_coral_each_level: list[int] = [0] * 4
    num_coral_levels_goal: int = 0
    auto_bonus_ranking_point: bool = False
    coral_bonus_ranking_point: bool = False
    barge_bonus_ranking_point: bool = False
    bonus_ranking_points: int = 0
    num_opponent_major_fouls: int = 0

    # TBA Field
    park_points: int = 0
    processor_points: int = 0
    net_points: int = 0
    level_1_points: int = 0
    level_2_points: int = 0
    level_3_points: int = 0
    level_4_points: int = 0


class MatchStatus(IntEnum):
    MATCH_SCHEDULE = 0
    MATCH_HIDDEN = 1
    RED_WON_MATCH = 2
    BLUE_WON_MATCH = 3
    TIE_MATCH = 4


def compare_points(red_points: int, blue_points: int) -> MatchStatus:
    if red_points > blue_points:
        return MatchStatus.RED_WON_MATCH

    if red_points < blue_points:
        return MatchStatus.BLUE_WON_MATCH

    return MatchStatus.TIE_MATCH


def determine_match_status(
    red_score_summary: ScoreSummary,
    blue_score_summary: ScoreSummary,
    apply_playoff_tiebreakers: bool,
) -> MatchStatus:
    status = compare_points(red_score_summary.score, blue_score_summary.score)
    if status != MatchStatus.TIE_MATCH:
        return status

    if apply_playoff_tiebreakers:
        status = compare_points(
            red_score_summary.num_opponent_major_fouls, blue_score_summary.num_opponent_major_fouls
        )
        if status != MatchStatus.TIE_MATCH:
            return status

        status = compare_points(red_score_summary.auto_points, blue_score_summary.auto_points)
        if status != MatchStatus.TIE_MATCH:
            return status

        status = compare_points(red_score_summary.barge_points, blue_score_summary.barge_points)
        if status != MatchStatus.TIE_MATCH:
            return status

    return MatchStatus.TIE_MATCH
