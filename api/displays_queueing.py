import asyncio
from datetime import timedelta

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import field
import models
import ws

from .arena import api_arena
from .display_util import enforce_display_configuration, register_display

NUM_NON_PLAYOFF_MATCHES_TO_SHOW = 5
NUM_PLAYOFF_MATCHES_TO_SHOW = 4

router = APIRouter(prefix='/displays/queueing', tags=['displays'])


@router.get('/')
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
    matches = models.read_matches_by_type(api_arena.current_match.type, False)

    num_matches_to_show = NUM_NON_PLAYOFF_MATCHES_TO_SHOW
    if api_arena.current_match.type == models.MatchType.PLAYOFF:
        num_matches_to_show = NUM_PLAYOFF_MATCHES_TO_SHOW

    upcoming_matches = list[models.Match]()
    red_off_field_teams_by_match = list[list[int]]()
    blue_off_field_teams_by_match = list[list[int]]()
    for i, match in enumerate(matches):
        if match.is_complete() or api_arena.current_match.type_order > match.type_order:
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
        display = await register_display(websocket)
    except ValueError as e:
        await websocket.send_text(str(e))
        await websocket.close()
        return

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(
            websocket,
            display.notifier,
            api_arena.match_timing_notifier,
            api_arena.match_load_notifier,
            api_arena.match_time_notifier,
            api_arena.event_status_notifier,
            api_arena.reload_displays_notifier,
        )
    )

    try:
        await asyncio.wait([notifiers_task], return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass

        await api_arena.mark_display_disconnect(display.display_configuration.id)
        await websocket.close()
