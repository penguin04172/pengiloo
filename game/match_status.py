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

class MATCH_STATUS(IntEnum):
    match_scheduled = 0
    match_hidden = 1
    red_won_match = 2
    blue_won_match = 3
    tie_match = 4

def compare_points(red_points: int, blue_points: int) -> MATCH_STATUS:
    if red_points > blue_points:
        return MATCH_STATUS.red_won_match
    
    if red_points < blue_points:
        return MATCH_STATUS.blue_won_match
    
    return MATCH_STATUS.tie_match

def determine_match_status(red_score_summary: ScoreSummary, blue_score_summary: ScoreSummary, apply_playoff_tiebreakers: bool) -> MATCH_STATUS:
    status = compare_points(red_score_summary.score, blue_score_summary.score)
    if status != MATCH_STATUS.tie_match:
        return status
    
    if apply_playoff_tiebreakers:
        status = compare_points(red_score_summary.num_opponent_tech_fouls, blue_score_summary.num_opponent_tech_fouls)
        if status != MATCH_STATUS.tie_match:
            return status
        
        status = compare_points(red_score_summary.auto_points, blue_score_summary.auto_points)
        if status != MATCH_STATUS.tie_match:
            return status
        
        status = compare_points(red_score_summary.stage_points, blue_score_summary.stage_points)
        if status != MATCH_STATUS.tie_match:
            return status
        
    return MATCH_STATUS.tie_match