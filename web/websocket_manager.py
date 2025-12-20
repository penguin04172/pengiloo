import asyncio
import logging
from typing import Set, Dict, List
from fastapi import WebSocket

from web.state_manager import get_state_manager

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts state updates from Arena."""
    
    def __init__(self, ipc):
        self.ipc = ipc
        # 所有連接
        self.active_connections: Set[WebSocket] = set()
        # 按訊息類型訂閱的連接 {message_type: set of websockets}
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        self.running = False
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, message_types: List[str] = None):
        """Add a new WebSocket connection and optionally subscribe to message types.
        
        Args:
            websocket: WebSocket connection to add
            message_types: List of message types to subscribe to. If None, subscribes to all.
        """
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)
            
            # 如果指定了訊息類型，加入訂閱
            if message_types:
                for msg_type in message_types:
                    if msg_type not in self.subscriptions:
                        self.subscriptions[msg_type] = set()
                    self.subscriptions[msg_type].add(websocket)
            
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        if message_types:
            logger.debug(f"Subscribed to: {message_types}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from all subscriptions."""
        self.active_connections.discard(websocket)
        
        # 從所有訂閱中移除
        for msg_type in self.subscriptions:
            self.subscriptions[msg_type].discard(websocket)
            
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
    
    async def broadcast_to_type(self, message_type: str, data: dict):
        """Broadcast a message to clients subscribed to a specific message type.
        
        Args:
            message_type: Type of message (e.g., 'match_time', 'realtime_score')
            data: Message data to send
        """
        message = {'type': message_type, 'data': data}
        
        # 如果沒有該類型的訂閱者，廣播給所有連接
        subscribers = self.subscriptions.get(message_type, self.active_connections)
        
        if not subscribers:
            return
        
        disconnected = set()
        for connection in subscribers:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending {message_type} to WebSocket: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_display(self, display_id: str, message_type: str, data: dict):
        """Send a message to a specific display.
        
        Args:
            display_id: Display identifier (e.g., 'audience', 'alliance_station')
            message_type: Type of message
            data: Message data
        """
        message = {
            'type': message_type,
            'display': display_id,
            'data': data
        }
        await self.broadcast(message)

    async def listen_for_state_updates(self):
        """Listen for state updates from Arena process via IPC and broadcast to WebSocket clients."""
        self.running = True
        logger.info("Starting WebSocket state listener...")
        state_manager = get_state_manager()
        
        while self.running:
            try:
                state_update = self.ipc.get_state_update()
                if state_update:
                    # state_update 格式: {'type': 'message_type', 'data': {...}}
                    message_type = state_update.get('type', 'unknown')
                    data = state_update.get('data', {})
                    
                    # Update state cache for Web process
                    state_manager.update_state({message_type: data})
                    
                    # Broadcast to subscribed WebSocket clients
                    await self.broadcast_to_type(message_type, data)
                else:
                    # No update, sleep briefly to avoid busy-waiting
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")
                await asyncio.sleep(0.1)

    def stop(self):
        """Stop the state listener."""
        self.running = False

