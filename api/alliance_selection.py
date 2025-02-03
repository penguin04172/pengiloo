import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import models
import tournament
import ws

from .arena import get_arena

router = APIRouter('/alliance_selection', tags=['alliance_selection'])

alliance_selection_time_limit_sec = 45


class AllianceSelectionResponse(BaseModel):
    alliances: list[models.Alliance]
    ranked_teams: list[models.AllianceSelectionRankedTeam]
    next_row: int
    next_col: int
    time_limit_sec: int


def determine_next_cell() -> tuple[int, int]:
    for i, alliance in enumerate(get_arena().alliance_selection_alliances):
        if alliance.team_ids[0] == 0:
            return i, 0
        if alliance.team_ids[1] == 0:
            return i, 1

    if get_arena().event.selection_round_2_order == 'F':
        for i, alliance in enumerate(get_arena().alliance_selection_alliances):
            if alliance.team_ids[2] == 0:
                return i, 2
    else:
        for i, alliance in reversed(list(enumerate(get_arena().alliance_selection_alliances))):
            if alliance.team_ids[2] == 0:
                return i, 2

    if get_arena().event.selection_round_3_order == 'F':
        for i, alliance in enumerate(get_arena().alliance_selection_alliances):
            if alliance.team_ids[3] == 0:
                return i, 3
    else:
        for i, alliance in reversed(list(enumerate(get_arena().alliance_selection_alliances))):
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
async def get_alliance_selection() -> AllianceSelectionResponse:
    next_row, next_col = determine_next_cell()
    return AllianceSelectionResponse(
        alliances=get_arena().alliance_selection_alliances,
        ranked_teams=get_arena().alliance_selection_ranked_teams,
        next_row=next_row,
        next_col=next_col,
        time_limit_sec=alliance_selection_time_limit_sec,
    )


@router.post('/')
async def post_alliance_selection(request: Request) -> dict:
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    body = await request.json()
    for i, alliance in enumerate(get_arena().alliance_selection_alliances):
        for j in range(len(alliance.team_ids)):
            team_id = body.get(f'selection{i}_{j}', 0)
            if team_id == 0:
                get_arena().alliance_selection_alliances[i].team_ids[j] = 0
            else:
                found = False
                for k, team in enumerate(get_arena().alliance_selection_ranked_teams):
                    if team.team_id == team_id:
                        if team.picked:
                            raise HTTPException(
                                status_code=400,
                                detail=f'Team {team_id} has already been picked',
                            )

                        found = True
                        get_arena().alliance_selection_alliances[i].team_ids[j] = team_id
                        get_arena().alliance_selection_ranked_teams[k].picked = True
                        break

                if not found:
                    raise HTTPException(
                        status_code=404, detail=f'Team {team_id} not found in ranked teams'
                    )

    # if ticker

    await get_arena().alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/start')
async def start_alliance_selection() -> dict:
    if len(get_arena().alliance_selection_alliances) > 0:
        raise HTTPException(status_code=400, detail='Alliance selection has already started')

    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    get_arena().alliance_selection_alliances = []
    teams_per_alliance = 3

    if get_arena().event.selection_round_3_order != '':
        teams_per_alliance = 4

    for i in range(get_arena().event.num_playoff_alliance):
        get_arena().alliance_selection_alliances.append(
            models.Alliance(id=i + 1, team_ids=[0] * teams_per_alliance)
        )

    rankings = models.read_all_rankings()
    get_arena().alliance_selection_ranked_teams = [
        models.AllianceSelectionRankedTeam(team_id=ranking.team_id, rank=ranking.rank, picked=False)
        for ranking in rankings
    ]

    await get_arena().alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/reset')
async def reset_alliance_selection() -> dict:
    if not can_reset_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    models.truncate_alliance()

    get_arena().alliance_selection_alliances = []
    get_arena().alliance_selection_ranked_teams = []

    await get_arena().alliance_selection_notifier.notify()
    return {'status': 'success'}


@router.post('/finalize')
async def finalize_alliance_selection(start_time: datetime) -> dict:
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    for alliance in get_arena().alliance_selection_alliances:
        for team_id in alliance.team_ids:
            if team_id <= 0:
                raise HTTPException(status_code=400, detail='Alliance selection not complete')

    for alliance in get_arena().alliance_selection_alliances:
        alliance.line_up[0] = alliance.team_ids[1]
        alliance.line_up[1] = alliance.team_ids[0]
        alliance.line_up[2] = alliance.team_ids[2]

        models.create_alliance(alliance)

    get_arena().create_playoff_matches(start_time)
    tournament.calculate_team_cards(models.MatchType.PLAYOFF)
    models.backup_db(get_arena().event.name, 'alliace_selection')

    if get_arena().event.tba_publishing_enabled:
        pass

    await get_arena().score_posted_notifier.notify()

    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, False)
    if len(matches) > 0:
        get_arena().load_match(matches[0])

    return {'status': 'success'}


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(websocket, get_arena().alliance_selection_notifier)
    )

    global alliance_selection_time_limit_sec

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'set_timer':
                if 'time_limit_sec' not in data['data']:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'time_limit_sec not provided'}}
                    )
                    continue
                alliance_selection_time_limit_sec = int(data['data']['time_limit_sec'])

            elif message_type == 'start_timer':
                if not get_arena().alliance_selection_show_timer:
                    get_arena().alliance_selection_show_timer = True
                    get_arena().alliance_selection_time_remaining_sec = (
                        alliance_selection_time_limit_sec
                    )
                    await get_arena().alliance_selection_notifier.notify()

            elif message_type == 'stop_timer':
                get_arena().alliance_selection_show_timer = False
                get_arena().alliance_selection_time_remaining_sec = 0
                await get_arena().alliance_selection_notifier.notify()
    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass
