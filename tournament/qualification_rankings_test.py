import random
import unittest

import game
import models
from models.base import db
from models.test_helper import build_test_match_result

from .qualification_rankings import (
    add_match_result_to_rankings,
    calculate_rankings,
    calculate_team_cards,
)


class TestQualificationRankings(unittest.TestCase):
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

    def test_calculate_rankings(self):
        random.seed(1)
        setup_match_results_for_testing()
        updated_rankings = calculate_rankings(False)
        rankings = models.read_all_rankings()
        self.assertEqual(updated_rankings, rankings)
        self.assertEqual(len(rankings), 6)
        self.assertEqual(rankings[0].team_id, 4)
        self.assertEqual(rankings[0].previous_rank, 0)
        self.assertEqual(rankings[1].team_id, 6)
        self.assertEqual(rankings[1].previous_rank, 0)
        self.assertEqual(rankings[2].team_id, 5)
        self.assertEqual(rankings[2].previous_rank, 0)
        self.assertEqual(rankings[3].team_id, 1)
        self.assertEqual(rankings[3].previous_rank, 0)
        self.assertEqual(rankings[4].team_id, 2)
        self.assertEqual(rankings[4].previous_rank, 0)
        self.assertEqual(rankings[5].team_id, 3)
        self.assertEqual(rankings[5].previous_rank, 0)

        previous_rankings = {}
        for ranking in rankings:
            previous_rankings[ranking.team_id] = ranking.rank

        match_result3 = build_test_match_result(3, 3)
        match_result3.blue_score, match_result3.red_score = (
            match_result3.red_score,
            match_result3.blue_score,
        )
        models.create_match_result(match_result3)
        updated_rankings = calculate_rankings(False)
        rankings = models.read_all_rankings()
        self.assertEqual(updated_rankings, rankings)
        self.assertEqual(len(rankings), 6)
        self.assertEqual(rankings[0].team_id, 6)
        self.assertEqual(rankings[0].previous_rank, previous_rankings[rankings[0].team_id])
        self.assertEqual(rankings[1].team_id, 5)
        self.assertEqual(rankings[1].previous_rank, previous_rankings[rankings[1].team_id])
        self.assertEqual(rankings[2].team_id, 4)
        self.assertEqual(rankings[2].previous_rank, previous_rankings[rankings[2].team_id])
        self.assertEqual(rankings[3].team_id, 1)
        self.assertEqual(rankings[3].previous_rank, previous_rankings[rankings[3].team_id])
        self.assertEqual(rankings[4].team_id, 2)
        self.assertEqual(rankings[4].previous_rank, previous_rankings[rankings[4].team_id])
        self.assertEqual(rankings[5].team_id, 3)
        self.assertEqual(rankings[5].previous_rank, previous_rankings[rankings[5].team_id])

        match_result3 = build_test_match_result(3, 4)
        models.create_match_result(match_result3)
        updated_rankings = calculate_rankings(True)
        rankings = models.read_all_rankings()
        self.assertEqual(updated_rankings, rankings)
        self.assertEqual(len(rankings), 6)
        self.assertEqual(rankings[0].team_id, 4)
        self.assertEqual(rankings[0].previous_rank, previous_rankings[rankings[0].team_id])
        self.assertEqual(rankings[1].team_id, 5)
        self.assertEqual(rankings[1].previous_rank, previous_rankings[rankings[1].team_id])
        self.assertEqual(rankings[2].team_id, 1)
        self.assertEqual(rankings[2].previous_rank, previous_rankings[rankings[2].team_id])
        self.assertEqual(rankings[3].team_id, 2)
        self.assertEqual(rankings[3].previous_rank, previous_rankings[rankings[3].team_id])
        self.assertEqual(rankings[4].team_id, 6)
        self.assertEqual(rankings[4].previous_rank, previous_rankings[rankings[4].team_id])
        self.assertEqual(rankings[5].team_id, 3)
        self.assertEqual(rankings[5].previous_rank, previous_rankings[rankings[5].team_id])

    def test_add_match_result_to_rankings_handle_cards(self):
        rankings = dict[int, game.Ranking]()
        match_result = build_test_match_result(1, 1)
        match_result.red_cards = {1: 'yellow', 2: 'red', 3: 'dq'}
        match_result.blue_cards = {4: 'red', 5: 'dq', 6: 'yellow'}
        add_match_result_to_rankings(rankings, 1, match_result, True)
        add_match_result_to_rankings(rankings, 2, match_result, True)
        add_match_result_to_rankings(rankings, 3, match_result, True)
        add_match_result_to_rankings(rankings, 4, match_result, False)
        add_match_result_to_rankings(rankings, 5, match_result, False)
        add_match_result_to_rankings(rankings, 6, match_result, False)
        self.assertEqual(rankings[1].fields.disqualifications, 0)
        self.assertEqual(rankings[2].fields.disqualifications, 1)
        self.assertEqual(rankings[3].fields.disqualifications, 1)
        self.assertEqual(rankings[4].fields.disqualifications, 1)
        self.assertEqual(rankings[5].fields.disqualifications, 1)
        self.assertEqual(rankings[6].fields.disqualifications, 0)


