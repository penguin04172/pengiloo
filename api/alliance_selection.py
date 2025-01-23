from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

import models
import tournament

from .arena import api_arena

router = APIRouter('/alliance_selection', tags=['alliance_selection'])

aliance_selection_time_limit_sec = 45


class AllianceSelectionResponse(BaseModel):
    alliances: list[models.Alliance]
    ranked_teams: list[models.AllianceSelectionRankedTeam]
    next_row: int
    next_col: int
    time_limit_sec: int


def determine_next_cell() -> tuple[int, int]:
    for i, alliance in enumerate(api_arena.alliance_selection_alliances):
        if alliance.team_ids[0] == 0:
            return i, 0
        if alliance.team_ids[1] == 0:
            return i, 1

    if api_arena.event.selection_round_2_order == 'F':
        for i, alliance in enumerate(api_arena.alliance_selection_alliances):
            if alliance.team_ids[2] == 0:
                return i, 2
    else:
        for i, alliance in reversed(list(enumerate(api_arena.alliance_selection_alliances))):
            if alliance.team_ids[2] == 0:
                return i, 2

    if api_arena.event.selection_round_3_order == 'F':
        for i, alliance in enumerate(api_arena.alliance_selection_alliances):
            if alliance.team_ids[3] == 0:
                return i, 3
    else:
        for i, alliance in reversed(list(enumerate(api_arena.alliance_selection_alliances))):
            if alliance.team_ids[3] == 0:
                return i, 3

    return -1, -1


def can_modify_alliance_selection():
    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
    if len(matches) > 0:
        return False
    return True


def can_reset_alliance_selection():
    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
    for match in matches:
        if match.is_complete():
            return False
    return True


@router.get('/')
async def get_alliance_selection():
    next_row, next_col = determine_next_cell()
    return AllianceSelectionResponse(
        alliances=api_arena.alliance_selection_alliances,
        ranked_teams=api_arena.alliance_selection_ranked_teams,
        next_row=next_row,
        next_col=next_col,
        time_limit_sec=aliance_selection_time_limit_sec,
    )


@router.post('/')
async def post_alliance_selection(request: Request):
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    body = await request.json()
    for i, alliance in enumerate(api_arena.alliance_selection_alliances):
        for j in range(len(alliance.team_ids)):
            team_id = body.get(f'selection{i}_{j}', 0)
            if team_id == 0:
                api_arena.alliance_selection_alliances[i].team_ids[j] = 0
            else:
                found = False
                for k, team in enumerate(api_arena.alliance_selection_ranked_teams):
                    if team.team_id == team_id:
                        if team.picked:
                            raise HTTPException(
                                status_code=400,
                                detail=f'Team {team_id} has already been picked',
                            )

                        found = True
                        api_arena.alliance_selection_alliances[i].team_ids[j] = team_id
                        api_arena.alliance_selection_ranked_teams[k].picked = True
                        break

                if not found:
                    raise HTTPException(
                        status_code=404, detail=f'Team {team_id} not found in ranked teams'
                    )

    # if ticker

    await api_arena.alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/start')
async def start_alliance_selection():
    if len(api_arena.alliance_selection_alliances) > 0:
        raise HTTPException(status_code=400, detail='Alliance selection has already started')

    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    api_arena.alliance_selection_alliances = []
    teams_per_alliance = 3

    if api_arena.event.selection_round_3_order != '':
        teams_per_alliance = 4

    for i in range(api_arena.event.num_playoff_alliance):
        api_arena.alliance_selection_alliances.append(
            models.Alliance(id=i + 1, team_ids=[0] * teams_per_alliance)
        )

    rankings = models.read_all_rankings()
    api_arena.alliance_selection_ranked_teams = [
        models.AllianceSelectionRankedTeam(team_id=ranking.team_id, rank=ranking.rank, picked=False)
        for ranking in rankings
    ]

    await api_arena.alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/reset')
async def reset_alliance_selection():
    if not can_reset_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    models.truncate_alliance()

    api_arena.alliance_selection_alliances = []
    api_arena.alliance_selection_ranked_teams = []

    await api_arena.alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/finalize')
async def finalize_alliance_selection(start_time: datetime):
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    for alliance in api_arena.alliance_selection_alliances:
        for team_id in alliance.team_ids:
            if team_id <= 0:
                raise HTTPException(status_code=400, detail='Alliance selection not complete')

    for alliance in api_arena.alliance_selection_alliances:
        alliance.line_up[0] = alliance.team_ids[1]
        alliance.line_up[1] = alliance.team_ids[0]
        alliance.line_up[2] = alliance.team_ids[2]

        models.create_alliance(alliance)

    api_arena.create_playoff_matches(start_time)
    tournament.calculate_team_cards(models.MatchType.PLAYOFF)
    models.backup_db(api_arena.event.name, 'alliace_selection')

    if api_arena.event.tba_publishing_enabled:
        pass

    await api_arena.score_posted_notifier.notify()

    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, False)
    if len(matches) > 0:
        api_arena.load_match(matches[0])

    return {'status': 'success'}
