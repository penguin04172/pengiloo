import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import ws
from field import DisplayConfiguration, DisplayType, display_type_names
from web import arena_commands

router = APIRouter(prefix='/setup/displays', tags=['displays'])


@router.get('')
async def get_display_type() -> dict[DisplayType, str]:
    return display_type_names


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'configure_display':
                id = data['data']['id']
                type = data['data']['type']
                nickname = data['data']['nickname']
                configuration = data['data']['configuration']
                
                display_config = {
                    'id': id,
                    'type': type,
                    'nickname': nickname,
                    'configuration': configuration
                }
                arena_commands.update_display(display_config)

            elif message_type == 'reload_display':
                display_id = data['data']['display_id']
                arena_commands.reload_displays(display_id)

            elif message_type == 'reload_all_displays':
                arena_commands.reload_displays()

            else:
                await websocket.send_json(
                    {'type': 'error', 'data': {'message': f'Invalid data type{message_type}'}}
                )
                continue

    except WebSocketDisconnect:
        pass
    finally:
        pass
