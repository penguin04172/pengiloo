import asyncio
import logging
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket

NOTIFY_QUEUE_SIZE = 5


class Notifier:
    listeners: set[WebSocket]
    message_type: str
    message_producer: Callable[..., Any] | None

    def __init__(self, message_type: str, message_producer: Callable[..., Any] | None = None):
        self.listeners = set()
        self.message_type = message_type
        self.message_producer = message_producer

    class MessageEnvelope:
        type: str
        payload: Any

        def __init__(self, type: str, payload: Any):
            self.type = type
            self.payload = payload

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.listeners.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.listeners.remove(websocket)

    async def notify(self):
        message_body = self.message_producer() if self.message_producer else None
        await self.notify_with_message(message_body)

    async def notify_with_message(self, message: Any):
        message = self.MessageEnvelope(type=self.message_type, payload=message)
        for listener in self.listeners:
            await self.notify_listener(listener, message)

    async def notify_listener(self, listener: WebSocket, message: MessageEnvelope):
        """
        非阻塞地通知單個監聽者。
        捕捉錯誤（例如連接中斷），並在失敗時從監聽列表中移除該 WebSocket。
        """
        try:
            # 非阻塞地發送訊息
            await listener.send_json(vars(message))
        except Exception as e:
            logging.warning(f'Failed to send message to listener: {e}')
            self.listeners.remove(listener)
