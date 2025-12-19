import asyncio
from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

import game
import models
import tournament
from web import arena_commands

router = APIRouter(prefix='/match/control', tags=['match_play'])


class MatchControlListItem(BaseModel):
    id: int
    short_name: str
    time: str
    status: game.MatchStatus
    color_class: str = ''

    def __lt__(self, other):
        return (
            self.status == game.MatchStatus.MATCH_SCHEDULE
            and other.status != game.MatchStatus.MATCH_SCHEDULE
        )


class MatchLoadResponse(BaseModel):
    matches_by_type: dict[models.MatchType, list[MatchControlListItem]]
    current_match_type: models.MatchType


@router.get('/load')
async def load_match(request: Request):
    """
    Get list of matches for match control panel.
    Note: Since we can't directly access Arena state in multiprocessing mode,
    we read from database. Current match state comes from WebSocket updates.
    """
    practice_matches = build_match_play_list(models.MatchType.PRACTICE)
    qualification_matches = build_match_play_list(models.MatchType.QUALIFICATION)
    playoff_matches = build_match_play_list(models.MatchType.PLAYOFF)

    matches_by_type = {
        models.MatchType.PRACTICE: practice_matches,
        models.MatchType.QUALIFICATION: qualification_matches,
        models.MatchType.PLAYOFF: playoff_matches,
    }
    
    # Default to practice if we can't determine current match
    current_match_type = models.MatchType.PRACTICE

    return MatchLoadResponse(matches_by_type=matches_by_type, current_match_type=current_match_type)


@router.post('/load_match/{match_id}')
async def api_load_match(match_id: int):
    """Load a specific match into the Arena."""
    if match_id == 0:
        arena_commands.load_test_match()
    else:
        arena_commands.load_match(match_id)
    return {"status": "command_sent", "match_id": match_id}


@router.post('/start')
async def api_start_match(mute_sounds: bool = False):
    """Start the currently loaded match."""
    arena_commands.start_match()
    return {"status": "command_sent"}


@router.post('/abort')
async def api_abort_match():
    """Abort the current match."""
    arena_commands.abort_match()
    return {"status": "command_sent"}


@router.post('/commit')
async def api_commit_results():
    """Commit the current match results."""
    arena_commands.commit_scores()
    return {"status": "command_sent"}


@router.post('/substitute')
async def api_substitute_teams(
    red1: int, red2: int, red3: int, 
    blue1: int, blue2: int, blue3: int
):
    """Substitute teams in the current match."""
    arena_commands.substitute_teams(red1, red2, red3, blue1, blue2, blue3)
    return {"status": "command_sent"}


@router.post('/audience_display/{mode}')
async def api_set_audience_display(mode: str):
    """Set the audience display mode."""
    arena_commands.set_audience_display(mode)
    return {"status": "command_sent", "mode": mode}


async def commit_match_score(
    match: models.Match, match_result: models.MatchResult, is_match_review_edit: bool
):
    """
    Commit a match score to the database.
    This function runs in the Web process and updates the database directly.
    """
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

    return updated_rankings


def build_match_play_list(match_type: models.MatchType):
    """Build a list of matches for display in the match control panel."""
    matches = models.read_matches_by_type(match_type, False)
    match_play_list = []
    for match in matches:
        list_item = MatchControlListItem(
            id=match.id,
            short_name=match.short_name,
            time=match.scheduled_time.strftime('%I:%M %p'),
            status=match.status,
        )
        if match.status == game.MatchStatus.RED_WON_MATCH:
            list_item.color_class = 'red'
        elif match.status == game.MatchStatus.BLUE_WON_MATCH:
            list_item.color_class = 'blue'
        elif match.status == game.MatchStatus.TIE_MATCH:
            list_item.color_class = 'yellow'
        else:
            list_item.color_class = ''

        match_play_list.append(list_item)

    return sorted(match_play_list)
