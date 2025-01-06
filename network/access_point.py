import logging
import time
from typing import Optional

import aiohttp
from pydantic import BaseModel

from models.team import Team

logger_ap = logging.getLogger('network.ap')

ACCESS_POINT_POLL_PERIOD_SEC = 1


class TeamWifiStatus(BaseModel):
    team_id: int = 0
    radio_linked: bool = False
    mbits: float = 0.0
    rx_rate: float = 0.0
    tx_rate: float = 0.0
    signal_noise_radio: int = 0


class ConfigurationRequest(BaseModel):
    channel: int = 0
    station_configurations: dict[str, 'StationConfiguration'] = {}

    class Config:
        alias = {'channel': 'channel', 'station_configurations': 'stationConfigurations'}
        populate_by_name = True


class StationConfiguration(BaseModel):
    ssid: str
    wpakey: str

    class Config:
        alias = {'ssid': 'ssid', 'wpakey': 'wpaKey'}
        populate_by_name = True


class AccessPointStatus(BaseModel):
    channel: int
    status: str
    station_statuses: dict[str, Optional['StationStatus']]

    class Config:
        alias = {'channel': 'channel', 'status': 'status', 'station_statuses': 'stationStatuses'}
        populate_by_name = True

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
    ssid: str
    hashed_wpakey: str
    wpa_key_salt: str
    is_linked: bool
    rx_rate_mbps: float
    tx_rate_mbps: float
    signal_noise_ratio: int
    bandwidth_used_mbps: float

    class Config:
        alias = {
            'ssid': 'ssid',
            'hashed_wpakey': 'hashedWpaKey',
            'wpa_key_salt': 'wpaKeySalt',
            'is_linked': 'isLinked',
            'rx_rate_mbps': 'rxRateMbps',
            'tx_rate_mbps': 'txRateMbps',
            'signal_noise_ratio': 'signalNoiseRatio',
            'bandwidth_used_mbps': 'bandwidthUsedMbps',
        }
        populate_by_name = True


class AccessPoint(BaseModel):
    api_url: str = ''
    password: str = ''
    channel: int = ''
    network_security_enabled: bool = False
    status: str = ''
    team_wifi_statuses: list[TeamWifiStatus] = [None] * 6
    last_configured_teams: list[Team] = [None] * 6

    def set_settings(
        self,
        address: str,
        password: str,
        channel: int,
        network_security_enabled: bool,
        wifi_statuses: list[TeamWifiStatus],
    ):
        self.api_url = f'http://{address}'
        self.password = password
        self.channel = channel
        self.network_security_enabled = network_security_enabled
        self.team_wifi_statuses = wifi_statuses

    async def run(self):
        while True:
            time.sleep(ACCESS_POINT_POLL_PERIOD_SEC)
            try:
                await self.update_monitoring()
            except:  # noqa: E722
                continue

            if self.status == 'ACTIVE' and not self.status_matches_last_last_configuration():
                logger_ap.warning(
                    'Access point is ACTIVE but does not match expected configuration; retrying configuration.'
                )
                try:
                    self.configure_team_wifi(self.last_configured_teams)
                except Exception as err:
                    logger_ap.error(f'Failed to reconfigure AP: {err}')

    async def configure_team_wifi(self, teams: list[Team | None]):
        if not self.network_security_enabled:
            return None

        self.status = 'CONFIGURING'
        self.last_configured_teams = teams
        request = ConfigurationRequest(channel=self.channel, station_configurations={})
        add_station(request.station_configurations, 'red1', teams[0])
        add_station(request.station_configurations, 'red2', teams[1])
        add_station(request.station_configurations, 'red3', teams[2])
        add_station(request.station_configurations, 'blue1', teams[3])
        add_station(request.station_configurations, 'blue2', teams[4])
        add_station(request.station_configurations, 'blue3', teams[5])

        url = f'{self.api_url}/configuration'
        headers = {}
        if self.password != '':
            headers = {'Authorization': f'Bearer {self.password}'}

        async with aiohttp.request(
            'POST', url=url, json=request.model_dump(by_alias=True), headers=headers
        ) as resp:
            if int(resp.status / 100) != 2:
                body = await resp.text()
                logger_ap.error(f'AP returned status {resp.status}: {body}')
                return f'AP returned status {resp.status}'

        logger_ap.info(
            'Access point accepted the new configuration and will apply it asynchronously.'
        )
        return None

    async def update_monitoring(self):
        if not self.network_security_enabled:
            return None

        url = f'{self.api_url}/status'
        headers = {}
        if self.password != '':
            headers = {'Authorization': f'Bearer {self.password}'}
        async with aiohttp.request('GET', url=url, headers=headers) as resp:
            if int(resp.status / 100) != 2:
                self.status = 'ERROR'
                body = await resp.text()
                logger_ap.error(f'AP returned status {resp.status}: {body}')
                return f'AP returned status {resp.status}'

            resp_data = await resp.json()
            ap_status = AccessPointStatus(**resp_data)
            if self.status != ap_status.status:
                logger_ap.info(f'AP status changed from {self.status} to {ap_status.status}')
                self.status = ap_status.status
                if self.status == 'ACTIVE':
                    logger_ap.info(f'AP detailed status:\n{ap_status.to_log_string()}')

            update_team_wifi_status(self.team_wifi_statuses[0], ap_status.station_statuses['red1'])
            update_team_wifi_status(self.team_wifi_statuses[1], ap_status.station_statuses['red2'])
            update_team_wifi_status(self.team_wifi_statuses[2], ap_status.station_statuses['red3'])
            update_team_wifi_status(self.team_wifi_statuses[3], ap_status.station_statuses['blue1'])
            update_team_wifi_status(self.team_wifi_statuses[4], ap_status.station_statuses['blue2'])
            update_team_wifi_status(self.team_wifi_statuses[5], ap_status.station_statuses['blue3'])
            return None

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
        team_wifi_status.signal_noise_radio = 0
    else:
        team_wifi_status.team_id = int(station_status.ssid)
        team_wifi_status.radio_linked = station_status.is_linked
        team_wifi_status.mbits = station_status.bandwidth_used_mbps
        team_wifi_status.rx_rate = station_status.rx_rate_mbps
        team_wifi_status.tx_rate = station_status.tx_rate_mbps
        team_wifi_status.signal_noise_radio = station_status.signal_noise_ratio
