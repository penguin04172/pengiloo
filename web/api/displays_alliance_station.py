import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws

from .display_util import enforce_display_configuration, register_display

router = APIRouter(prefix='/displays/alliance_station', tags=['displays'])


@router.get('')
async def alliance_station_display(request: Request, display_id: str = '', nickname='') -> dict:
    path = await enforce_display_configuration(request, display_id, nickname, {'station': 'R1'})
    if path is not None:
        return {'status': 'redirect', 'path': path}
    return {'status': 'success'}

