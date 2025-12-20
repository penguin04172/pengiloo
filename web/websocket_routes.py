from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from datetime import datetime
from typing import Any
from web.state_manager import get_state_manager

logger = logging.getLogger(__name__)
router = APIRouter()


def json_serializer(obj: Any) -> str:
    """Custom JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def send_json_safe(websocket: WebSocket, data: dict):
    """Send JSON with custom serializer for datetime objects."""
    json_str = json.dumps(data, default=json_serializer)
    await websocket.send_text(json_str)


@router.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Arena state updates.
    Clients connect here to receive live match updates, scores, etc.
    Subscribes to all message types.
    """
    ws_manager = websocket.app.state.ws_manager
    await ws_manager.connect(websocket)  # 不�?定�???= ?�收?�?��???
    
    # Send initial state after connection
    state_manager = get_state_manager()
    all_state = state_manager.get_all_state()
    for message_type, data in all_state.items():
        try:
            await send_json_safe(websocket, {'type': message_type, 'data': data})
        except Exception as e:
            logger.error(f"Error sending initial state {message_type}: {e}")
    
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
async def websocket_audience_display(websocket: WebSocket):
    """WebSocket for audience display - subscribes to audience-specific updates."""
    ws_manager = websocket.app.state.ws_manager
    subscribed_types = [
        'audience_display_mode',
        'match_time',
        'match_load',
        'realtime_score',
        'score_posted',
        'play_sound',
        'lower_third',
    ]
    await ws_manager.connect(websocket, subscribed_types)
    
    # Send initial state for subscribed types
    state_manager = get_state_manager()
    for message_type in subscribed_types:
        data = state_manager.get_state(message_type)
        if data is not None:
            try:
                await send_json_safe(websocket, {'type': message_type, 'data': data})
            except Exception as e:
                logger.error(f"Error sending initial state {message_type}: {e}")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Audience display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/displays/alliance_station")
async def websocket_alliance_station_display(websocket: WebSocket):
    """WebSocket for alliance station display."""
    ws_manager = websocket.app.state.ws_manager
    subscribed_types = [
        'alliance_station_display_mode',
        'match_load',
        'match_time',
        'realtime_score',
        'scoring_status',
    ]
    await ws_manager.connect(websocket, subscribed_types)
    
    # Send initial state for subscribed types
    state_manager = get_state_manager()
    for message_type in subscribed_types:
        data = state_manager.get_state(message_type)
        if data is not None:
            try:
                await send_json_safe(websocket, {'type': message_type, 'data': data})
            except Exception as e:
                logger.error(f"Error sending initial state {message_type}: {e}")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Alliance station display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/displays/ranking")
async def websocket_ranking_display(websocket: WebSocket):
    """WebSocket for rankings display."""
    ws_manager = websocket.app.state.ws_manager
    subscribed_types = [
        'rankings',
        'lower_third',
    ]
    await ws_manager.connect(websocket, subscribed_types)
    
    # Send initial state for subscribed types
    state_manager = get_state_manager()
    for message_type in subscribed_types:
        data = state_manager.get_state(message_type)
        if data is not None:
            try:
                await send_json_safe(websocket, {'type': message_type, 'data': data})
            except Exception as e:
                logger.error(f"Error sending initial state {message_type}: {e}")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Ranking display WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/match_control")
async def websocket_match_control(websocket: WebSocket):
    """WebSocket for match control panel."""
    ws_manager = websocket.app.state.ws_manager
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
    
    # Send initial state after connection
    state_manager = get_state_manager()
    all_state = state_manager.get_all_state()
    for message_type, data in all_state.items():
        try:
            await send_json_safe(websocket, {'type': message_type, 'data': data})
        except Exception as e:
            logger.error(f"Error sending initial state {message_type}: {e}")
    
    try:
        while True:
            message = await websocket.receive_text()
            # Parse and handle incoming commands
            try:
                data = json.loads(message)
                if 'type' not in data:
                    continue
                
                command_type = data['type']
                command_data = data.get('data', {})
                
                from web import arena_commands
                
                # Handle match control commands
                if command_type == 'load_match':
                    match_id = command_data.get('match_id', 0)
                    if match_id == 0:
                        arena_commands.load_test_match()
                    else:
                        arena_commands.load_match(match_id)
                elif command_type == 'show_result':
                    arena_commands.show_result(command_data.get('match_id'))
                elif command_type == 'substitute_teams':
                    arena_commands.substitute_teams(command_data)
                elif command_type == 'toggle_bypass':
                    arena_commands.toggle_bypass(command_data.get('station'))
                elif command_type == 'start_match':
                    arena_commands.start_match()
                elif command_type == 'abort_match':
                    arena_commands.abort_match()
                elif command_type == 'signal_reset':
                    arena_commands.signal_reset()
                elif command_type == 'commit_results':
                    arena_commands.commit_results()
                elif command_type == 'discard_results':
                    arena_commands.discard_results()
                elif command_type == 'set_audience_display':
                    arena_commands.set_audience_display(command_data)
                elif command_type == 'set_alliance_station_display':
                    arena_commands.set_alliance_station_display(command_data)
                elif command_type == 'start_timeout':
                    arena_commands.start_timeout(command_data.get('duration_sec'))
                elif command_type == 'set_test_match_name':
                    arena_commands.set_test_match_name(command_data.get('name'))
                else:
                    logger.warning(f"Unknown command type: {command_type}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Match control WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/displays")
async def websocket_setup_displays(websocket: WebSocket):
    """WebSocket for display configuration setup - handles commands and broadcasts updates."""
    ws_manager = websocket.app.state.ws_manager
    subscribed_types = ['display_configuration']
    await ws_manager.connect(websocket, subscribed_types)
    
    # Send initial state for subscribed types
    state_manager = get_state_manager()
    for message_type in subscribed_types:
        data = state_manager.get_state(message_type)
        if data is not None:
            try:
                await send_json_safe(websocket, {'type': message_type, 'data': data})
            except Exception as e:
                logger.error(f"Error sending initial state {message_type}: {e}")
    
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
                await send_json_safe(websocket, {
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup displays WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/field_testing")
async def websocket_setup_field_testing(websocket: WebSocket):
    """WebSocket for field testing - handles sound test commands."""
    ws_manager = websocket.app.state.ws_manager
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
                await send_json_safe(websocket, {
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup field testing WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/setup/lower_thirds")
async def websocket_setup_lower_thirds(websocket: WebSocket):
    """WebSocket for lower thirds setup - handles commands and broadcasts updates."""
    ws_manager = websocket.app.state.ws_manager
    subscribed_types = ['audience_display_mode', 'lower_third']
    await ws_manager.connect(websocket, subscribed_types)
    
    # Send initial state for subscribed types
    state_manager = get_state_manager()
    for message_type in subscribed_types:
        data = state_manager.get_state(message_type)
        if data is not None:
            try:
                await send_json_safe(websocket, {'type': message_type, 'data': data})
            except Exception as e:
                logger.error(f"Error sending initial state {message_type}: {e}")
    
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
                await send_json_safe(websocket, {
                    'type': 'error',
                    'data': {'message': f'Invalid message type: {message_type}'}
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Setup lower thirds WebSocket error: {e}")
        ws_manager.disconnect(websocket)

