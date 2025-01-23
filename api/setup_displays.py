import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import ws
from field import DisplayConfiguration, DisplayType, display_type_names

from .arena import api_arena

router = APIRouter(prefix='/setup/displays', tags=['displays'])


@router.get('/')
async def get_display_type() -> dict[DisplayType, str]:
    return display_type_names


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(websocket, api_arena.display_configuration_notifier)
    )

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
                api_arena.update_display(
                    DisplayConfiguration(
                        id=id, type=type, nickname=nickname, configuration=configuration
                    )
                )
            elif message_type == 'reload_display':
                display_id = data['data']
                api_arena.reload_displays_notifier.notify_with_message(display_id)

            elif message_type == 'reload_all_displays':
                api_arena.reload_displays_notifier.notify()

            else:
                await websocket.send_json(
                    {'type': 'error', 'message': f'Invalid message type{message_type}'}
                )
                continue

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass
        await websocket.close()
