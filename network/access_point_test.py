import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from models.team import Team
from network.access_point import (
    AccessPoint,
    APConfigurationError,
    APMonitoringError,
    StationStatus,
    TeamWifiStatus,
)
from network.openwrt import UbusLoginError, UbusTimeoutError


class TestAccessPoint(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ap = AccessPoint()
        self.ap.network_security_enabled = True
        self.ap.team_wifi_statuses = [TeamWifiStatus() for _ in range(6)]
        self.ap.ap = AsyncMock()

        # 設定基本的 mock 回傳值
        self.ap.ap.login.return_value = None
        self.ap.ap.get_wifi_info.return_value = {
            'ssid': '0',  # 修改：使用有效的預設 ssid
            'quality': 0,
            'signal': 0,
            'noise': 0,
        }
        self.ap.ap.get_wifi_clients.return_value = {}
        self.ap.ap.set_wifi_ssid_and_password.return_value = None

    async def test_update_monitoring_security_disabled(self):
        self.ap.network_security_enabled = False
        await self.ap.update_monitoring()
        self.ap.ap.login.assert_not_called()

    async def test_update_monitoring_login_failure(self):
        self.ap.ap.login.side_effect = UbusLoginError('Login failed')
        with self.assertRaises(APConfigurationError):
            await self.ap.update_monitoring()

    async def test_update_monitoring_timeout(self):
        self.ap.ap.login.side_effect = UbusTimeoutError('Timeout')
        with self.assertRaises(APMonitoringError):
            await self.ap.update_monitoring()

    async def test_update_monitoring_success(self):
        wifi_info = {
            'ssid': '1234',
            'quality': 70,
            'signal': -50,
            'noise': -90,
        }
        wifi_clients = {
            'aa:bb:cc:dd:ee:ff': {
                'rate': {'rx': 54000000, 'tx': 48000000},
                'airtime': {'rx': 1000000, 'tx': 2000000},
            }
        }

        self.ap.ap.get_wifi_info.return_value = wifi_info
        self.ap.ap.get_wifi_clients.return_value = wifi_clients

        await self.ap.update_monitoring()

        self.assertEqual(self.ap.team_wifi_statuses[0].team_id, 1234)
        self.assertTrue(self.ap.team_wifi_statuses[0].radio_linked)
        self.assertEqual(self.ap.team_wifi_statuses[0].rx_rate, 54.0)

    async def test_configure_team_wifi_security_disabled(self):
        self.ap.network_security_enabled = False
        teams = [Mock(spec=Team) for _ in range(6)]
        await self.ap.configure_team_wifi(teams)
        self.ap.ap.set_wifi_ssid_and_password.assert_not_called()

    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_configure_team_wifi_success(self, mock_sleep):
        teams = [Mock(spec=Team, id=i, wpakey=f'key{i}') for i in range(6)]
        self.ap.status_correct_configuration = Mock(return_value=True)

        await self.ap.configure_team_wifi(teams)

        self.assertEqual(self.ap.last_configured_teams, teams)
        mock_sleep.assert_not_called()

    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_configure_team_wifi_retry_success(self, mock_sleep):
        teams = [Mock(spec=Team, id=i, wpakey=f'key{i}') for i in range(6)]
        self.ap.status_correct_configuration = Mock(side_effect=[False, True])

        await self.ap.configure_team_wifi(teams)

        mock_sleep.assert_called_once_with(self.ap.retry_delay)
        self.assertEqual(self.ap.last_configured_teams, teams)

    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_configure_team_wifi_max_retries_failure(self, mock_sleep):
        teams = [Mock(spec=Team, id=i, wpakey=f'key{i}') for i in range(6)]
        self.ap.status_correct_configuration = Mock(return_value=False)

        with self.assertRaises(APConfigurationError):
            await self.ap.configure_team_wifi(teams)

        self.assertEqual(mock_sleep.call_count, self.ap.max_retries)


if __name__ == '__main__':
    unittest.main()
