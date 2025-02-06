import asyncio

import aiohttp
from pydantic import BaseModel

from . import config
from .exceptions import (
    UbusLoginError,
    UbusRequestError,
    UbusTimeoutError,
    UbusUnauthorizedError,
)


class OpenWrtUbusPayload(BaseModel):
    jsonrpc: str = '2.0'
    id: int = 1
    method: str
    params: list


class OpenWrtUbusClient:
    def __init__(self, host='', username='', password=''):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.base_url = f'http://{self.host}/ubus'

    async def login(self):
        """登入 OpenWrt 並獲取 session ID"""
        payload = OpenWrtUbusPayload(
            method='call',
            params=[
                config.DEFAULT_SESSION_ID,
                *config.UBUS_METHODS['LOGIN'],
                {'username': self.username, 'password': self.password},
            ],
        ).model_dump()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, json=payload, timeout=config.TIMEOUT
                ) as resp:
                    data = await resp.json()

                    if 'result' in data and data['result'][0] == 0:
                        self.session_id = data['result'][1]['ubus_rpc_session']
                    else:
                        raise UbusLoginError('Login Failed')
        except asyncio.TimeoutError:  # noqa
            raise UbusTimeoutError('UBUS Login Timeout') from None
        except aiohttp.ClientError as e:
            raise UbusRequestError(f'Connection Error: {e}') from e

    async def call(self, object_name, method, params: dict = None):
        """發送 ubus API 請求"""
        if params is None:
            params = {}

        if not self.session_id:
            raise UbusUnauthorizedError()

        payload = OpenWrtUbusPayload(
            method='call', params=[self.session_id, object_name, method, params]
        ).model_dump()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, json=payload, timeout=config.TIMEOUT
                ) as resp:
                    if resp.status == 401:
                        raise UbusUnauthorizedError()
                    elif resp.status >= 400:
                        raise UbusRequestError(f'API Error, Status: {resp.status}')

                    data = await resp.json()

                    if 'result' in data and data['result'][0] != 0:
                        error_code = data['result'][0]
                        raise UbusRequestError(f'UBUS API Returned Error: {error_code}')

                    return data
        except asyncio.TimeoutError:  # noqa
            raise UbusTimeoutError('UBUS API Request Timeout') from None
        except aiohttp.ClientError as e:
            raise UbusRequestError(f'Client Error: {e}') from e

    async def get_system_info(self):
        """查詢 OpenWrt 系統資訊"""
        return await self.call(*config.UBUS_METHODS['SYSTEM_INFO'])

    async def get_network_status(self, interface='lan'):
        """查詢網路介面狀態"""
        return await self.call(*config.UBUS_METHODS['NETWORK_STATUS'](interface))
