import random
import unittest
import unittest.mock
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import models

from .schedule import build_random_schedule


class TestSchedule(unittest.IsolatedAsyncioTestCase):
    def assert_match(
        self,
        match,
        match_type,
        type_order,
        time_in_sec,
        short_name,
        long_name,
        tba_comp_level,
        red1,
        red2,
        red3,
        blue1,
        blue2,
        blue3,
    ):
        self.assertEqual(match.type, match_type)
        self.assertEqual(match.type_order, type_order)
        self.assertEqual(match.scheduled_time, datetime.min + timedelta(seconds=time_in_sec))
        self.assertEqual(match.short_name, short_name)
        self.assertEqual(match.long_name, long_name)
        self.assertEqual(match.name_detail, None)
        self.assertEqual(match.playoff_red_alliance, None)
        self.assertEqual(match.playoff_blue_alliance, None)
        self.assertEqual(match.red1, red1)
        self.assertEqual(match.red2, red2)
        self.assertEqual(match.red3, red3)
        self.assertEqual(match.blue1, blue1)
        self.assertEqual(match.blue2, blue2)
        self.assertEqual(match.blue3, blue3)
        self.assertEqual(match.tba_match_key.comp_level, tba_comp_level)
        self.assertEqual(match.tba_match_key.set_number, 0)
        self.assertEqual(match.tba_match_key.match_number, type_order)

    @patch('tournament.schedule.asyncio.create_subprocess_exec')
    async def test_schedule_teams(self, mock_subprocess):
        random.seed(0)
        teams = [models.Team(id=i + 101) for i in range(18)]
        process_mock = unittest.mock.AsyncMock()
        process_mock.communicate.return_value = (
            b'1 15 0 11 0 8 0 9 0 6 0 17 0\n'
            + b'2 14 0 12 0 3 0 1 0 4 0 18 0\n'
            + b'3 10 0 7 0 5 0 6 0 13 0 2 0\n'
            + b'4 12 0 8 0 9 0 1 0 11 0 3 0\n'
            + b'5 13 0 17 0 15 0 10 0 14 0 2 0\n'
            + b'6 18 0 5 0 6 0 7 0 4 0 16 0\n',
            b'',
        )
        mock_subprocess.return_value = process_mock

        schedule_blocks = [
            models.ScheduleBlock(
                match_type=models.MATCH_TYPE.pratice,
                start_time=datetime.min,
                num_matches=6,
                match_spacing_sec=60,
            )
        ]

        with patch('builtins.open', mock_open()) as mock_file:
            matches = await build_random_schedule(teams, schedule_blocks, models.MATCH_TYPE.pratice)

        self.assertEqual(len(matches), 6)
        self.assert_match(
            matches[0],
            models.MATCH_TYPE.pratice,
            1,
            0,
            'P1',
            'Practice 1',
            'p',
            117,
            104,
            115,
            118,
            108,
            110,
        )
        self.assert_match(
            matches[1],
            models.MATCH_TYPE.pratice,
            2,
            60,
            'P2',
            'Practice 2',
            'p',
            103,
            111,
            102,
            113,
            105,
            112,
        )
        self.assert_match(
            matches[2],
            models.MATCH_TYPE.pratice,
            3,
            120,
            'P3',
            'Practice 3',
            'p',
            106,
            107,
            109,
            108,
            116,
            114,
        )
        self.assert_match(
            matches[3],
            models.MATCH_TYPE.pratice,
            4,
            180,
            'P4',
            'Practice 4',
            'p',
            111,
            115,
            118,
            113,
            104,
            102,
        )
        self.assert_match(
            matches[4],
            models.MATCH_TYPE.pratice,
            5,
            240,
            'P5',
            'Practice 5',
            'p',
            116,
            110,
            117,
            106,
            103,
            114,
        )
        self.assert_match(
            matches[5],
            models.MATCH_TYPE.pratice,
            6,
            300,
            'P6',
            'Practice 6',
            'p',
            112,
            109,
            108,
            107,
            105,
            101,
        )

        schedule_blocks = [
            models.ScheduleBlock(
                match_type=models.MATCH_TYPE.qualification,
                start_time=datetime.min,
                num_matches=6,
                match_spacing_sec=60,
            )
        ]

        with patch('builtins.open', mock_open()) as mock_file:
            matches = await build_random_schedule(
                teams, schedule_blocks, models.MATCH_TYPE.qualification
            )

        self.assertEqual(len(matches), 6)
        self.assert_match(
            matches[0],
            models.MATCH_TYPE.qualification,
            1,
            0,
            'Q1',
            'Qualification 1',
            'qm',
            118,
            112,
            108,
            109,
            111,
            107,
        )
        self.assert_match(
            matches[1],
            models.MATCH_TYPE.qualification,
            2,
            60,
            'Q2',
            'Qualification 2',
            'qm',
            105,
            117,
            103,
            110,
            115,
            101,
        )
        self.assert_match(
            matches[2],
            models.MATCH_TYPE.qualification,
            3,
            120,
            'Q3',
            'Qualification 3',
            'qm',
            102,
            106,
            114,
            111,
            116,
            104,
        )
        self.assert_match(
            matches[3],
            models.MATCH_TYPE.qualification,
            4,
            180,
            'Q4',
            'Qualification 4',
            'qm',
            117,
            108,
            109,
            110,
            112,
            103,
        )
        self.assert_match(
            matches[4],
            models.MATCH_TYPE.qualification,
            5,
            240,
            'Q5',
            'Qualification 5',
            'qm',
            116,
            107,
            118,
            102,
            105,
            104,
        )
        self.assert_match(
            matches[5],
            models.MATCH_TYPE.qualification,
            6,
            300,
            'Q6',
            'Qualification 6',
            'qm',
            101,
            114,
            111,
            106,
            115,
            113,
        )
