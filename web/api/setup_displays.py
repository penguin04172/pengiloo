import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import ws
from field import DisplayConfiguration, DisplayType, display_type_names
from web import arena_commands

router = APIRouter(prefix='/setup/displays', tags=['displays'])


@router.get('')
async def get_display_type() -> dict[DisplayType, str]:
    return display_type_names
