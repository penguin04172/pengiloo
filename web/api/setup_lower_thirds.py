import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import models
import ws
from web.arena import get_arena

router = APIRouter(prefix='/setup/lower_thirds', tags=['lower_thirds'])


@router.get('')
async def get_lower_thirds() -> list[models.LowerThird]:
    lower_thirds = models.read_all_lower_thirds()
    return lower_thirds


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(websocket, get_arena().audience_display_mode_notifier)
    )

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'update_lower_third':
                lower_third = models.LowerThird(**data['data'])
                save_lower_third(lower_third)

            elif message_type == 'delete_lower_third':
                lower_third = models.LowerThird(**data['data'])
                models.delete_lower_third(lower_third.id)

            elif message_type == 'show_lower_third':
                lower_third = models.LowerThird(**data['data'])
                save_lower_third(lower_third)
                get_arena().lower_third = lower_third
                get_arena().show_lower_third = True
                await get_arena().lower_third_notifier.notify()
                continue

            elif message_type == 'hide_lower_third':
                lower_third = models.LowerThird(**data['data'])
                save_lower_third(lower_third)
                get_arena().show_lower_third = False
                await get_arena().lower_third_notifier.notify()
                continue

            elif message_type == 'reorder_lower_thirds':
                id = data['data']['id']
                move_up = data['data']['move_up']

                try:
                    reorder_lower_third(id, move_up)
                except ValueError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif message_type == 'set_audience_display':
                mode = str(data['data'])
                await get_arena().set_audience_display_mode(mode)

            else:
                await websocket.send_json(
                    {'type': 'error', 'data': {'message': f'Invalid data type{message_type}'}}
                )
                continue

            await ws.write_notifier(websocket, get_arena().reload_displays_notifier)

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass


def save_lower_third(lower_third: models.LowerThird):
    old_lower_third = models.read_lower_third_by_id(lower_third.id)
    if old_lower_third is None:
        lower_third.id = models.read_next_lower_third_display_order()
        models.create_lower_third(lower_third)
    else:
        old_lower_third.top_text = lower_third.top_text
        old_lower_third.bottom_text = lower_third.bottom_text
        models.update_lower_third(lower_third)


def reorder_lower_third(id: int, move_up: bool):
    lower_third = models.read_lower_third_by_id(id)
    if lower_third is None:
        raise ValueError('Lower third not found')

    lower_third_list = models.read_all_lower_thirds()
    index = lower_third_list.index(lower_third)

    if move_up:
        index -= 1
    else:
        index += 1

    if index < 0 or index >= len(lower_third_list):
        raise ValueError('Index out of range')

    adjacent_lower_third = lower_third_list[index]
    lower_third.display_order, adjacent_lower_third.display_order = (
        adjacent_lower_third.display_order,
        lower_third.display_order,
    )

    models.update_lower_third(lower_third)
    models.update_lower_third(adjacent_lower_third)
