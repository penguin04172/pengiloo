import unittest

from game.ranking import Ranking, RankingField

from .base import db
from .ranking import (
    create_ranking,
    read_all_rankings,
    read_ranking_for_team,
    truncate_ranking,
    update_ranking,
)


class TeamTest(unittest.TestCase):
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

    def ranking_1(self):
        return Ranking(
            team_id=7641,
            rank=1,
            previous_rank=0,
            **RankingField(
                ranking_points=20,
                coopertition_points=625,
                match_points=90,
                auto_points=554,
                barge_points=12,
                rand=0.7641,
                wins=3,
                losses=2,
                ties=1,
                disqualifications=0,
                played=10,
            ).model_dump(),
        )

    def ranking_2(self):
        return Ranking(
            team_id=6998,
            rank=2,
            previous_rank=1,
            **RankingField(
                ranking_points=18,
                coopertition_points=700,
                match_points=625,
                auto_points=90,
                barge_points=23,
                rand=0.6998,
                wins=1,
                losses=3,
                ties=2,
                disqualifications=0,
                played=10,
            ).model_dump(),
        )

    def test_read_nonexistent_ranking(self):
        ranking = read_ranking_for_team(7641)
        self.assertIsNone(ranking)

    def test_ranking_crud(self):
        ranking_ex = self.ranking_1()
        ranking_1 = create_ranking(ranking_ex)
        ranking_2 = read_ranking_for_team(7641)
        self.assertEqual(ranking_1, ranking_2)

        ranking_1.rand = 0.1234
        update_ranking(ranking_1)
        ranking_2 = read_ranking_for_team(7641)
        self.assertEqual(ranking_1, ranking_2)

    def test_truncate_rankings(self):
        ranking_ex = self.ranking_1()
        create_ranking(ranking_ex)
        truncate_ranking()
        ranking_2 = read_ranking_for_team(7641)
        self.assertIsNone(ranking_2)

    def test_read_all_rankings(self):
        rankings = read_all_rankings()
        self.assertEqual(len(rankings), 0)

        for i in range(20):
            create_ranking(Ranking(team_id=i + 1, rank=i))

        rankings = read_all_rankings()
        self.assertEqual(20, len(rankings))
        for i in range(20):
            self.assertEqual(i + 1, rankings[i].team_id)
