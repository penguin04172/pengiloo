import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

NOTIFY_QUEUE_SIZE = 5


class Notifier:
    """Notifier class."""

    listeners: list[WebSocket]
    message_type: str
    message_producer: Callable[..., Any] | None

    def __init__(self, message_type: str, message_producer: Callable[..., Any] | None = None):
        """Create a new Notifier instance.

        Args:
            message_type (str): _description_
            message_producer (Callable[..., Any] | None, optional): _description_. Defaults to None.
        """
        self.listeners = []
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
            self.listeners.append(websocket)

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
        except (WebSocketDisconnect, asyncio.CancelledError):
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
    try:
        async with asyncio.TaskGroup() as tg:
            for notifier in notifiers:
                await notifier.connect(websocket)
                tg.create_task(notifier.listen(websocket))

                if notifier.message_producer is not None:
                    await write_notifier(websocket, notifier)

            async def heartbeat():
                while True:
                    try:
                        await asyncio.sleep(10)
                        await websocket.send_json({'type': 'ping', 'data': {}})
                    except WebSocketDisconnect:
                        tg.cancel()
                        return  # 這樣外部可以捕捉到 WebSocketDisconnect
                    except RuntimeError:
                        return  # 避免 asyncio 被關閉時出錯

            tg.create_task(heartbeat())

    except (WebSocketDisconnect, asyncio.CancelledError):
        pass

    finally:
        # 確保所有 notifier 也都會斷線
        for notifier in notifiers:
            if websocket in notifier.listeners:
                await notifier.disconnect(websocket)


async def write_notifier(websocket: WebSocket, notifier: Notifier):
    await websocket.send_json(
        vars(notifier.MessageEnvelope(type=notifier.message_type, data=notifier.get_message_body()))
    )
