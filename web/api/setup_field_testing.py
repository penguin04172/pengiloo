from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import game
from web import arena_commands

router = APIRouter(prefix='/setup/field_testing', tags=['field_testing'])


@router.get('')
async def get_field_testing() -> list[game.MatchSound]:
    return game.get_sounds()

