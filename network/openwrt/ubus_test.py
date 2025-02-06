import unittest

from .exceptions import UbusUnauthorizedError
from .ubus import OpenWrtUbusClient


class TestOpenWrtUbusClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = OpenWrtUbusClient(host='192.168.1.1', username='root', password='')

    async def test_login(self):
        await self.client.login()
        self.assertIsNotNone(self.client.session_id)

    async def test_call(self):
        await self.client.login()
        await self.client.call('system', 'board')
        await self.client.call('network.interface.lan', 'status')

    async def test_exceptions(self):
        with self.assertRaises(UbusUnauthorizedError):
            await self.client.get_system_info()

        with self.assertRaises(UbusUnauthorizedError):
            await self.client.get_network_status()
