from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket, request: Request):
    """
    WebSocket endpoint for real-time Arena state updates.
    Clients connect here to receive live match updates, scores, etc.
    """
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket)
    
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
