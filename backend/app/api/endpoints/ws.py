from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.core.notifier import manager
from loguru import logger

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Here we can handle incoming messages from clients (e.g. Referees)
            logger.debug(f"Client {client_id} sent: {data}")
            await manager.send_personal_message(f"Ack: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")
