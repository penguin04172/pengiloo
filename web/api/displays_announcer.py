import asyncio

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

import ws
from web import arena_state

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
    # Return match load information from cached state
    match_name = arena_state.get_match_name()
    match_type = arena_state.get_match_type()
    return {
        'match_name': match_name,
        'match_type': match_type.value if match_type else 'test',
        'state': arena_state.get_match_state().value if arena_state.get_match_state() else 'PRE_MATCH'
    }


@router.get('/score_posted')
async def announcer_score_posted() -> dict:
    # Return score posted information from cached state
    red_score = arena_state.get_red_score()
    blue_score = arena_state.get_blue_score()
    return {
        'red_score': red_score,
        'blue_score': blue_score,
        'match_name': arena_state.get_match_name()
    }


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
