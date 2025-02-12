from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import game
from web.arena import get_arena

router = APIRouter(prefix='/setup/field_testing', tags=['field_testing'])


@router.get('')
async def get_field_testing() -> list[game.MatchSound]:
    return game.get_sounds()


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'play_sound':
                sound = data['data']
                await get_arena().play_sound_notifier.notify_with_message(sound)

            else:
                await websocket.send_json(
                    {'type': 'error', 'data': {'message': f'Invalid data type{message_type}'}}
                )
                continue
    except WebSocketDisconnect:
        pass
    finally:
        pass
