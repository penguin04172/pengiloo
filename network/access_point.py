import asyncio
import logging
import math

from pydantic import BaseModel

from models.team import Team

from . import openwrt

logger_ap = logging.getLogger(__name__)

ACCESS_POINT_POLL_PERIOD_SEC = 3
ACCESS_POINT_RETRY_DELAY_SEC = 30
ACCESS_POINT_INTERFACES = ['phy2-ap0', 'phy2-ap1', 'phy2-ap2', 'phy2-ap3', 'phy2-ap4', 'phy2-ap5']


class TeamWifiStatus(BaseModel):
    team_id: int = 0
    radio_linked: bool = False
    mbits: float = 0.0
    rx_rate: float = 0.0
    tx_rate: float = 0.0
    signal_noise_ratio: int = 0
    connection_quality: int = 0


class StationStatus(BaseModel):
    team_id: int = 0
    is_linked: bool = False
    rx_rate_mbps: float = 0.0
    tx_rate_mbps: float = 0.0
    signal_noise_ratio: int = 0
    bandwidth_used_mbps: float = 0.0
    connection_quality: int = 0


class APConfigurationError(Exception):
    pass


class APMonitoringError(Exception):
    pass


class AccessPoint:
    def __init__(self):
        self.ap = None
        self.channel = 149
        self.network_security_enabled = False
        self.team_wifi_statuses: list[TeamWifiStatus] = [None] * 6
        self.last_configured_teams: list[Team] = [None] * 6
        self.status: str = 'UnKnown'
        self.config_request_queue = asyncio.Queue(10)

    async def set_settings(
        self,
        address: str,
        password: str,
        channel: int,
        network_security_enabled: bool,
        wifi_statuses: list[TeamWifiStatus],
    ):
        self.ap = openwrt.UbusClient(host=address, username='root', password=password)
        self.network_security_enabled = network_security_enabled
        self.team_wifi_statuses = wifi_statuses
        self.status = 'ACTIVE'

        if self.channel != channel and self.network_security_enabled:
            logger_ap.info(f'設定 AP 頻道至 {channel}')
            asyncio.create_task(self.ap.set_wifi_channel(channel, 1))
            self.channel = channel

    async def run(self):
        """主要運行迴圈，處理配置請求和監控狀態"""
        while True:
            try:
                # 使用 asyncio.wait_for 設定等待超時
                config_request = await asyncio.wait_for(
                    self.config_request_queue.get(), timeout=ACCESS_POINT_POLL_PERIOD_SEC
                )
                # 清空佇列中的其他請求，只處理最新的
                while not self.config_request_queue.empty():
                    config_request = await self.config_request_queue.get()

                # 處理配置請求
                try:
                    await self.handle_configuration_request(config_request)
                except Exception as err:
                    logger_ap.error(f'配置失敗: {err}')
                    self.status = 'ErrorConfig'

            except asyncio.TimeoutError:  # noqa
                # 超時時執行定期監控
                try:
                    await self.update_monitoring()
                except Exception as err:
                    logger_ap.error(f'監控更新失敗: {err}')
                    self.status = 'ErrorMonitor'

    async def configure_team_wifi(self, teams: list[Team | None]):
        """提交新的配置請求"""
        await self.config_request_queue.put(teams)
        # print(f'configure_team_wifi: {teams}')

    async def handle_configuration_request(self, teams: list[Team | None]):
        """處理配置請求"""
        if not self.network_security_enabled:
            return

        if self.status_correct_configuration(teams):
            return

        self.status = 'CONFIGURING'
        await self.configure_teams(teams)

    async def configure_teams(self, teams: list[Team | None]):
        retry = 0

        async def attempt_configuration():
            await self.update_monitoring()
            if self.status_correct_configuration(teams):
                return True

            await self.ap.set_wifi_ssid_and_password(
                self.channel,
                [
                    {'id': team.id, 'wpakey': team.wpakey}
                    if team is not None
                    else {'id': None, 'wpakey': None}
                    for team in teams
                ],
            )
            return False

        while True:
            try:
                if await attempt_configuration():
                    self.last_configured_teams = teams
                    return

                logger_ap.info(f'配置未成功，正在重試 ({retry + 1}')
                await asyncio.sleep(3)

            except Exception as err:
                logger_ap.error(f'第 {retry + 1} 次嘗試失敗: {err}')
                retry += 1
                await asyncio.sleep(ACCESS_POINT_RETRY_DELAY_SEC)
                continue

    async def update_monitoring(self):
        if not self.network_security_enabled:
            return

        try:
            await self.ap.login()
        except openwrt.UbusLoginError as err:
            raise APConfigurationError(f'認證失敗: {err}') from err
        except openwrt.UbusTimeoutError as err:
            raise APMonitoringError(f'連線逾時: {err}') from err

        for i, interface in enumerate(ACCESS_POINT_INTERFACES):
            station_status = StationStatus()
            wifi_info = await self.ap.get_wifi_info(interface)
            # print(f'wifi_info: {wifi_info}')
            self.channel = wifi_info['channel']
            ssid = wifi_info['ssid']
            station_status.team_id = 0 if 'no-team' in ssid else int(ssid)
            station_status.connection_quality = wifi_info.get('quality', 0)
            wifi_clients = await self.ap.get_wifi_assoclist(interface)
            logger_ap.info(f'wifi_clients: {wifi_clients}')

            if len(wifi_clients) > 0:
                mac = list(wifi_clients.keys())[0]
                station_status.is_linked = True
                station_status.rx_rate_mbps = wifi_clients[mac]['rate']['rx'] / 1000000
                station_status.tx_rate_mbps = wifi_clients[mac]['rate']['tx'] / 1000000
                station_status.signal_noise_ratio = 20 * math.log10(
                    wifi_info['signal'] / wifi_info['noise']
                )
                station_status.bandwidth_used_mbps = (
                    wifi_clients[mac]['airtime']['rx'] + wifi_clients[mac]['airtime']['tx']
                ) / 1000000
            logger_ap.info(f'station_status: {station_status}')

            self.team_wifi_statuses[i] = TeamWifiStatus(**station_status.model_dump())
        print(f'team_wifi_statuses: {self.team_wifi_statuses}')

    def status_correct_configuration(self, teams: list[Team | None]):
        for i, team in enumerate(teams):
            expected_team_id = 0
            if team is not None:
                expected_team_id = team.id

            if self.team_wifi_statuses[i].team_id != expected_team_id:
                return False

        return True

    async def get_team_wifi_status(self, station_id: str):
        if station_id not in ['R1', 'R2', 'R3', 'B1', 'B2', 'B3']:
            return None
        return self.team_wifi_statuses[station_id]


def update_team_wifi_status(team_wifi_status: list[TeamWifiStatus], station_status: StationStatus):
    if station_status is None:
        team_wifi_status[0].team_id = 0
        team_wifi_status[0].radio_linked = False
        team_wifi_status[0].mbits = 0
        team_wifi_status[0].rx_rate = 0
        team_wifi_status[0].tx_rate = 0
        team_wifi_status[0].signal_noise_ratio = 0
        team_wifi_status[0].connection_quality = 0
    else:
        team_wifi_status[0].team_id = int(station_status.ssid)
        team_wifi_status[0].radio_linked = station_status.is_linked
        team_wifi_status[0].mbits = station_status.bandwidth_used_mbps
        team_wifi_status[0].rx_rate = station_status.rx_rate_mbps
        team_wifi_status[0].tx_rate = station_status.tx_rate_mbps
        team_wifi_status[0].signal_noise_ratio = station_status.signal_noise_ratio
        team_wifi_status[0].connection_quality = station_status.connection_quality
