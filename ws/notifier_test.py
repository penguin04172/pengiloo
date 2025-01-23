import logging
import unittest
from unittest.mock import AsyncMock, Mock

from fastapi import WebSocket

from .notifier import Notifier


class TestNotifier(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        logger = logging.getLogger()
        logger.propagate = False

    async def test_connect(self):
        notifier = Notifier(message_type='test', message_producer=self.message_generator)
        websocket = AsyncMock(spec=WebSocket)
        await notifier.connect(websocket)
        websocket.accept.assert_called_once()
        self.assertIn(websocket, notifier.listeners)

    def test_disconnect(self):
        notifier = Notifier(message_type='test', message_producer=self.message_generator)
        websocket = Mock(spec=WebSocket)
        notifier.listeners.add(websocket)
        notifier.disconnect(websocket)
        self.assertNotIn(websocket, notifier.listeners)

    async def test_notifier(self):
        notifier = Notifier(message_type='test', message_producer=self.message_generator)
        await notifier.notify()
        await notifier.notify_with_message(12345)
        await notifier.notify_with_message({})

        websocket = AsyncMock(spec=WebSocket)
        await notifier.connect(websocket)

        await notifier.notify()
        websocket.send_json.assert_called_with({'type': 'test', 'payload': 'test_message'})

        await notifier.notify_with_message(12345)
        websocket.send_json.assert_called_with({'type': 'test', 'payload': 12345})

        await notifier.notify_with_message('message1')
        await notifier.notify_with_message('message2')
        await notifier.notify()
        websocket.send_json.assert_any_call({'type': 'test', 'payload': 'message1'})
        websocket.send_json.assert_any_call({'type': 'test', 'payload': 'message2'})
        websocket.send_json.assert_any_call({'type': 'test', 'payload': 'test_message'})

    async def test_multiple_listeners(self):
        notifier = Notifier(message_type='test2', message_producer=None)
        listeners = [AsyncMock(spec=WebSocket) for _ in range(50)]
        for listener in listeners:
            await notifier.connect(listener)

        await notifier.notify()
        await notifier.notify_with_message('test_message')

        for listener in listeners:
            listener.send_json.assert_any_call({'type': 'test2', 'payload': None})
            listener.send_json.assert_any_call({'type': 'test2', 'payload': 'test_message'})

        notifier.disconnect(listeners[4])
        listeners[4].send_json.reset_mock()
        self.assertEqual(len(notifier.listeners), 49)

        await notifier.notify_with_message('test_message2')
        listeners[4].send_json.assert_not_called()
        for listener in notifier.listeners:
            listener.send_json.assert_any_call({'type': 'test2', 'payload': 'test_message2'})

        notifier.disconnect(listeners[16])
        listeners[16].send_json.reset_mock()
        notifier.disconnect(listeners[31])
        listeners[31].send_json.reset_mock()
        notifier.disconnect(listeners[47])
        listeners[47].send_json.reset_mock()
        self.assertEqual(len(notifier.listeners), 46)

        await notifier.notify_with_message('test_message3')
        listeners[16].send_json.assert_not_called()
        listeners[31].send_json.assert_not_called()
        listeners[47].send_json.assert_not_called()
        for listener in notifier.listeners:
            listener.send_json.assert_any_call({'type': 'test2', 'payload': 'test_message3'})

    def message_generator(self):
        return 'test_message'
