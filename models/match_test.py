import unittest
from datetime import datetime

from .base import db
from .match import (
    Match,
    MatchStatus,
    MatchType,
    TbaMatchKey,
    create_match,
    delete_match,
    read_match_by_id,
    read_match_by_type_order,
    read_matches_by_type,
    truncate_matches,
    update_match,
)


class MatchTest(unittest.TestCase):
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

    def test_get_nonexist_match(self):
        match = read_match_by_id(7641)
        self.assertIsNone(match)

    def test_match_crud(self):
        match_ex = Match(
            type=MatchType.QUALIFICATION,
            type_order=7641,
            scheduled_time=datetime(2024, 2, 1),
            long_name='Qualification 7641',
            short_name='Q7641',
            name_detail='Qual Round',
            red1=1,
            red2=2,
            red3=3,
            blue1=4,
            blue2=5,
            blue3=6,
            use_tiebreak_criteria=True,
            tba_match_key=TbaMatchKey(comp_level='qm', set_number=0, match_number=7641),
        )

        match = create_match(match_ex)
        match_2 = read_match_by_id(1)
        self.assertEqual(match, match_2)

        match_2 = read_match_by_type_order(MatchType.QUALIFICATION, 7641)
        self.assertEqual(match, match_2)

        match.status = MatchStatus.RED_WON_MATCH
        match_2 = update_match(match)
        self.assertEqual(match, match_2)

        delete_match(match.id)
        match_2 = read_match_by_id(match.id)
        self.assertIsNone(match_2)

    def test_truncate_matches(self):
        match_ex = Match(
            type=MatchType.QUALIFICATION,
            type_order=7641,
            long_name='Qualification 7641',
            short_name='Q7641',
            name_detail='Qual Round',
            red1=1,
            red2=2,
            red3=3,
            blue1=4,
            blue2=5,
            blue3=6,
        )
        create_match(match_ex)
        truncate_matches()
        match_2 = read_match_by_id(1)
        self.assertIsNone(match_2)

    def test_read_by_type_order(self):
        match_ex = Match(type=MatchType.PRACTICE, type_order=2, short_name='P2')
        match_ex1 = create_match(match_ex)

        match_ex = Match(type=MatchType.QUALIFICATION, type_order=2, short_name='Q2')
        match_ex2 = create_match(match_ex)

        match = read_match_by_type_order(MatchType.QUALIFICATION, 1)
        self.assertIsNone(match)

        match = read_match_by_type_order(MatchType.QUALIFICATION, 2)
        self.assertEqual(match, match_ex2)

        match = read_match_by_type_order(MatchType.PRACTICE, 2)
        self.assertEqual(match, match_ex1)

    def test_read_matches_by_type(self):
        match_ex = Match(type=MatchType.QUALIFICATION, type_order=1, short_name='Q1')
        match_1 = create_match(match_ex)

        match_ex = Match(type=MatchType.PRACTICE, type_order=2, short_name='P2')
        match_2 = create_match(match_ex)

        match_ex = Match(type=MatchType.PRACTICE, type_order=1, short_name='P1')
        match_3 = create_match(match_ex)

        matches = read_matches_by_type(MatchType.TEST)
        self.assertEqual(matches, [])

        matches = read_matches_by_type(MatchType.PRACTICE)
        self.assertEqual(2, len(matches))
        self.assertEqual(match_2, matches[1])
        self.assertEqual(match_3, matches[0])

        matches = read_matches_by_type(MatchType.QUALIFICATION)
        self.assertEqual(1, len(matches))
        self.assertEqual(match_1, matches[0])

        match_3.status = MatchStatus.MATCH_HIDDEN
        update_match(match_3)
        matches = read_matches_by_type(MatchType.PRACTICE)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], match_2)

        matches = read_matches_by_type(MatchType.PRACTICE, True)
        self.assertEqual(len(matches), 2)
        self.assertEqual(match_2, matches[1])
        self.assertEqual(match_3, matches[0])

    def test_tba_match_key(self):
        key = TbaMatchKey(comp_level='p', set_number=0, match_number=3)
        self.assertEqual(str(key), 'p3')

        key = TbaMatchKey(comp_level='qm', set_number=0, match_number=17)
        self.assertEqual(str(key), 'qm17')

        key = TbaMatchKey(comp_level='sf', set_number=5, match_number=1)
        self.assertEqual(str(key), 'sf5m1')

        key = TbaMatchKey(comp_level='f', set_number=1, match_number=4)
        self.assertEqual(str(key), 'f1m4')
