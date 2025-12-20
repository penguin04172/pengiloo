import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/wall', tags=['displays'])


@router.get('')
async def placeholder_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(
        request,
        display_id,
        nickname,
        {'background': '#000', 'reversed': 'false', 'top_spacing_px': '0', 'zoom_factor': '1'},
    )
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

    # State updates are handled by main /ws/arena WebSocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        pass
