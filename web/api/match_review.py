from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import game
import models
from web.arena import get_arena

from .match_control import commit_match_score, get_current_match_result

router = APIRouter(prefix='/match/review', tags=['match_review'])


class MatchReviewListItem(BaseModel):
    id: int
    short_name: str
    time: str
    red_teams: list[str]
    blue_teams: list[str]
    red_score: int = 0
    blue_score: int = 0
    color_class: str = ''
    is_completed: bool = False


class MatchReviewResponse(BaseModel):
    matches_by_type: dict[models.MatchType, list[MatchReviewListItem]]
    current_match_type: models.MatchType


@router.get('')
async def get_match_review() -> MatchReviewResponse:
    pratice_matches = await build_match_review_list(models.MatchType.PRACTICE)
    qualification_matches = await build_match_review_list(models.MatchType.QUALIFICATION)
    playoff_matches = await build_match_review_list(models.MatchType.PLAYOFF)

    matches_by_type = {
        models.MatchType.PRACTICE: pratice_matches,
        models.MatchType.QUALIFICATION: qualification_matches,
        models.MatchType.PLAYOFF: playoff_matches,
    }
    current_match_type = get_arena().current_match.type
    if current_match_type == models.MatchType.TEST:
        current_match_type = models.MatchType.PRACTICE

    return MatchReviewResponse(
        matches_by_type=matches_by_type,
        current_match_type=current_match_type,
    )


class MatchReviewEditResponse(BaseModel):
    match: models.Match
    match_result: models.MatchResult
    is_current: bool
    rules: dict[int, game.Rule]


@router.get('/{match_id}/edit')
async def get_match_review_edit(match_id: str):
    try:
        match, match_result, is_current = get_match_result_from_request(match_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return MatchReviewEditResponse(
        match=match,
        match_result=match_result,
        is_current=is_current,
        rules=game.get_all_rules(),
    )


@router.post('/{match_id}/edit')
async def post_match_review_edit(match_id: str, match_result: models.MatchResult):
    match, _, is_current = get_match_result_from_request(match_id)

    if match_result.match_id != match.id:
        raise HTTPException(
            status_code=400, detail=f'Match ID {match_result.match_id} does not match'
        )

    if is_current:
        get_arena().red_realtime_score.current_score = match_result.red_score
        get_arena().blue_realtime_score.current_score = match_result.blue_score
        get_arena().red_realtime_score.cards = match_result.red_cards
        get_arena().blue_realtime_score.cards = match_result.blue_cards

        return {'status': 'success'}
    else:
        commit_match_score(match, match_result, True)

        return {'status': 'success'}


def get_match_result_from_request(match_id: str):
    if match_id == 'current':
        return get_arena().current_match, get_current_match_result(), True

    match = models.read_match_by_id(int(match_id))
    if match is None:
        raise ValueError(f'Match {match_id} not found')

    match_result = models.read_match_result_for_match(match.id)
    if match_result is None:
        match_result = models.MatchResult(
            match_id=match.id,
            match_type=match.type,
        )

    return match, match_result, False


async def build_match_review_list(match_type: models.MatchType):
    matches = models.read_matches_by_type(match_type, False)

    match_review_list = []
    for match in matches:
        list_item = MatchReviewListItem(
            id=match.id,
            short_name=match.short_name,
            time=match.scheduled_time.strftime('%b %m/%d %I:%M %p'),
            red_teams=list(map(str, [match.red1, match.red2, match.red3])),
            blue_teams=list(map(str, [match.blue1, match.blue2, match.blue3])),
        )

        result = models.read_match_result_for_match(match.id)
        if result is not None:
            list_item.red_score = result.red_score_summary().score
            list_item.blue_score = result.blue_score_summary().score

        if match.status == game.MatchStatus.RED_WON_MATCH:
            list_item.color_class = 'red'
            list_item.is_completed = True
        elif match.status == game.MatchStatus.BLUE_WON_MATCH:
            list_item.color_class = 'blue'
            list_item.is_completed = True
        elif match.status == game.MatchStatus.TIE_MATCH:
            list_item.color_class = 'yellow'
            list_item.is_completed = True
        else:
            list_item.color_class = ''
            list_item.is_completed = False

        match_review_list.append(list_item)

    return match_review_list
