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


class UbusPayload(BaseModel):
    jsonrpc: str = '2.0'
    id: int = 1
    method: str = 'call'
    params: list


class UbusClient:
    def __init__(self, host='', username='root', password='', timeout=1):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.base_url = f'http://{self.host}/ubus'
        self.timeout = timeout

    async def login(self):
        """登入 OpenWrt 並獲取 session ID"""
        payload = UbusPayload(
            params=[
                config.DEFAULT_SESSION_ID,
                *config.UBUS_METHODS['LOGIN'],
                {'username': self.username, 'password': self.password},
            ],
        ).model_dump()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, timeout=self.timeout) as resp:
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

        payload = UbusPayload(params=[self.session_id, object_name, method, params]).model_dump()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, timeout=self.timeout) as resp:
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

    async def get_wifi_info(self, station='wlan0') -> dict:
        """查詢無線網路設定"""
        data = await self.call(*config.UBUS_METHODS['WIFI_INFO'](station))
        return data['result'][1]

    async def get_wifi_assoclist(self, station='wlan0') -> list:
        """查詢無線網路連線列表"""
        data = await self.call(*config.UBUS_METHODS['WIFI_ASSOCLIST'](station))
        return data['result'][1]['results']

    async def get_wifi_clients(self, station='wlan0') -> dict:
        """查詢無線網路客戶端列表"""
        data = await self.call(*config.UBUS_METHODS['WIFI_CLIENTS'](station))
        return data['result'][1]['clients']

    async def set_wifi_channel(self, channel: int, radio=0):
        """設定無線網路頻道"""

        async with aiohttp.ClientSession() as session:
            payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['WIFI_CHANNEL'](radio, channel)]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

            payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['UCI_COMMIT']('wireless')]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

            payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['RECONE_WIFI']]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

    async def set_wifi_ssid_and_password(self, channel: int, teams: list[dict]):
        async with aiohttp.ClientSession() as session:
            channel_payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['WIFI_CHANNEL'](channel)]
            ).model_dump()
            await session.post(self.base_url, json=channel_payload, timeout=self.timeout)

            for index, team in enumerate(teams):
                setup_payload = UbusPayload(
                    params=[
                        self.session_id,
                        *config.UBUS_METHODS['UCI_SET'](
                            'wireless',
                            f'@wifi-iface[{index+1}]',
                            {
                                'disabled': '0',
                                'ssid': team['id'] or f'no-team-{index+1}',
                                'key': team['wpakey'] or f'no-team-{index+1}',
                                'sae': team['wpakey'] or f'no-team-{index+1}',
                            },
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=setup_payload, timeout=self.timeout)

            # 提交變更
            commit_payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['UCI_COMMIT_WIFI']]
            )
            await session.post(self.base_url, json=commit_payload, timeout=self.timeout)

            # 重新啟動 Wi-Fi
            reload_payload = UbusPayload(
                params=[self.session_id, *config.UBUS_METHODS['RECONF_WIFI']]
            )
            await session.post(self.base_url, json=reload_payload, timeout=self.timeout)
