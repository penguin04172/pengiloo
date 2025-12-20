from datetime import timedelta

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import field
import models
from web import arena_state

from .display_util import enforce_display_configuration, register_display

NUM_NON_PLAYOFF_MATCHES_TO_SHOW = 5
NUM_PLAYOFF_MATCHES_TO_SHOW = 4

router = APIRouter(prefix='/displays/queueing', tags=['displays'])


@router.get('')
async def audience_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(request, display_id, nickname)
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}


class MatchLoadResponse(BaseModel):
    upcoming_matches: list[models.Match]
    red_off_field_teams_by_match: list[list[int]]
    blue_off_field_teams_by_match: list[list[int]]


@router.get('/match_load')
async def match_load() -> MatchLoadResponse:
    match_type = arena_state.get_match_type()
    type_order = arena_state.get_full_state().get('match_type_order', 0)
    matches = models.read_matches_by_type(match_type, False)

    num_matches_to_show = NUM_NON_PLAYOFF_MATCHES_TO_SHOW
    if match_type == models.MatchType.PLAYOFF:
        num_matches_to_show = NUM_PLAYOFF_MATCHES_TO_SHOW

    upcoming_matches = list[models.Match]()
    red_off_field_teams_by_match = list[list[int]]()
    blue_off_field_teams_by_match = list[list[int]]()
    for i, match in enumerate(matches):
        if match.is_complete() or type_order > match.type_order:
            continue
        upcoming_matches.append(match)
        red_off_field_teams, blue_off_field_teams = models.read_off_field_team_ids(match)
        red_off_field_teams_by_match.append(red_off_field_teams)
        blue_off_field_teams_by_match.append(blue_off_field_teams)
        if len(upcoming_matches) == num_matches_to_show:
            break

        if i + 1 < len(matches) and (
            matches[i + 1].scheduled_time - match.scheduled_time
        ) > timedelta(minutes=field.MAX_MATCH_GAP_MIN):
            break

    return MatchLoadResponse(
        upcoming_matches=upcoming_matches,
        red_off_field_teams_by_match=red_off_field_teams_by_match,
        blue_off_field_teams_by_match=blue_off_field_teams_by_match,
    )


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        _ = await register_display(websocket)
    except ValueError as e:
        await websocket.send_text(str(e))
        await websocket.close()
        return

    # State updates are handled by main /ws/arena WebSocket
    # This endpoint just maintains the display connection
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        pass
