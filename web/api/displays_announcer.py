import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws
from web.arena import get_arena

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/announcer', tags=['displays'])


@router.get('')
async def announcer_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(request, display_id, nickname, None)
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}


@router.get('/match_load')
async def announcer_match_load() -> dict:
    return get_arena().generate_match_load_message()


@router.get('/score_posted')
async def announcer_score_posted() -> dict:
    return get_arena().generate_score_posted_message()


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
            get_arena().match_timing_notifier,
            get_arena().audience_display_mode_notifier,
            get_arena().event_status_notifier,
            get_arena().match_load_notifier,
            get_arena().match_time_notifier,
            get_arena().realtime_score_notifier,
            get_arena().score_posted_notifier,
            get_arena().reload_displays_notifier,
        )
    )

    try:
        await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass

        await get_arena().mark_display_disconnect(display.display_configuration.id)
