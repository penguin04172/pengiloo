import unittest
from unittest.mock import AsyncMock, patch

from models.team import Team

from .access_point import (
    AccessPoint,
    AccessPointStatus,
    ConfigurationRequest,
    StationConfiguration,
    StationStatus,
    TeamWifiStatus,
)


class AccessPointTest(unittest.IsolatedAsyncioTestCase):
    @patch('network.access_point.aiohttp.request')
    async def test_configure(self, mock_request):
        ap = AccessPoint()
        configure_request = None
        wifi_status = [TeamWifiStatus() for _ in range(6)]
        ap.set_settings('', 'password1', 123, True, wifi_status)

        def mock_request_side_effect(method, url, json, headers):
            self.assertEqual(url, 'http:///configuration')
            self.assertEqual(headers.get('Authorization', None), 'Bearer password1')
            nonlocal configure_request
            configure_request = json

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 200

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect

        teams = [Team(id=i * 1111, wpakey=f'{i*11111111}') for i in range(1, 7)]

        await ap.configure_team_wifi(teams)
        self.assertEqual(
            ConfigurationRequest(
                channel=123,
                station_configurations={
                    'red1': StationConfiguration(ssid='1111', wpakey='11111111'),
                    'red2': StationConfiguration(ssid='2222', wpakey='22222222'),
                    'red3': StationConfiguration(ssid='3333', wpakey='33333333'),
                    'blue1': StationConfiguration(ssid='4444', wpakey='44444444'),
                    'blue2': StationConfiguration(ssid='5555', wpakey='55555555'),
                    'blue3': StationConfiguration(ssid='6666', wpakey='66666666'),
                },
            ).model_dump(),
            configure_request,
        )

        ap.channel = 456
        self.configure_request = {}
        await ap.configure_team_wifi([None, None, teams[1], None, teams[0], None])
        self.assertEqual(
            ConfigurationRequest(
                channel=456,
                station_configurations={
                    'red3': StationConfiguration(ssid='2222', wpakey='22222222'),
                    'blue2': StationConfiguration(ssid='1111', wpakey='11111111'),
                },
            ).model_dump(),
            configure_request,
        )

        def mock_request_side_effect2(method, url, json, headers):
            self.assertEqual(url, 'http:///configuration')
            self.assertEqual(headers.get('Authorization', None), 'Bearer password1')
            nonlocal configure_request
            configure_request = json

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 507
            mock_response.text.return_value = 'oops!'

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect2

        ret = await ap.configure_team_wifi(teams)
        self.assertEqual(ret, 'AP returned status 507')
        self.assertEqual('CONFIGURING', ap.status)

    @patch('network.access_point.aiohttp.request')
    async def test_update_monitoring(self, mock_request):
        ap = AccessPoint()
        wifi_status = [TeamWifiStatus() for _ in range(6)]
        ap.set_settings('', 'password2', 123, True, wifi_status)

        ap_status = AccessPointStatus(
            channel=456,
            status='ACTIVE',
            station_statuses={
                'red1': StationStatus(
                    ssid='1111',
                    hashed_wpakey='hash1111',
                    wpa_key_salt='salt1',
                    is_linked=True,
                    rx_rate_mbps=1,
                    tx_rate_mbps=2,
                    signal_noise_ratio=3,
                    bandwidth_used_mbps=4,
                ),
                'red2': StationStatus(
                    ssid='2222',
                    hashed_wpakey='hash2222',
                    wpa_key_salt='salt2',
                    is_linked=False,
                    rx_rate_mbps=5,
                    tx_rate_mbps=6,
                    signal_noise_ratio=7,
                    bandwidth_used_mbps=8,
                ),
                'red3': StationStatus(
                    ssid='3333',
                    hashed_wpakey='hash3333',
                    wpa_key_salt='salt3',
                    is_linked=True,
                    rx_rate_mbps=9,
                    tx_rate_mbps=10,
                    signal_noise_ratio=11,
                    bandwidth_used_mbps=12,
                ),
                'blue1': StationStatus(
                    ssid='4444',
                    hashed_wpakey='hash4444',
                    wpa_key_salt='salt4',
                    is_linked=False,
                    rx_rate_mbps=13,
                    tx_rate_mbps=14,
                    signal_noise_ratio=15,
                    bandwidth_used_mbps=16,
                ),
                'blue2': StationStatus(
                    ssid='5555',
                    hashed_wpakey='hash5555',
                    wpa_key_salt='salt5',
                    is_linked=True,
                    rx_rate_mbps=17,
                    tx_rate_mbps=18,
                    signal_noise_ratio=19,
                    bandwidth_used_mbps=20,
                ),
                'blue3': StationStatus(
                    ssid='6666',
                    hashed_wpakey='hash6666',
                    wpa_key_salt='salt6',
                    is_linked=False,
                    rx_rate_mbps=21,
                    tx_rate_mbps=22,
                    signal_noise_ratio=23,
                    bandwidth_used_mbps=24,
                ),
            },
        )
        # request_data = ap_status

        def mock_request_side_effect(method, url, headers):
            self.assertEqual(url, 'http:///status')
            self.assertEqual(headers.get('Authorization', None), 'Bearer password2')

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = ap_status.model_dump()

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect

        await ap.update_monitoring()

        self.assertEqual(ap.channel, 123)
        self.assertEqual(ap.status, 'ACTIVE')
        self.assertEqual(
            wifi_status[0],
            TeamWifiStatus(
                team_id=1111,
                radio_linked=True,
                mbits=4,
                rx_rate=1,
                tx_rate=2,
                signal_noise_ratio=3,
            ),
        )
        self.assertEqual(
            wifi_status[1],
            TeamWifiStatus(
                team_id=2222,
                radio_linked=False,
                mbits=8,
                rx_rate=5,
                tx_rate=6,
                signal_noise_ratio=7,
            ),
        )
        self.assertEqual(
            wifi_status[2],
            TeamWifiStatus(
                team_id=3333,
                radio_linked=True,
                mbits=12,
                rx_rate=9,
                tx_rate=10,
                signal_noise_ratio=11,
            ),
        )
        self.assertEqual(
            wifi_status[3],
            TeamWifiStatus(
                team_id=4444,
                radio_linked=False,
                mbits=16,
                rx_rate=13,
                tx_rate=14,
                signal_noise_ratio=15,
            ),
        )
        self.assertEqual(
            wifi_status[4],
            TeamWifiStatus(
                team_id=5555,
                radio_linked=True,
                mbits=20,
                rx_rate=17,
                tx_rate=18,
                signal_noise_ratio=19,
            ),
        )
        self.assertEqual(
            wifi_status[5],
            TeamWifiStatus(
                team_id=6666,
                radio_linked=False,
                mbits=24,
                rx_rate=21,
                tx_rate=22,
                signal_noise_ratio=23,
            ),
        )

        ap_status.status = 'CONFIGURING'
        ap_status.station_statuses = {
            'red1': None,
            'red2': None,
            'red3': StationStatus(
                ssid='123',
                hashed_wpakey='hash333',
                wpa_key_salt='salt3',
                is_linked=True,
                rx_rate_mbps=9,
                tx_rate_mbps=10,
                signal_noise_ratio=11,
                bandwidth_used_mbps=12,
            ),
            'blue1': None,
            'blue2': StationStatus(
                ssid='456',
                hashed_wpakey='hash555',
                wpa_key_salt='salt5',
                is_linked=False,
                rx_rate_mbps=17,
                tx_rate_mbps=18,
                signal_noise_ratio=19,
                bandwidth_used_mbps=20,
            ),
            'blue3': None,
        }
        await ap.update_monitoring()
        self.assertEqual(ap.status, 'CONFIGURING')
        self.assertEqual(wifi_status[0], TeamWifiStatus())
        self.assertEqual(wifi_status[1], TeamWifiStatus())
        self.assertEqual(
            wifi_status[2],
            TeamWifiStatus(
                team_id=123,
                radio_linked=True,
                mbits=12,
                rx_rate=9,
                tx_rate=10,
                signal_noise_ratio=11,
            ),
        )
        self.assertEqual(wifi_status[3], TeamWifiStatus())
        self.assertEqual(
            wifi_status[4],
            TeamWifiStatus(
                team_id=456,
                radio_linked=False,
                mbits=20,
                rx_rate=17,
                tx_rate=18,
                signal_noise_ratio=19,
            ),
        )
        self.assertEqual(wifi_status[5], TeamWifiStatus())

        def mock_request_side_effect2(method, url, headers):
            self.assertEqual(url, 'http:///status')
            self.assertEqual(headers.get('Authorization', None), 'Bearer password2')

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.text.return_value = 'oops!'

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect2
        ret = await ap.update_monitoring()
        self.assertEqual(ret, 'AP returned status 404')
        self.assertEqual('ERROR', ap.status)

    @patch('network.access_point.aiohttp.request')
    async def test_last_configuration(self, mock_request):
        ap = AccessPoint()
        wifi_status = [TeamWifiStatus() for _ in range(6)]
        ap.set_settings('', '', 123, True, wifi_status)

        def mock_request_side_effect(method, url, json, headers):
            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 200

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect

        self.assertTrue(ap.status_matches_last_last_configuration())

        team1 = Team(id=123, wpakey='11111111')
        team2 = Team(id=4567, wpakey='22222222')
        await ap.configure_team_wifi([None, team1, None, team2, None, None])
        self.assertFalse(ap.status_matches_last_last_configuration())

        ap.team_wifi_statuses[1].team_id = 123
        self.assertFalse(ap.status_matches_last_last_configuration())

        ap.team_wifi_statuses[3].team_id = 3456
        self.assertFalse(ap.status_matches_last_last_configuration())

        ap.team_wifi_statuses[3].team_id = 4567
        self.assertTrue(ap.status_matches_last_last_configuration())

        ap.team_wifi_statuses[4].team_id = 8877
        self.assertFalse(ap.status_matches_last_last_configuration())
