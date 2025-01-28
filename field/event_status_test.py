import asyncio
import unittest
from datetime import datetime, timedelta

import game
import models

from .specs import MatchState
from .test_helper import setup_test_arena_with_parameter


class EventStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
        models.db.generate_mapping(create_tables=True)

    @classmethod
    def tearDownClass(cls) -> None:
        models.db.disconnect()

    def setUp(self) -> None:
        models.db.create_tables(True)

    def tearDown(self) -> None:
        models.db.drop_all_tables(with_all_data=True)

    @staticmethod
    def set_match(match, match_time, started_at, is_complete):
        match.scheduled_time = match_time
        match.started_at = started_at
        if is_complete:
            match.status = game.MatchStatus.TIE_MATCH
        else:
            match.status = game.MatchStatus.MATCH_SCHEDULE
        models.update_match(match)

    def test_cycle_time(self):
        arena = setup_test_arena_with_parameter(self)
        arena.current_match.type = models.MatchType.PRACTICE

        self.assertEqual(arena.event_status.cycle_time, '')
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(0)))
        self.assertEqual(arena.event_status.cycle_time, '')
        asyncio.run(arena.update_cycle_time(datetime.now() - timedelta(seconds=125)))
        self.assertEqual(arena.event_status.cycle_time, '')
        asyncio.run(arena.update_cycle_time(datetime.now()))
        self.assertRegex(arena.event_status.cycle_time, r'^2:05.*')
        asyncio.run(arena.update_cycle_time(datetime.now() + timedelta(seconds=3456)))
        self.assertRegex(arena.event_status.cycle_time, r'^57:36.*')
        asyncio.run(arena.update_cycle_time(datetime.now() + timedelta(hours=5)))
        self.assertRegex(arena.event_status.cycle_time, r'^4:02:24.*')
        asyncio.run(arena.update_cycle_time(datetime.now() + timedelta(hours=123, seconds=1256)))
        self.assertRegex(arena.event_status.cycle_time, r'^118:20:56.*')

        arena.current_match.type = models.MatchType.TEST
        asyncio.run(arena.update_cycle_time(datetime.now() + timedelta(hours=123, seconds=1256)))
        self.assertEqual(arena.event_status.cycle_time, '')

    def test_cycle_time_delta(self):
        arena = setup_test_arena_with_parameter(self)
        arena.current_match.type = models.MatchType.PRACTICE

        arena.current_match.scheduled_time = datetime.fromtimestamp(1000)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1000)))
        self.assertEqual(arena.event_status.cycle_time, '')
        arena.current_match.scheduled_time = datetime.fromtimestamp(1754)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1754)))
        self.assertEqual(arena.event_status.cycle_time, '12:34 (0:00 faster than scheduled)')

        arena.current_match.scheduled_time = datetime.fromtimestamp(1000)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1000)))
        arena.current_match.scheduled_time = datetime.fromtimestamp(1500)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1417)))
        self.assertEqual(arena.event_status.cycle_time, '6:57 (1:23 faster than scheduled)')

        arena.current_match.scheduled_time = datetime.fromtimestamp(1000)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1000)))
        arena.current_match.scheduled_time = datetime.fromtimestamp(1500)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(2500)))
        self.assertEqual(arena.event_status.cycle_time, '25:00 (16:40 slower than scheduled)')

        arena.current_match.scheduled_time = datetime.fromtimestamp(1000)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(1000)))
        arena.current_match.scheduled_time = datetime.fromtimestamp(2000)
        asyncio.run(arena.update_cycle_time(datetime.fromtimestamp(2000)))
        self.assertEqual(arena.event_status.cycle_time, '')

    def test_early_late_message(self):
        arena = setup_test_arena_with_parameter(self)
        asyncio.run(arena.load_test_match())
        self.assertEqual(arena.get_early_late_message(), '')

        models.create_match(models.Match(type=models.MatchType.QUALIFICATION, type_order=1))
        models.create_match(models.Match(type=models.MatchType.QUALIFICATION, type_order=2))
        matches = models.read_matches_by_type(models.MatchType.QUALIFICATION, False)
        self.assertEqual(len(matches), 2)

        self.set_match(
            matches[0], datetime.now() + timedelta(seconds=300), datetime.fromtimestamp(0), False
        )
        arena.current_match = matches[0]
        arena.match_state = MatchState.PRE_MATCH
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[0], datetime.now() + timedelta(seconds=60), datetime.fromtimestamp(0), False
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[0], datetime.now() - timedelta(seconds=60), datetime.fromtimestamp(0), False
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[0], datetime.now() - timedelta(seconds=120), datetime.fromtimestamp(0), False
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[0], datetime.now() - timedelta(seconds=180), datetime.fromtimestamp(0), False
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes late')

        self.set_match(matches[0], datetime.now() + timedelta(seconds=181), datetime.now(), False)
        arena.match_state = MatchState.AUTO_PERIOD
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes early')

        self.set_match(
            matches[0],
            datetime.now() - timedelta(seconds=300),
            datetime.now() - timedelta(seconds=601),
            False,
        )
        self.set_match(
            matches[1],
            datetime.now() + timedelta(seconds=481),
            datetime.fromtimestamp(0),
            False,
        )
        arena.match_state = MatchState.POST_MATCH
        self.assertEqual(arena.get_early_late_message(), 'Event is running 5 minutes early')

        self.set_match(
            matches[1],
            datetime.now() + timedelta(seconds=181),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes early')

        self.set_match(
            matches[1],
            datetime.now() - timedelta(seconds=60),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[1],
            datetime.now() - timedelta(seconds=180),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes late')

        self.set_match(
            matches[0],
            datetime.now() - timedelta(seconds=300),
            datetime.now() - timedelta(seconds=601),
            True,
        )
        self.assertEqual(arena.get_early_late_message(), '')

        self.set_match(
            matches[1],
            datetime.now() + timedelta(seconds=900),
            datetime.fromtimestamp(0),
            False,
        )
        arena.current_match = matches[1]
        arena.match_state = MatchState.PRE_MATCH
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[1],
            datetime.now() + timedelta(seconds=899),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 5 minutes early')

        self.set_match(
            matches[1],
            datetime.now() + timedelta(seconds=60),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[1],
            datetime.now() - timedelta(seconds=120),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running on schedule')

        self.set_match(
            matches[1],
            datetime.now() - timedelta(seconds=180),
            datetime.fromtimestamp(0),
            False,
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes late')

        self.set_match(
            matches[1],
            datetime.now() - timedelta(seconds=180),
            datetime.now() - timedelta(seconds=541),
            False,
        )
        arena.match_state = MatchState.TELEOP_PERIOD
        self.assertEqual(arena.get_early_late_message(), 'Event is running 6 minutes early')

        self.set_match(
            matches[1],
            datetime.now(),
            datetime.now() + timedelta(seconds=481),
            False,
        )
        arena.match_state = MatchState.POST_MATCH
        self.assertEqual(arena.get_early_late_message(), 'Event is running 8 minutes late')

        self.set_match(
            matches[1],
            datetime.now(),
            datetime.now() + timedelta(seconds=481),
            True,
        )
        self.assertEqual(arena.get_early_late_message(), '')

        arena.match_state = MatchState.PRE_MATCH
        arena.current_match = models.Match(
            id=0,
            type=models.MatchType.PRACTICE,
            type_order=1,
            scheduled_time=datetime.now() - timedelta(seconds=181),
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes late')

        arena.current_match = models.Match(
            id=0,
            type=models.MatchType.PLAYOFF,
            type_order=1,
            scheduled_time=datetime.now() - timedelta(seconds=181),
        )
        self.assertEqual(arena.get_early_late_message(), 'Event is running 3 minutes late')
