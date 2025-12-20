import asyncio

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

import game
from web import arena_commands, arena_state

router = APIRouter(prefix='/panels/scoring', tags=['panels'])


@router.websocket('/{alliance}/websocket')
async def scoring_panel_websocket(alliance: str, websocket: WebSocket):
    """WebSocket endpoint for scoring panel - handles high-frequency scoring updates."""
    await websocket.accept()

    if alliance not in ['red', 'blue']:
        await websocket.close(1008, 'Invalid alliance')
        return

    # Register panel with Arena via IPC
    panel_id = f"ws_{alliance}_{id(websocket)}"
    arena_commands.register_scoring_panel(alliance, panel_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            
            command = data['type']
            
            if command == 'commit_match':
                # Check match state from cached state
                match_state = arena_state.get_match_state()
                if match_state != 'POST_MATCH':
                    await websocket.send_json({
                        'type': 'error',
                        'data': {'message': 'Match not in POST_MATCH state'}
                    })
                    continue
                
                # Send commit command via IPC
                arena_commands.commit_panel_score(alliance, panel_id)
                await websocket.send_json({
                    'type': 'commit_acknowledged',
                    'data': {'alliance': alliance}
                })
            
            else:
                # All other commands are scoring updates
                payload = data.get('data', {})
                
                # Send scoring command to Arena via IPC
                arena_commands.update_scoring(
                    alliance=alliance,
                    command=command,
                    position=payload.get('position'),
                    level=payload.get('level'),
                    action=payload.get('action'),
                    state=payload.get('state')
                )
                
                # Optional: Acknowledge receipt
                # Actual score update will come via /ws/arena state broadcast
    
    except WebSocketDisconnect:
        pass
    finally:
        # Unregister panel from Arena
        arena_commands.unregister_scoring_panel(alliance, panel_id)


@router.get('/{alliance}/score')
async def get_score(alliance: str) -> dict:
    """Get current score for an alliance (for debugging/monitoring)."""
    if alliance not in ['red', 'blue']:
        raise HTTPException(status_code=400, detail='Invalid alliance')
    
    score = arena_state.get_realtime_score(alliance)
    return {'alliance': alliance, 'score': score}
