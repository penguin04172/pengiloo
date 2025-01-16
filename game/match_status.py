from enum import IntEnum

from pydantic import BaseModel


class ScoreSummary(BaseModel):
    leave_points: int = 0
    auto_points: int = 0
    amp_points: int = 0
    speaker_points: int = 0
    stage_points: int = 0
    match_points: int = 0
    foul_points: int = 0
    score: int = 0
    coopertition_criteria_met: bool = False
    coopertition_bonus: bool = False
    num_notes: int = 0
    num_notes_goal: int = 0
    melody_bonus_ranking_point: bool = False
    ensemble_bonus_ranking_point: bool = False
    bonus_ranking_points: int = 0
    num_opponent_tech_fouls: int = 0

    # TBA Field
    park_points: int = 0
    onstage_points: int = 0
    harmony_points: int = 0
    spotlight_points: int = 0
    trap_points: int = 0


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
            red_score_summary.num_opponent_tech_fouls, blue_score_summary.num_opponent_tech_fouls
        )
        if status != MatchStatus.TIE_MATCH:
            return status

        status = compare_points(red_score_summary.auto_points, blue_score_summary.auto_points)
        if status != MatchStatus.TIE_MATCH:
            return status

        status = compare_points(red_score_summary.stage_points, blue_score_summary.stage_points)
        if status != MatchStatus.TIE_MATCH:
            return status

    return MatchStatus.TIE_MATCH
