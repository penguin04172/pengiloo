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
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Match control WebSocket error: {e}")
        ws_manager.disconnect(websocket)
