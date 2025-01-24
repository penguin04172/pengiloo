import random

from pydantic import BaseModel

from .score_summary import ScoreSummary


class RankingField(BaseModel):
    ranking_points: int = 0
    coopertition_points: int = 0
    match_points: int = 0
    auto_points: int = 0
    barge_points: int = 0
    rand: float = random.random()
    wins: int = 0
    losses: int = 0
    ties: int = 0
    disqualifications: int = 0
    played: int = 0

    def add_score_summary(
        self, own_score: ScoreSummary, opponent_score: ScoreSummary, disqualfied: bool
    ):
        self.played += 1
        self.rand = random.random()

        if disqualfied:
            self.disqualifications += 1
            return

        # Check rp
        if own_score.score > opponent_score.score:
            self.ranking_points += 3
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
        self.barge_points += own_score.barge_points


class Ranking(RankingField):
    team_id: int
    rank: int = 0
    previous_rank: int = 0

    class Config:
        from_attributes = True

    def __lt__(self, other: 'Ranking'):
        if self.ranking_points * other.played == other.ranking_points * self.played:
            if self.coopertition_points * other.played == other.coopertition_points * self.played:
                if self.match_points * other.played == other.match_points * self.played:
                    if self.auto_points * other.played == other.auto_points * self.played:
                        if self.barge_points * other.played == other.barge_points * self.played:
                            return self.rand > other.rand
                        return self.barge_points * other.played > other.barge_points * self.played
                    return self.auto_points * other.played > other.auto_points * self.played
                return self.match_points * other.played > other.match_points * self.played
            return self.coopertition_points * other.played > other.coopertition_points * self.played
        return self.ranking_points * other.played > other.ranking_points * self.played


class Rankings(list[Ranking]):
    def len(self) -> int:
        return len(self)

    def swap(self, i, j):
        self[i], self[j] = self[j], self[i]
