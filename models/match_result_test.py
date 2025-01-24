import unittest

from game.score import EndgameStatus

from .base import db
from .match_result import (
    create_match_result,
    delete_match_result,
    read_match_result_for_match,
    truncate_match_results,
    update_match_result,
)
from .test_helper import build_test_match_result


class MatchResultTest(unittest.TestCase):
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

    def test_read_nonexist_match_result(self):
        result = read_match_result_for_match(7641)
        self.assertIsNone(result)

    def test_match_result_crud(self):
        match_result = create_match_result(build_test_match_result(7641, 5))
        match_result_2 = read_match_result_for_match(7641)
        self.assertEqual(match_result, match_result_2)

        match_result.blue_score.endgame_statuses = [
            EndgameStatus.PARK,
            EndgameStatus.NONE,
            EndgameStatus.CAGE_RIGHT,
        ]
        update_match_result(match_result)
        match_result_2 = read_match_result_for_match(7641)
        self.assertEqual(match_result, match_result_2)

        delete_match_result(match_result.id)
        match_result_2 = read_match_result_for_match(7641)
        self.assertIsNone(match_result_2)

    def test_truncate_match_results(self):
        create_match_result(build_test_match_result(7641, 1))
        truncate_match_results()
        match_result_2 = read_match_result_for_match(7641)
        self.assertIsNone(match_result_2)

    def test_read_match_result_for_match(self):
        create_match_result(build_test_match_result(7641, 2))
        match_result_2 = create_match_result(build_test_match_result(7641, 5))
        create_match_result(build_test_match_result(7641, 4))

        match_result_4 = read_match_result_for_match(7641)
        self.assertEqual(match_result_2, match_result_4)
