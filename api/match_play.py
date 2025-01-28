from datetime import datetime

import game
import models
import tournament

from .arena import api_arena


async def commit_match_score(
    match: models.Match, match_result: models.MatchResult, is_match_review_edit: bool
):
    updated_rankings = game.Rankings()
    if match.type == models.MatchType.PLAYOFF:
        match_result.correct_playoff_score()

    match.score_commit_at = datetime.now()
    red_score_summary = match_result.red_score_summary()
    blue_score_summary = match_result.blue_score_summary()
    match.status = game.determine_match_status(
        red_score_summary, blue_score_summary, match.use_tiebreak_criteria
    )
    if match.type != models.MatchType.TEST:
        if match_result.play_number == 0:
            prev_match_result = models.read_match_result_for_match(match.id)
            if prev_match_result is not None:
                match_result.play_number = prev_match_result.play_number + 1
            else:
                match_result.play_number = 1

            models.create_match_result(match_result)
        else:
            models.update_match_result(match_result)

        models.update_match(match)

        if match.should_update_cards():
            tournament.calculate_team_cards(match.type)

        if match.should_update_ranking():
            rankings = tournament.calculate_rankings(is_match_review_edit)
            updated_rankings = rankings

        if match.should_update_playoff_matches():
            models.update_alliance_from_match(
                match.playoff_red_alliance, [match.red1, match.red2, match.red3]
            )
            models.update_alliance_from_match(
                match.playoff_blue_alliance, [match.blue1, match.blue2, match.blue3]
            )

            api_arena.update_playoff_tournament()

        if api_arena.playoff_tournament.is_complete():
            winner_alliance_id = api_arena.playoff_tournament.winning_alliance_id()
            finalist_alliance_id = api_arena.playoff_tournament.finalist_alliance_id()

            tournament.create_or_update_winner_and_finalist_awards(
                winner_alliance_id, finalist_alliance_id
            )

        if api_arena.event.tba_publishing_enabled and match.type != models.MatchType.PRACTICE:
            pass

        models.backup_db(api_arena.event.name, f'post_{match.type}_match_{match.short_name}')

    if not is_match_review_edit:
        api_arena.saved_match = match
        api_arena.saved_match_result = match_result
        api_arena.saved_rankings = updated_rankings
        await api_arena.score_posted_notifier.notify()


def get_current_match_result():
    return models.MatchResult(
        match_id=api_arena.current_match.id,
        match_type=api_arena.current_match.type,
        red_score=api_arena.red_realtime_score.current_score,
        blue_score=api_arena.blue_realtime_score.current_score,
        red_cards=api_arena.red_realtime_score.cards,
        blue_cards=api_arena.blue_realtime_score.cards,
    )
