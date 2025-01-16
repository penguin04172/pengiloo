import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

import models
from game.match_status import MATCH_STATUS
from models.base import db
from models.match import MATCH_TYPE

from .tba import TbaClient, new_tba_client


class TbaTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        db.bind(provider='sqlite', filename=':memory:', create_db=True)
        db.generate_mapping(create_tables=True)

    @classmethod
    def tearDownClass(cls) -> None:
        db.disconnect()

    def setUp(self) -> None:
        db.create_tables(True)

    def tearDown(self) -> None:
        db.drop_all_tables(with_all_data=True)

    @patch('third_party.tba.aiohttp.request')
    async def test_publish_team(self, mock_request):
        def mock_request_side_effect(method, url, body, headers):
            self.assertNotEqual(url.find('event/my_event_code'), -1)
            self.assertEqual(headers['X-TBA-Auth-Id'], 'my_secret_id')
            self.assertEqual(headers['X-TBA-Auth-Sig'], '690b307105e2c9eafcd40a2e2754510a')
            self.assertEqual(body.decode(), '["frc123","frc4567"]')

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {}

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect

        models.create_team(models.Team(id=123))
        models.create_team(models.Team(id=4567))

        client = new_tba_client('my_event_code', 'my_secret_id', 'my_secret')
        client.base_url = ''
        await client.publish_teams()

    @patch('third_party.tba.aiohttp.request')
    async def test_publish_matches(self, mock_request):
        def mock_request_side_effect(method, url, body, headers):
            self.assertNotEqual(url.find('event/my_event_code'), -1)
            self.assertEqual(headers['X-TBA-Auth-Id'], 'my_secret_id')
            self.assertEqual(headers['X-TBA-Auth-Sig'], '690b307105e2c9eafcd40a2e2754510a')
            self.assertEqual(body.decode(), '["frc123","frc4567"]')

            # 模擬 response 行為
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {}

            # 模擬上下文管理器行為
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            return mock_context

        mock_request.side_effect = mock_request_side_effect
        match1 = models.Match(
            type=MATCH_TYPE.qualification,
            type_order=2,
            short_name='Q2',
            scheduled_time=datetime.now(),
            red1=7,
            red2=8,
            red3=9,
            blue1=10,
            blue2=11,
            blue3=12,
            status=MATCH_STATUS.red_won_match,
            tba_match_key=models.TbaMatchKey(comp_level='qm', set_number=0, match_number=2),
        )
        match2 = models.Match(
            type=MATCH_TYPE.playoff,
            type_order=0,
            short_name='SF2-2',
            tba_match_key=models.TbaMatchKey(comp_level='omg', set_number=5, match_number=29),
        )
        models.create_match(match1)
        models.create_match(match2)
