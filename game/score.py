from enum import IntEnum

from pydantic import BaseModel

from .foul import Foul
from .game_specific import specific
from .score_elements import BranchLevel, ScoreElements
from .score_summary import ScoreSummary


class EndgameStatus(IntEnum):
    NONE = 0
    PARK = 1
    CAGE_LEFT = 2
    CAGE_CENTER = 3
    CAGE_RIGHT = 4


class CageStatus(IntEnum):
    SHALLOW = 0
    DEEP = 1


class CagePosition(IntEnum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


cage_points = {
    CageStatus.SHALLOW: 6,
    CageStatus.DEEP: 12,
}


class Score(BaseModel):
    leave_statuses: list[bool] = [False] * 3
    bypass_statuses: list[bool] = [False] * 3
    score_elements: ScoreElements = ScoreElements()
    cage_statuses: list[CageStatus] = [CageStatus.SHALLOW] * 3
    endgame_statuses: list[EndgameStatus] = [EndgameStatus.NONE] * 3
    fouls: list[Foul] = []
    playoff_dq: bool = False

    def summarize(self, opponent_score: 'Score') -> ScoreSummary:
        summary = ScoreSummary()

        if self.playoff_dq:
            return summary

        # Auto Points Summary
        summary.leave_points = self.leave_statuses.count(True) * 3
        auto_coral_points = self.score_elements.auto_coral_points()
        auto_algae_points = self.score_elements.auto_algae_points()
        summary.auto_points = summary.leave_points + auto_algae_points + auto_coral_points

        # Coral and Algae points
        summary.coral_points = self.score_elements.total_coral_points()
        summary.algae_points = self.score_elements.total_algae_points()

        # Endgame points
        for status in self.endgame_statuses:
            match status:
                case EndgameStatus.PARK:
                    summary.park_points += 2
                case EndgameStatus.CAGE_LEFT:
                    summary.cage_points += cage_points[self.cage_statuses[CagePosition.LEFT]]
                case EndgameStatus.CAGE_CENTER:
                    summary.cage_points += cage_points[self.cage_statuses[CagePosition.CENTER]]
                case EndgameStatus.CAGE_RIGHT:
                    summary.cage_points += cage_points[self.cage_statuses[CagePosition.RIGHT]]

        summary.barge_points = summary.park_points + summary.cage_points
        summary.match_points = (
            summary.leave_points
            + summary.coral_points
            + summary.algae_points
            + summary.barge_points
        )

        # Calculate penalty points
        for foul in opponent_score.fouls:
            summary.foul_points += foul.point_value()

            # Store techfoul count to break ties
            if foul.is_major:
                summary.num_opponent_major_fouls += 1

            rule = foul.rule()
            if rule is not None:
                summary.barge_bonus_ranking_point = rule.is_ranking_point

        summary.score = summary.match_points + summary.foul_points

        # Calculate bonus ranking points
        summary.auto_bonus_ranking_point = False
        if self.score_elements.auto_coral_points() >= specific.auto_bonus_coral_threshold:
            summary.auto_bonus_ranking_point = (
                True
                if self.leave_statuses.count(True) + self.bypass_statuses.count(True) == 3
                else False
            )

        summary.num_coral_each_level = [
            self.score_elements.num_coral_each_level_scored(level)
            for level in range(BranchLevel.COUNT)
        ]
        summary.num_coral_levels_goal = specific.coral_bonus_level_threshold_without_coop
        if specific.coral_bonus_level_threshold_with_coop > 0:
            summary.coopertition_criteria_met = (
                self.score_elements.num_processor_algae_scored()
                >= specific.coop_bonus_algae_threshold
            )
            summary.coopertition_bonus = summary.coopertition_criteria_met and (
                opponent_score.score_elements.num_processor_algae_scored()
                >= specific.coop_bonus_algae_threshold
            )
            if summary.coopertition_bonus:
                summary.num_coral_levels_goal = specific.coral_bonus_level_threshold_with_coop

        if (
            sum(
                1
                for num in summary.num_coral_each_level
                if num >= specific.coral_bonus_num_threshold
            )
            >= summary.num_coral_levels_goal
        ):
            summary.coral_bonus_ranking_point = True

        if summary.barge_points >= specific.barge_bonus_point_threshold:
            summary.barge_bonus_ranking_point = True

        if summary.auto_bonus_ranking_point:
            summary.bonus_ranking_points += 1

        if summary.coral_bonus_ranking_point:
            summary.bonus_ranking_points += 1

        if summary.barge_bonus_ranking_point:
            summary.bonus_ranking_points += 1

        return summary

    # Returns true if and only if all fields are equal
    def equals(self, other: 'Score') -> bool:
        if (
            self.leave_statuses != other.leave_statuses
            or self.score_elements != other.score_elements
            or self.endgame_statuses != other.endgame_statuses
            or self.playoff_dq != other.playoff_dq
            or len(self.fouls) != len(other.fouls)
        ):
            return False

        for i, foul in enumerate(self.fouls):
            if foul != other.fouls[i]:
                return False

        return True
