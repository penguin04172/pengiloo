import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import models
import ws
from web import arena_commands

router = APIRouter(prefix='/setup/lower_thirds', tags=['lower_thirds'])


@router.get('')
async def get_lower_thirds() -> list[models.LowerThird]:
    lower_thirds = models.read_all_lower_thirds()
    return lower_thirds


def save_lower_third(lower_third: models.LowerThird):
    old_lower_third = models.read_lower_third_by_id(lower_third.id)
    if old_lower_third is None:
        lower_third.display_order = models.read_next_lower_third_display_order()
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
