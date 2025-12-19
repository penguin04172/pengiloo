import asyncio
import logging
from typing import Set
from fastapi import WebSocket

from web.state_manager import get_state_manager

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts state updates from Arena."""
    
    def __init__(self, ipc):
        self.ipc = ipc
        self.active_connections: Set[WebSocket] = set()
        self.running = False

    async def connect(self, websocket: WebSocket):
        """Add a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def listen_for_state_updates(self):
        """Listen for state updates from Arena process via IPC and broadcast to WebSocket clients."""
        self.running = True
        logger.info("Starting WebSocket state listener...")
        state_manager = get_state_manager()
        
        while self.running:
            try:
                state_update = self.ipc.get_state_update()
                if state_update:
                    # Update state cache for Web process
                    state_manager.update_state(state_update)
                    # Broadcast to all WebSocket clients
                    await self.broadcast(state_update)
                else:
                    # No update, sleep briefly to avoid busy-waiting
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")
                await asyncio.sleep(0.1)

    def stop(self):
        """Stop the state listener."""
        self.running = False

