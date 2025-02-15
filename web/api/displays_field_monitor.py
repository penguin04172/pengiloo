import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws
from web.arena import get_arena

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/field_monitor', tags=['displays'])


@router.get('')
async def field_monitor_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(request, display_id, nickname)
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}


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
