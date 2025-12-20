import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import field
import game
import models
import ws
from web import arena_state, arena_commands

router = APIRouter(prefix='/panels/referee', tags=['panels'])


class FoulListResponse(BaseModel):
    match: models.Match
    red_fouls: list[game.Foul]
    blue_fouls: list[game.Foul]
    rules: dict[int, game.Rule]


@router.get('/foul_list')
async def get_foul_list() -> FoulListResponse:
    current_match_id = arena_state.get_match_id()
    current_match = models.read_match_by_id(current_match_id) if current_match_id else models.Match()
    
    # Get fouls from cached state
    red_score = arena_state.get_red_score()
    blue_score = arena_state.get_blue_score()
    
    return FoulListResponse(
        match=current_match,
        red_fouls=red_score.get('fouls', []) if red_score else [],
        blue_fouls=blue_score.get('fouls', []) if blue_score else [],
        rules=game.get_all_rules(),
    )


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # State updates handled by main /ws/arena WebSocket
    # This WebSocket handles referee panel commands
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'add_foul':
                alliance = data['data'].get('alliance')
                is_major = data['data'].get('is_major')
                
                # Send foul command via IPC
                arena_commands.add_foul(alliance, is_major)

            elif message_type in [
                'toggle_foul_type',
                'update_foul_team',
                'update_foul_rule',
                'delete_foul',
            ]:
                alliance = data['data'].get('alliance')
                index = data['data'].get('index')
                team_id = data['data'].get('team_id', 0)
                rule_id = data['data'].get('rule_id', 0)
                
                # Send foul update command via IPC
                arena_commands.update_foul(
                    alliance=alliance,
                    command=message_type,
                    index=index,
                    team_id=team_id,
                    rule_id=rule_id
                )

            elif message_type == 'card':
                alliance = data['data'].get('alliance')
                team_id = data['data'].get('team_id')
                card = data['data'].get('card')
                
                # Send card command via IPC
                arena_commands.assign_card(alliance, team_id, card)

            elif message_type == 'signal_reset':
                # Check if in POST_MATCH state
                match_state = arena_state.get_match_state()
                if match_state != field.MatchState.POST_MATCH:
                    continue
                
                # Send signal reset command
                arena_commands.signal_reset()

            elif message_type == 'commit_match':
                # Check if in POST_MATCH state
                match_state = arena_state.get_match_state()
                if match_state != field.MatchState.POST_MATCH:
                    continue
                
                # Send commit fouls command via IPC
                arena_commands.commit_fouls()

            else:
                await websocket.send_json(
                    {
                        'type': 'error',
                        'data': {'message': f'Invalid message type{message_type}'},
                    }
                )

    except WebSocketDisconnect:
        pass
    finally:
        pass
