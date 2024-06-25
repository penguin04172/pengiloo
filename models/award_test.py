import unittest
from .database import db
from .award import *

class TestAlliance(unittest.TestCase):
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

    def test_read_nonexist_award(self):
        award = read_award_by_id(7641)
        self.assertIsNone(award)

    def test_award_crud(self):
        award_ex = Award(type=AwardType.judged_award, award_name="Safety Award", team_id=7641)
        award_1 = create_award(award_ex)
        award_2 = read_award_by_id(1)
        self.assertEqual(award_1, award_2)

        award_2.id = None
        award_2.award_name = "Spirit Award"
        award_2 = create_award(award_2)
        awards = read_all_awards()
        self.assertEqual(2, len(awards))
        self.assertEqual(award_1, awards[0])
        self.assertEqual(award_2, awards[1])

        award_1.team_id = 0
        award_1.person_name = "ABCD EFG"
        update_award(award_1)
        award_2 = read_award_by_id(1)
        self.assertEqual(award_1.team_id, award_2.team_id)
        self.assertEqual(award_1.person_name, award_2.person_name)

        delete_award(1)
        award_2 = read_award_by_id(1)
        self.assertIsNone(award_2)

    def test_truncate_awards(self):
        award_ex = Award(type=AwardType.judged_award, award_name="Safety Award", team_id=7641)
        create_award(award_ex)
        truncate_awards()
        award_2 = read_award_by_id(1)
        self.assertIsNone(award_2)

    def test_read_award_by_type(self):
        award_1 = create_award(Award(type=AwardType.winner_award, award_name="Event Winner", team_id=6998))
        award_2 = create_award(Award(type=AwardType.finalist_award, award_name="Event Finalist", team_id=8121))
        award_3 = create_award(Award(type=AwardType.judged_award, award_name="Safety Award", team_id=7641))
        award_4 = create_award(Award(type=AwardType.winner_award, award_name="Event Winner", team_id=7641))

        awards = read_awards_by_type(AwardType.judged_award)
        self.assertEqual(1, len(awards))
        self.assertEqual(award_3, awards[0])

        awards = read_awards_by_type(AwardType.finalist_award)
        self.assertEqual(1, len(awards))
        self.assertEqual(award_2, awards[0])

        awards = read_awards_by_type(AwardType.winner_award)
        self.assertEqual(2, len(awards))
        self.assertEqual(award_1, awards[0])
        self.assertEqual(award_4, awards[1])

        


