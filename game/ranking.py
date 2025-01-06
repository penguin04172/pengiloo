import random

from pydantic import BaseModel

from .match_status import ScoreSummary


class RankingField(BaseModel):
	ranking_points: int = 0
	coopertition_points: int = 0
	match_points: int = 0
	auto_points: int = 0
	stage_points: int = 0
	random: float = random.random()
	wins: int = 0
	losses: int = 0
	ties: int = 0
	disqualifications: int = 0
	played: int = 0

	def add_score_summary(
		self, own_score: ScoreSummary, opponent_score: ScoreSummary, disqualfied: bool
	):
		self.played += 1
		self.random = random.random()

		if disqualfied:
			self.disqualifications += 1
			return

		# Check rp
		if own_score.score > opponent_score.score:
			self.ranking_points += 2
			self.wins += 1
		elif own_score.score == opponent_score.score:
			self.ranking_points += 1
			self.ties += 1
		else:
			self.losses += 1
		self.ranking_points += own_score.bonus_ranking_points

		# tiebreaker points
		if own_score.coopertition_bonus:
			self.coopertition_points += 1
		self.match_points += own_score.match_points
		self.auto_points += own_score.auto_points
		self.stage_points += own_score.stage_points


class Ranking(BaseModel):
	team_id: int
	rank: int
	previous_rank: int = 0
	fields: RankingField = RankingField()

	class Config:
		from_attributes = True

	def __lt__(self, other: 'Ranking'):
		if (
			self.fields.ranking_points * other.fields.played
			== other.fields.ranking_points * self.fields.played
		):
			if (
				self.fields.coopertition_points * other.fields.played
				== other.fields.coopertition_points * self.fields.played
			):
				if (
					self.fields.match_points * other.fields.played
					== other.fields.match_points * self.fields.played
				):
					if (
						self.fields.auto_points * other.fields.played
						== other.fields.auto_points * self.fields.played
					):
						if (
							self.fields.stage_points * other.fields.played
							== other.fields.stage_points * self.fields.played
						):
							return self.fields.random > other.fields.random
						return (
							self.fields.stage_points * other.fields.played
							> other.fields.stage_points * self.fields.played
						)
					return (
						self.fields.auto_points * other.fields.played
						> other.fields.auto_points * self.fields.played
					)
				return (
					self.fields.match_points * other.fields.played
					> other.fields.match_points * self.fields.played
				)
			return (
				self.fields.coopertition_points * other.fields.played
				> other.fields.coopertition_points * self.fields.played
			)
		return (
			self.fields.ranking_points * other.fields.played
			> other.fields.ranking_points * self.fields.played
		)


class Rankings(list[Ranking]):
	def len(self) -> int:
		return len(self)

	def swap(self, i, j):
		self[i], self[j] = self[j], self[i]
