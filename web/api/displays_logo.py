import asyncio
import logging

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/logo', tags=['displays'])


@router.get('')
async def logo_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(request, display_id, nickname, {'message': ''})
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        display = await register_display(websocket)
    except ValueError as e:
        logging.error(f'Error registering display: {e}')
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
