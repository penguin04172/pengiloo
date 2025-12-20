from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from game.match_sounds import get_sounds_list
from web import arena_commands

router = APIRouter(prefix='/setup/field_testing', tags=['field_testing'])


class MatchSound(BaseModel):
    name: str
    file_extension: str


@router.get('')
async def get_field_testing() -> list[MatchSound]:
    return [MatchSound(**sound) for sound in get_sounds_list()]

