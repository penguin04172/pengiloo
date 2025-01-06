import random
import unittest

from .match_status import ScoreSummary
from .ranking import *


class TestRanking(unittest.TestCase):
	def setUp(self) -> None:
		random.seed(0)

	def test_add_score_summary(self):
		red_summary = ScoreSummary(
			leave_points=4,
			auto_points=30,
			stage_points=19,
			match_points=67,
			score=67,
			coopertition_bonus=False,
			melody_bonus_ranking_point=False,
			ensemble_bonus_ranking_point=True,
			bonus_ranking_points=1,
		)

		blue_summary = ScoreSummary(
			leave_points=2,
			auto_points=16,
			stage_points=14,
			match_points=61,
			score=81,
			coopertition_bonus=True,
			melody_bonus_ranking_point=True,
			ensemble_bonus_ranking_point=True,
			bonus_ranking_points=1,
		)

		ranking_fields = RankingField()
		ranking_fields.add_score_summary(red_summary, blue_summary, False)
		self.assertEqual(
			ranking_fields,
			RankingField(
				ranking_points=1,
				coopertition_points=0,
				match_points=67,
				auto_points=30,
				stage_points=19,
				random=0.8444218515250481,
				wins=0,
				losses=1,
				ties=0,
				disqualifications=0,
				played=1,
			),
		)

		ranking_fields.add_score_summary(blue_summary, red_summary, False)
		self.assertEqual(
			ranking_fields,
			RankingField(
				ranking_points=4,
				coopertition_points=1,
				match_points=128,
				auto_points=46,
				stage_points=33,
				random=0.7579544029403025,
				wins=1,
				losses=1,
				ties=0,
				disqualifications=0,
				played=2,
			),
		)

		ranking_fields.add_score_summary(red_summary, red_summary, False)
		self.assertEqual(
			ranking_fields,
			RankingField(
				ranking_points=6,
				coopertition_points=1,
				match_points=195,
				auto_points=76,
				stage_points=52,
				random=0.420571580830845,
				wins=1,
				losses=1,
				ties=1,
				disqualifications=0,
				played=3,
			),
		)

		ranking_fields.add_score_summary(blue_summary, red_summary, True)
		self.assertEqual(
			ranking_fields,
			RankingField(
				ranking_points=6,
				coopertition_points=1,
				match_points=195,
				auto_points=76,
				stage_points=52,
				random=0.25891675029296335,
				wins=1,
				losses=1,
				ties=1,
				disqualifications=1,
				played=4,
			),
		)

	def test_sort_rankings(self):
		rankings = Rankings()
		rankings.append(
			Ranking(
				team_id=1,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.49,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=2,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.51,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=3,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=49,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=4,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=51,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=5,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=49,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=6,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=50,
					auto_points=51,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=7,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=49,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=8,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=50,
					match_points=51,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=9,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=49,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=10,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=50,
					coopertition_points=51,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=11,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=49,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=12,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=51,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.50,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.sort()
		self.assertEqual(12, rankings[0].team_id)
		self.assertEqual(10, rankings[1].team_id)
		self.assertEqual(8, rankings[2].team_id)
		self.assertEqual(6, rankings[3].team_id)
		self.assertEqual(4, rankings[4].team_id)
		self.assertEqual(2, rankings[5].team_id)
		self.assertEqual(1, rankings[6].team_id)
		self.assertEqual(3, rankings[7].team_id)
		self.assertEqual(5, rankings[8].team_id)
		self.assertEqual(7, rankings[9].team_id)
		self.assertEqual(9, rankings[10].team_id)
		self.assertEqual(11, rankings[11].team_id)

		rankings = Rankings()
		rankings.append(
			Ranking(
				team_id=1,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=10,
					coopertition_points=25,
					match_points=25,
					auto_points=25,
					stage_points=25,
					random=0.49,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=5,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=2,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=19,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.51,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=5,
				),
			)
		)
		rankings.append(
			Ranking(
				team_id=3,
				rank=0,
				previous_rank=0,
				fields=RankingField(
					ranking_points=20,
					coopertition_points=50,
					match_points=50,
					auto_points=50,
					stage_points=50,
					random=0.51,
					wins=3,
					losses=2,
					ties=1,
					disqualifications=0,
					played=10,
				),
			)
		)
		rankings.sort()
		self.assertEqual(2, rankings[0].team_id)
		self.assertEqual(3, rankings[1].team_id)
		self.assertEqual(1, rankings[2].team_id)
