import asyncio
import logging
import math
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel

from models.team import Team

from . import openwrt

logger_ap = logging.getLogger(__name__)

ACCESS_POINT_POLL_PERIOD_SEC = 1
ACCESS_POINT_INTERFACES = ['phy1-ap0', 'phy1-ap1', 'phy1-ap2', 'phy1-ap3', 'phy1-ap4', 'phy1-ap5']


class AccessPointConnection(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    CONFIGURING = 2
    ERROR = 3


class TeamWifiStatus(BaseModel):
    team_id: int = 0
    radio_linked: bool = False
    mbits: float = 0.0
    rx_rate: float = 0.0
    tx_rate: float = 0.0
    signal_noise_ratio: int = 0
    connection_uptime: float = 0.0
    last_seen: float | None = None
    connection_quality: int = 0  # 0-100


class ConfigurationRequest(BaseModel):
    channel: int = 0
    station_configurations: dict[str, 'StationConfiguration'] = {}


class StationConfiguration(BaseModel):
    ssid: str
    wpakey: str


class AccessPointStatus(BaseModel):
    channel: int
    status: AccessPointConnection
    station_statuses: dict[str, Optional['StationStatus']]

    def to_log_string(self):
        buffer = f'Channel: {self.channel}\n'
        for station in ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']:
            station_status = self.station_statuses[station]
            ssid = '[empty]'
            if station_status is not None:
                ssid = station_status.ssid
            buffer += f'{station: <6}: {ssid}'
        return buffer


class StationStatus(BaseModel):
    ssid: str = ''
    is_linked: bool = False
    rx_rate_mbps: float = 0.0
    tx_rate_mbps: float = 0.0
    signal_noise_ratio: int = 0
    bandwidth_used_mbps: float = 0.0
    quality: int = 0


class APConfigurationError(Exception):
    pass


class APMonitoringError(Exception):
    pass


class AccessPoint:
    def __init__(self):
        self.ap = None
        self.channel = 0
        self.network_security_enabled = False
        self.team_wifi_statuses: list[TeamWifiStatus] = [None] * 6
        self.last_configured_teams: list[Team] = [None] * 6
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    def set_settings(
        self,
        address: str,
        password: str,
        channel: int,
        network_security_enabled: bool,
        wifi_statuses: list[TeamWifiStatus],
    ):
        self.ap = openwrt.UbusClient(host=address, username='root', password=password)
        self.channel = channel
        self.network_security_enabled = network_security_enabled
        self.team_wifi_statuses = wifi_statuses

    async def run(self):
        while True:
            await asyncio.sleep(ACCESS_POINT_POLL_PERIOD_SEC)
            try:
                await self.update_monitoring()
            except RuntimeError as err:
                logger_ap.error(f'Failed to update monitoring: {err}')

            if self.status_matches_last_last_configuration():
                logger_ap.warning(
                    'Access point does not match expected configuration; retrying configuration.'
                )
                try:
                    await self.configure_team_wifi(self.last_configured_teams)
                except Exception as err:
                    logger_ap.error(f'Failed to reconfigure AP: {err}')

    async def configure_team_wifi(self, teams: list[Team | None]):
        if not self.network_security_enabled:
            return

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

        for retry in range(self.max_retries):
            try:
                if await attempt_configuration():
                    self.last_configured_teams = teams
                    return

                logger_ap.info(f'配置未成功，正在重試 ({retry + 1}/{self.max_retries})')
                await asyncio.sleep(self.retry_delay)

            except Exception as err:
                logger_ap.error(f'第 {retry + 1} 次嘗試失敗: {err}')
                if retry < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                continue

        raise APConfigurationError('已達最大重試次數，配置失敗')

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
            station_status.ssid = wifi_info['ssid']
            station_status.quality = wifi_info.get('quality', 0)
            wifi_clients = await self.ap.get_wifi_clients(interface)

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

            update_team_wifi_status(self.team_wifi_statuses[i], station_status)

    def status_matches_last_last_configuration(self):
        for i in range(6):
            expect_team_id = 0
            actual_team_id = 0
            if self.last_configured_teams[i] is not None:
                expect_team_id = self.last_configured_teams[i].id

            if self.team_wifi_statuses[i] is not None:
                actual_team_id = self.team_wifi_statuses[i].team_id

            if expect_team_id != actual_team_id:
                return False
        return True

    def status_correct_configuration(self, teams: list[Team | None]):
        for i, team in enumerate(teams):
            expected_team_id = 0
            if team is not None:
                expected_team_id = team.id

            if self.team_wifi_statuses[i].team_id != expected_team_id:
                return False

        return True


def add_station(stations_configurations: dict[str, StationConfiguration], station: str, team: Team):
    if team is None:
        return

    stations_configurations[station] = StationConfiguration(ssid=str(team.id), wpakey=team.wpakey)


def update_team_wifi_status(team_wifi_status: TeamWifiStatus, station_status: StationStatus):
    if station_status is None:
        team_wifi_status.team_id = 0
        team_wifi_status.radio_linked = False
        team_wifi_status.mbits = 0
        team_wifi_status.rx_rate = 0
        team_wifi_status.tx_rate = 0
        team_wifi_status.signal_noise_ratio = 0
    else:
        team_wifi_status.team_id = int(station_status.ssid)
        team_wifi_status.radio_linked = station_status.is_linked
        team_wifi_status.mbits = station_status.bandwidth_used_mbps
        team_wifi_status.rx_rate = station_status.rx_rate_mbps
        team_wifi_status.tx_rate = station_status.tx_rate_mbps
        team_wifi_status.signal_noise_ratio = station_status.signal_noise_ratio
