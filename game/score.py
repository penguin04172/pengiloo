from enum import IntEnum

from pydantic import BaseModel

from .amp_speaker import AmpSpeaker
from .foul import Foul
from .game_specific import game_specific
from .match_status import ScoreSummary


class ENDGAME_STATUS(IntEnum):
    none = 0
    park = 1
    stage_left = 2
    stage_center = 3
    stage_right = 4


class STAGE_POSITION(IntEnum):
    left = 0
    center = 1
    right = 2


class Score(BaseModel):
    leave_statuses: list[bool] = [False] * 3
    amp_speaker: AmpSpeaker = AmpSpeaker()
    endgame_statuses: list[ENDGAME_STATUS] = [ENDGAME_STATUS.none] * 3
    microphone_statuses: list[bool] = [False] * 3
    trap_statuses: list[bool] = [False] * 3
    fouls: list[Foul] = []
    playoff_dq: bool = False

    def summarize(self, opponent_score: 'Score') -> ScoreSummary:
        summary = ScoreSummary()

        if self.playoff_dq:
            return summary

        # Auto Points Summary
        summary.leave_points = self.leave_statuses.count(True) * 2
        auto_note_points = self.amp_speaker.auto_note_points()
        summary.auto_points = summary.leave_points + auto_note_points

        # Amp and Speaker points
        summary.amp_points = self.amp_speaker.amp_points()
        summary.speaker_points = self.amp_speaker.speaker_points()

        # Endgame points
        robots_by_position = {
            STAGE_POSITION.left: 0,
            STAGE_POSITION.center: 0,
            STAGE_POSITION.right: 0,
        }
        for status in self.endgame_statuses:
            match status:
                case ENDGAME_STATUS.park:
                    summary.park_points += 1
                case ENDGAME_STATUS.stage_left:
                    summary.onstage_points += 3
                    robots_by_position[STAGE_POSITION.left] += 1
                case ENDGAME_STATUS.stage_center:
                    summary.onstage_points += 3
                    robots_by_position[STAGE_POSITION.center] += 1
                case ENDGAME_STATUS.stage_right:
                    summary.onstage_points += 3
                    robots_by_position[STAGE_POSITION.right] += 1

        total_onstage_robots = 0
        for position, onstage_robots in robots_by_position.items():
            total_onstage_robots += onstage_robots
            if onstage_robots > 1:
                summary.harmony_points += 2 * (onstage_robots - 1)

            if self.microphone_statuses[position] and onstage_robots > 0:
                summary.spotlight_points += onstage_robots

            if self.trap_statuses[position]:
                summary.trap_points += 5

        summary.stage_points = (
            summary.park_points
            + summary.onstage_points
            + summary.harmony_points
            + summary.spotlight_points
            + summary.trap_points
        )
        summary.match_points = (
            summary.leave_points
            + summary.amp_points
            + summary.speaker_points
            + summary.stage_points
        )

        # Calculate penalty points
        for foul in opponent_score.fouls:
            summary.foul_points += foul.point_value()

            # Store techfoul count to break ties
            if foul.is_technical:
                summary.num_opponent_tech_fouls += 1

            rule = foul.rule()
            if rule is not None:
                summary.ensemble_bonus_ranking_point = rule.is_ranking_point

        summary.score = summary.match_points + summary.foul_points

        # Calculate bonus ranking points
        summary.num_notes = self.amp_speaker.total_notes_scored()
        summary.num_notes_goal = game_specific.melody_bouns_threshold_without_coop
        if game_specific.melody_bonus_threshold_with_coop > 0:
            summary.coopertition_criteria_met = self.amp_speaker.coop_activated
            summary.coopertition_bonus = (
                summary.coopertition_criteria_met and opponent_score.amp_speaker.coop_activated
            )
            if summary.coopertition_bonus:
                summary.num_notes_goal = game_specific.melody_bonus_threshold_with_coop

        if summary.num_notes >= summary.num_notes_goal:
            summary.melody_bonus_ranking_point = True

        if (
            summary.stage_points >= game_specific.ENSEMBLE_BONUS_POINT_THRESHOLD
            and total_onstage_robots >= game_specific.ENSEMBLE_BONUS_ROBOT_THRESHOLD
        ):
            summary.ensemble_bonus_ranking_point = True

        if summary.melody_bonus_ranking_point:
            summary.bonus_ranking_points += 1

        if summary.ensemble_bonus_ranking_point:
            summary.bonus_ranking_points += 1

        return summary

    # Returns true if and only if all fields are equal
    def equals(self, other: 'Score') -> bool:
        if (
            self.leave_statuses != other.leave_statuses
            or self.amp_speaker != other.amp_speaker
            or self.endgame_statuses != other.endgame_statuses
            or self.microphone_statuses != other.microphone_statuses
            or self.trap_statuses != other.trap_statuses
            or self.playoff_dq != other.playoff_dq
            or len(self.fouls) != len(other.fouls)
        ):
            return False

        for i, foul in enumerate(self.fouls):
            if foul != other.fouls[i]:
                return False

        return True