def setup_match_results_for_testing():
    match1 = models.Match(
        type=models.MATCH_TYPE.qualification,
        type_order=1,
        red1=1,
        red2=2,
        red3=3,
        blue1=4,
        blue2=5,
        blue3=6,
        status=game.MATCH_STATUS.red_won_match,
    )
    match1 = models.create_match(match1)
    match_result1 = build_test_match_result(match1.id, 1)
    match_result1.red_cards = {'2': 'red'}
    models.create_match_result(match_result1)

    match2 = models.Match(
        type=models.MATCH_TYPE.qualification,
        type_order=2,
        red1=1,
        red2=3,
        red3=5,
        blue1=2,
        blue2=4,
        blue3=6,
        status=game.MATCH_STATUS.blue_won_match,
        red2_is_surrogate=True,
        blue3_is_surrogate=True,
    )
    match2 = models.create_match(match2)
    match_result2 = build_test_match_result(match2.id, 1)
    match_result2.blue_score = match_result2.red_score
    models.create_match_result(match_result2)

    match3 = models.Match(
        type=models.MATCH_TYPE.qualification,
        type_order=3,
        red1=6,
        red2=5,
        red3=4,
        blue1=3,
        blue2=2,
        blue3=1,
        status=game.MATCH_STATUS.tie_match,
        red3_is_surrogate=True,
    )
    match3 = models.create_match(match3)
    match_result3 = build_test_match_result(match3.id, 1)
    models.create_match_result(match_result3)
    match_result3 = models.MatchResult(
        match_id=match3.id, play_number=2, match_type=models.MATCH_TYPE.qualification
    )
    models.create_match_result(match_result3)

    match4 = models.Match(
        type=models.MATCH_TYPE.pratice,
        type_order=1,
        red1=1,
        red2=2,
        red3=3,
        blue1=4,
        blue2=5,
        blue3=6,
        status=game.MATCH_STATUS.red_won_match,
    )
    match4 = models.create_match(match4)
    match_result4 = build_test_match_result(match4.id, 1)
    models.create_match_result(match_result4)

    match5 = models.Match(
        type=models.MATCH_TYPE.playoff,
        type_order=8,
        red1=1,
        red2=2,
        red3=3,
        blue1=4,
        blue2=5,
        blue3=6,
        status=game.MATCH_STATUS.blue_won_match,
    )
    match5 = models.create_match(match5)
    match_result5 = build_test_match_result(match5.id, 1)
    models.create_match_result(match_result5)

    match6 = models.Match(
        type=models.MATCH_TYPE.qualification,
        type_order=4,
        red1=7,
        red2=8,
        red3=9,
        blue1=10,
        blue2=11,
        blue3=12,
        status=game.MATCH_STATUS.match_scheduled,
    )
    match6 = models.create_match(match6)
    match_result6 = build_test_match_result(match6.id, 1)
    models.create_match_result(match_result6)
