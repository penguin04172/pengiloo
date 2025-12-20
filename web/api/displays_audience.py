import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/audience', tags=['displays'])


@router.get('')
async def audience_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(
        request,
        display_id,
        nickname,
        {'background': '#0f0', 'reversed': False, 'overlay_location': 'bottom'},
    )
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}
