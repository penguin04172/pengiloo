import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

NOTIFY_QUEUE_SIZE = 5


class Notifier:
    """Notifier class."""

    listeners: set[WebSocket]
    message_type: str
    message_producer: Callable[..., Any] | None
    lock: asyncio.Lock

    def __init__(self, message_type: str, message_producer: Callable[..., Any] | None = None):
        """Create a new Notifier instance.

        Args:
            message_type (str): _description_
            message_producer (Callable[..., Any] | None, optional): _description_. Defaults to None.
        """
        self.listeners = set()
        self.message_type = message_type
        self.message_producer = message_producer
        self.lock = asyncio.Lock()

    class MessageEnvelope:
        """Message envelope class."""

        type: str
        data: Any

        def __init__(self, type: str, data: Any):
            self.type = type
            self.data = data

    async def connect(self, websocket: WebSocket):
        """Connect a new listener.

        Args:
            websocket (WebSocket): _description_
        """
        async with self.lock:
            self.listeners.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a listener.

        Args:
            websocket (WebSocket): _description_
        """
        async with self.lock:
            self.listeners.remove(websocket)

    async def listen(self, websocket: WebSocket):
        """Listen for new listeners."""
        try:
            while True:
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            pass
        finally:
            await self.disconnect(websocket)

    async def notify(self):
        """Notify all listeners with a message."""
        message_body = self.get_message_body()
        await self.notify_with_message(message_body)

    async def notify_with_message(self, message: Any):
        """Notify all listeners with a message.

        Args:
            message (Any): _description_
        """
        message = self.MessageEnvelope(type=self.message_type, data=message)
        async with self.lock:
            for listener in self.listeners:
                await self.notify_listener(listener, message)

    async def notify_listener(self, listener: WebSocket, message: MessageEnvelope):
        """Notify a single listener with a message.

        Args:
            listener (WebSocket): _description_
            message (MessageEnvelope): _description_
        """
        await listener.send_json(vars(message))

    def get_message_body(self):
        """Get the message body."""
        return self.message_producer() if self.message_producer else {}


async def handle_notifiers(websocket: WebSocket, *notifiers: Notifier):
    listeners = []
    for notifier in notifiers:
        await notifier.connect(websocket)
        listeners.append(asyncio.create_task(notifier.listen(websocket)))

        if notifier.message_producer is not None:
            await write_notifier(websocket, notifier)

    async def heartbeat():
        while True:
            await asyncio.sleep(10)
            try:
                await websocket.send_json({'type': 'ping', 'data': {}})
            except WebSocketDisconnect:
                return

    listeners.append(asyncio.create_task(heartbeat()))

    done, pending = await asyncio.wait(listeners, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()

    for notifier in notifiers:
        await notifier.disconnect(websocket)


async def write_notifier(websocket: WebSocket, notifier: Notifier):
    await websocket.send_json(
        vars(notifier.MessageEnvelope(type=notifier.message_type, data=notifier.get_message_body()))
    )
