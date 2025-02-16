import asyncio

import aiohttp
from pydantic import BaseModel

from . import config
from .exceptions import UbusLoginError, UbusRequestError, UbusTimeoutError, UbusUnauthorizedError


class UbusPayload(BaseModel):
    jsonrpc: str = '2.0'
    id: int = 1
    method: str = 'call'
    params: list


class UbusClient:
    def __init__(self, host='', username='root', password='', timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self._session_id = None
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
                        self._session_id = data['result'][1]['ubus_rpc_session']
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

        if not self._session_id:
            raise UbusUnauthorizedError()

        payload = UbusPayload(params=[self._session_id, object_name, method, params]).model_dump()

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
        print(data)
        return data['result'][1]['clients']

    async def set_wifi_channel(self, channel: int, radio=0):
        """設定無線網路頻道"""
        async with aiohttp.ClientSession() as session:
            payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['WIFI_CHANNEL'](radio, channel)]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

            payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['UCI_COMMIT']('wireless')]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

            payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['RECONF_WIFI']]
            ).model_dump()
            await session.post(self.base_url, json=payload, timeout=self.timeout)

    async def set_wifi_ssid_and_password(self, channel: int, teams: list[dict]):
        async with aiohttp.ClientSession() as session:
            channel_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['WIFI_CHANNEL'](2, channel)]
            ).model_dump()
            await session.post(self.base_url, json=channel_payload, timeout=self.timeout)

            for index, team in enumerate(teams):
                setup_payload = UbusPayload(
                    params=[
                        self._session_id,
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

            access_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['UCI_ACCESS']('wireless')]
            ).model_dump()
            resp = await session.post(self.base_url, json=access_payload, timeout=self.timeout)
            print(await resp.text())

            await session.post(
                f'http://{self.host}/cgi-bin/cgi-exec',
                data={'sessionid': self._session_id, 'command': '/usr/libexec/luci-peeraddr'},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=self.timeout,
            )

            await session.post(
                f'http://{self.host}/cgi-bin/luci/admin/uci/apply_unchecked',
                data={'sid': self._session_id},
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                timeout=self.timeout,
            )

            # # 提交變更
            # commit_payload = UbusPayload(
            #     params=[self._session_id, *config.UBUS_METHODS['UCI_COMMIT']('wireless')]
            # ).model_dump()
            # resp = await session.post(self.base_url, json=commit_payload, timeout=self.timeout)
            # print(await resp.text())

            # # 重新啟動 Wi-Fi
            # reload_payload = UbusPayload(
            #     params=[self._session_id, *config.UBUS_METHODS['RECONF_WIFI']]
            # ).model_dump()
            # resp = await session.post(self.base_url, json=reload_payload, timeout=self.timeout)
            # print(await resp.text())

    async def generate_ethernet_configs(self, team_id: int = None, vlan: int = None):
        if vlan not in [10, 20, 30, 40, 50, 60]:
            raise ValueError('Invalid VLAN ID')

        async with aiohttp.ClientSession() as session:
            if team_id:
                payload = UbusPayload(
                    params=[
                        self._session_id,
                        *config.UBUS_METHODS['UCI_SET'](
                            'network',
                            f'vlan{vlan}',
                            {
                                'proto': 'static',
                                'ipaddr': f'10.{team_id//100}.{team_id%100}.4',
                                'netmask': '255.255.255.0',
                            },
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=payload, timeout=self.timeout)

                payload = UbusPayload(
                    params=[
                        self._session_id,
                        *config.UBUS_METHODS['UCI_SET']('dhcp', f'vlan{vlan}', {'ignore': '0'}),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=payload, timeout=self.timeout)

            else:
                payload = UbusPayload(
                    params=[
                        self._session_id,
                        *config.UBUS_METHODS['UCI_SET'](
                            'network', f'vlan{vlan}', {'proto': 'none'}
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=payload, timeout=self.timeout)

                payload = UbusPayload(
                    params=[
                        self._session_id,
                        *config.UBUS_METHODS['UCI_DEL'](
                            'network', f'vlan{vlan}', ['ipaddr', 'netmask']
                        ),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=payload, timeout=self.timeout)

                payload = UbusPayload(
                    params=[
                        self._session_id,
                        *config.UBUS_METHODS['UCI_SET']('dhcp', f'vlan{vlan}', {'ignore': '1'}),
                    ]
                ).model_dump()
                await session.post(self.base_url, json=payload, timeout=self.timeout)

    async def commit_ethernet_configs(self):
        async with aiohttp.ClientSession() as session:
            commit_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['UCI_COMMIT']('network')]
            ).model_dump()
            await session.post(self.base_url, json=commit_payload, timeout=self.timeout)

            commit_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['UCI_COMMIT']('dhcp')]
            ).model_dump()
            await session.post(self.base_url, json=commit_payload, timeout=self.timeout)

            reload_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['RELOAD_NETWORK']]
            ).model_dump()
            await session.post(self.base_url, json=reload_payload, timeout=self.timeout)

            reload_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['RC_INIT']('dnsmasq')]
            ).model_dump()
            await session.post(self.base_url, json=reload_payload, timeout=self.timeout)

            reload_payload = UbusPayload(
                params=[self._session_id, *config.UBUS_METHODS['RC_INIT']('odhcpd')]
            ).model_dump()
            await session.post(self.base_url, json=reload_payload, timeout=self.timeout)
