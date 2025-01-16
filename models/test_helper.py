from game.test_helper import score_1, score_2

from .match_result import MatchResult, MatchType


def build_test_match_result(match_id: int, play_number: int):
    match_result = MatchResult(
        match_id=match_id, play_number=play_number, match_type=MatchType.QUALIFICATION
    )
    match_result.red_score = score_1()
    match_result.blue_score = score_2()
    match_result.red_cards = {'6998': 'yellow'}
    match_result.blue_cards = {}
    return match_result
