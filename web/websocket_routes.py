from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket, request: Request):
    """
    WebSocket endpoint for real-time Arena state updates.
    Clients connect here to receive live match updates, scores, etc.
    Subscribes to all message types.
    """
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket)  # 不指定類型 = 接收所有訊息
    
    try:
        # Keep the connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            logger.debug(f"Received from WebSocket: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/displays/audience")
async def websocket_audience_display(websocket: WebSocket, request: Request):
    """WebSocket for audience display - subscribes to audience-specific updates."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, [
        'audience_display_mode',
        'match_time',
        'match_load',
        'realtime_score',
        'score_posted',
        'play_sound',
        'lower_third',
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Audience display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/displays/alliance_station")
async def websocket_alliance_station_display(websocket: WebSocket, request: Request):
    """WebSocket for alliance station display."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, [
        'alliance_station_display_mode',
        'match_load',
        'match_time',
        'realtime_score',
        'scoring_status',
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Alliance station display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/displays/ranking")
async def websocket_ranking_display(websocket: WebSocket, request: Request):
    """WebSocket for rankings display."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, [
        'rankings',
        'lower_third',
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Ranking display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/match_control")
async def websocket_match_control(websocket: WebSocket, request: Request):
    """WebSocket for match control panel."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, [
        'arena_status',
        'match_load',
        'match_time',
        'realtime_score',
        'scoring_status',
        'event_status',
        'audience_display_mode',
        'alliance_station_display_mode',
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Match control WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/displays")
async def websocket_setup_displays(websocket: WebSocket, request: Request):
    """WebSocket for display configuration setup - handles commands and broadcasts updates."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, ['display_configuration'])
    
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            
            message_type = data['type']
            from web import arena_commands
            
            if message_type == 'configure_display':
                display_config = data['data']
                arena_commands.update_display(display_config)
            elif message_type == 'reload_display':
                display_id = data['data']
                arena_commands.reload_displays(display_id)
            elif message_type == 'reload_all_displays':
                arena_commands.reload_displays()
            else:
                await websocket.send_json({
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup displays WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/field_testing")
async def websocket_setup_field_testing(websocket: WebSocket, request: Request):
    """WebSocket for field testing - handles sound test commands."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            
            message_type = data['type']
            from web import arena_commands
            
            if message_type == 'play_sound':
                sound_name = data['data']
                arena_commands.play_sound(sound_name)
            else:
                await websocket.send_json({
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup field testing WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/lower_thirds")
async def websocket_setup_lower_thirds(websocket: WebSocket, request: Request):
    """WebSocket for lower thirds setup - handles commands and broadcasts updates."""
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, ['audience_display_mode', 'lower_third'])
    
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            
            message_type = data['type']
            from web import arena_commands
            
            if message_type == 'save_lower_third':
                lower_third = data['data']
                arena_commands.save_lower_third(lower_third)
            elif message_type == 'delete_lower_third':
                lower_third = data['data']
                arena_commands.delete_lower_third(lower_third['id'])
            elif message_type == 'show_lower_third':
                lower_third = data['data']
                arena_commands.show_lower_third(lower_third['id'])
            elif message_type == 'hide_lower_third':
                arena_commands.hide_lower_third()
            elif message_type == 'reorder_lower_third':
                reorder_data = data['data']
                arena_commands.reorder_lower_third(reorder_data['id'], reorder_data['move_up'])
            elif message_type == 'set_audience_display':
                mode = data['data']
                arena_commands.set_audience_display(mode)
            else:
                await websocket.send_json({
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup lower thirds WebSocket error: {e}")
        ws_manager.disconnect(websocket)
