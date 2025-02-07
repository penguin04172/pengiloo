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
    def __init__(self, host='', username='root', password=''):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.base_url = f'http://{self.host}/ubus'

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

        payload = UbusPayload(params=[self.session_id, object_name, method, params]).model_dump()

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

    async def set_wifi_ssid_and_password(self, channel: int, teams: list[dict]):
        session_id = await self.login()

        async with aiohttp.ClientSession() as session:
            channel_payload = UbusPayload(
                params=[session_id, *config.UBUS_METHODS['WIFI_CHANNEL'](channel)]
            ).model_dump()
            await session.post(self.base_url, json=channel_payload)

            for index, team in enumerate(teams):
                # 啟動 WIFI
                disable_payload = UbusPayload(
                    params=[session_id, *config.UBUS_METHODS['WIFI_DISABLE'](index, 0)]
                ).model_dump()
                await session.post(self.base_url, json=disable_payload)

                # 設定 SSID
                ssid_payload = UbusPayload(
                    params=[
                        session_id,
                        *config.UBUS_METHODS['WIFI_SSID'](
                            index, team['id'] or f'no-team-{index+1}'
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=ssid_payload)

                # 設定 WPA 密碼
                wpakey_payload = UbusPayload(
                    params=[
                        session_id,
                        *config.UBUS_METHODS['WIFI_WPAPSK'](
                            index, team['wpakey'] or f'no-team-{index+1}'
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=wpakey_payload)

                # 設定 SAE
                sae_payload = UbusPayload(
                    params=[
                        session_id,
                        *config.UBUS_METHODS['WIFI_WPASAE'](
                            index, team['wpakey'] or f'no-team-{index+1}'
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=sae_payload)

            # 提交變更
            commit_payload = UbusPayload(
                params=[session_id, *config.UBUS_METHODS['UCI_COMMIT_WIFI']]
            )
            await session.post(self.base_url, json=commit_payload)

            # 重新啟動 Wi-Fi
            reload_payload = UbusPayload(
                params=[session_id, *config.UBUS_METHODS['RELOAD_NETWORK']]
            )
            await session.post(self.base_url, json=reload_payload)
