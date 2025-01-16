import unittest
from datetime import datetime

from .base import db
from .match import MatchType
from .scheduled_break import (
    ScheduledBreak,
    create_scheduled_break,
    delete_scheduled_breaks_by_match_type,
    read_scheduled_break_by_id,
    read_scheduled_break_by_match_type_order,
    read_scheduled_breaks_by_match_type,
    truncate_scheduled_breaks,
    update_scheduled_break,
)


class TestScheduleBreak(unittest.TestCase):
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

    def test_schedule_break_crud(self):
        scheduled_break1 = ScheduledBreak(
            match_type=MatchType.QUALIFICATION,
            type_order_before=50,
            time=datetime.now(),
            duration_sec=600,
            description='Lunch break',
        )
        scheduled_break1 = create_scheduled_break(scheduled_break1)

        scheduled_break2 = ScheduledBreak(
            match_type=MatchType.QUALIFICATION,
            type_order_before=25,
            time=datetime.now(),
            duration_sec=300,
            description='Breakfast break',
        )
        scheduled_break2 = create_scheduled_break(scheduled_break2)

        scheduled_break3 = ScheduledBreak(
            match_type=MatchType.PLAYOFF,
            type_order_before=4,
            time=datetime.now(),
            duration_sec=900,
            description='Awards',
        )
        scheduled_break3 = create_scheduled_break(scheduled_break3)

        scheduled_break = read_scheduled_break_by_id(1)
        self.assertEqual(scheduled_break, scheduled_break1)
        scheduled_break = read_scheduled_break_by_id(2)
        self.assertEqual(scheduled_break, scheduled_break2)

        scheduled_break2.description = 'Brunch break'
        scheduled_break2 = update_scheduled_break(scheduled_break2)
        scheduled_break = read_scheduled_break_by_id(2)
        self.assertEqual(scheduled_break, scheduled_break2)

        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.PRATICE)
        self.assertEqual(len(scheduled_breaks), 0)
        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(scheduled_breaks), 2)
        self.assertEqual(scheduled_breaks[0], scheduled_break1)
        self.assertEqual(scheduled_breaks[1], scheduled_break2)

        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.PLAYOFF)
        self.assertEqual(len(scheduled_breaks), 1)
        self.assertEqual(scheduled_breaks[0], scheduled_break3)

        scheduled_break = read_scheduled_break_by_match_type_order(MatchType.QUALIFICATION, 25)
        self.assertEqual(scheduled_break, scheduled_break2)
        scheduled_break = read_scheduled_break_by_match_type_order(MatchType.PLAYOFF, 4)
        self.assertEqual(scheduled_break, scheduled_break3)
        scheduled_break = read_scheduled_break_by_match_type_order(MatchType.PLAYOFF, 5)
        self.assertIsNone(scheduled_break)

        delete_scheduled_breaks_by_match_type(MatchType.PLAYOFF)
        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.PLAYOFF)
        self.assertEqual(len(scheduled_breaks), 0)
        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(scheduled_breaks), 2)

        truncate_scheduled_breaks()
        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(scheduled_breaks), 0)
        scheduled_breaks = read_scheduled_breaks_by_match_type(MatchType.PLAYOFF)
        self.assertEqual(len(scheduled_breaks), 0)
