import logging
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket

NOTIFY_QUEUE_SIZE = 5


class Notifier:
    """Notifier class."""

    listeners: set[WebSocket]
    message_type: str
    message_producer: Callable[..., Any] | None

    def __init__(self, message_type: str, message_producer: Callable[..., Any] | None = None):
        """Create a new Notifier instance.

        Args:
            message_type (str): _description_
            message_producer (Callable[..., Any] | None, optional): _description_. Defaults to None.
        """
        self.listeners = set()
        self.message_type = message_type
        self.message_producer = message_producer

    class MessageEnvelope:
        """Message envelope class."""

        type: str
        payload: Any

        def __init__(self, type: str, payload: Any):
            self.type = type
            self.payload = payload

    async def connect(self, websocket: WebSocket):
        """Connect a new listener.

        Args:
            websocket (WebSocket): _description_
        """
        await websocket.accept()
        self.listeners.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Disconnect a listener.

        Args:
            websocket (WebSocket): _description_
        """
        self.listeners.remove(websocket)

    async def notify(self):
        """Notify all listeners with a message."""
        message_body = self.message_producer() if self.message_producer else None
        await self.notify_with_message(message_body)

    async def notify_with_message(self, message: Any):
        """Notify all listeners with a message.

        Args:
            message (Any): _description_
        """
        message = self.MessageEnvelope(type=self.message_type, payload=message)
        for listener in self.listeners:
            await self.notify_listener(listener, message)

    async def notify_listener(self, listener: WebSocket, message: MessageEnvelope):
        """Notify a single listener with a message.

        Args:
            listener (WebSocket): _description_
            message (MessageEnvelope): _description_
        """
        try:
            await listener.send_json(vars(message))
        except Exception as e:
            logging.warning(f'Failed to send message to listener: {e}')
            self.listeners.remove(listener)
