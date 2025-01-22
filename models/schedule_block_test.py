import unittest
from datetime import datetime, timedelta

from .base import db
from .match import MatchType
from .schedule_block import (
    ScheduleBlock,
    create_schedule_block,
    delete_schedule_block_by_match_type,
    read_schedule_blocks_by_match_type,
    truncate_schedule_blocks,
)


class TestScheduleBlock(unittest.TestCase):
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

    def test_schedule_block_crud(self):
        schedule_block1 = ScheduleBlock(
            match_type=MatchType.PRACTICE,
            start_time=datetime.now(),
            num_matches=10,
            match_spacing_sec=600,
        )
        schedule_block1 = create_schedule_block(schedule_block1)

        schedule_block2 = ScheduleBlock(
            match_type=MatchType.QUALIFICATION,
            start_time=datetime.now(),
            num_matches=20,
            match_spacing_sec=480,
        )
        schedule_block2 = create_schedule_block(schedule_block2)

        schedule_block3 = ScheduleBlock(
            match_type=MatchType.QUALIFICATION,
            start_time=schedule_block2.start_time + timedelta(seconds=20 * 480),
            num_matches=20,
            match_spacing_sec=480,
        )
        schedule_block3 = create_schedule_block(schedule_block3)

        blocks = read_schedule_blocks_by_match_type(MatchType.PRACTICE)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0], schedule_block1)

        blocks = read_schedule_blocks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0], schedule_block2)
        self.assertEqual(blocks[1], schedule_block3)

        delete_schedule_block_by_match_type(MatchType.PRACTICE)
        blocks = read_schedule_blocks_by_match_type(MatchType.PRACTICE)
        self.assertEqual(len(blocks), 0)

        blocks = read_schedule_blocks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(blocks), 2)

        truncate_schedule_blocks()
        blocks = read_schedule_blocks_by_match_type(MatchType.QUALIFICATION)
        self.assertEqual(len(blocks), 0)
