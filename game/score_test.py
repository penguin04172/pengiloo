import unittest

from .amp_speaker import AmpSpeaker
from .foul import Foul
from .score import *


class ScoreTest(unittest.TestCase):
    def test_score_summary(self):
        game_specific.melody_bouns_threshold_without_coop = 18
        game_specific.melody_bonus_threshold_with_coop = 15
        red_score = self.score_1()
        blue_score = self.score_2()

        red_summary = red_score.summarize(blue_score)
        self.assertEqual(4, red_summary.leave_points)
        self.assertEqual(36, red_summary.auto_points)
        self.assertEqual(6, red_summary.amp_points)
        self.assertEqual(57, red_summary.speaker_points)
        self.assertEqual(14, red_summary.stage_points)
        self.assertEqual(81, red_summary.match_points)
        self.assertEqual(0, red_summary.foul_points)
        self.assertEqual(81, red_summary.score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(17, red_summary.num_notes)
        self.assertEqual(18, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, red_summary.ensemble_bonus_ranking_point)
        self.assertEqual(0, red_summary.bonus_ranking_points)
        self.assertEqual(0, red_summary.num_opponent_tech_fouls)

        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(2, blue_summary.leave_points)
        self.assertEqual(42, blue_summary.auto_points)
        self.assertEqual(51, blue_summary.amp_points)
        self.assertEqual(161, blue_summary.speaker_points)
        self.assertEqual(13, blue_summary.stage_points)
        self.assertEqual(227, blue_summary.match_points)
        self.assertEqual(29, blue_summary.foul_points)
        self.assertEqual(256, blue_summary.score)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(85, blue_summary.num_notes)
        self.assertEqual(18, blue_summary.num_notes_goal)
        self.assertEqual(True, blue_summary.melody_bonus_ranking_point)
        self.assertEqual(True, blue_summary.ensemble_bonus_ranking_point)
        self.assertEqual(2, blue_summary.bonus_ranking_points)
        self.assertEqual(5, blue_summary.num_opponent_tech_fouls)

        # Unsetting team and rule_id don't invalidate fouls
        red_score.fouls[0].team_id = 0
        red_score.fouls[0].rule_id = 0
        self.assertEqual(29, blue_score.summarize(red_score).foul_points)

        # Test playoff_dq
        red_score.playoff_dq = True
        self.assertEqual(0, red_score.summarize(blue_score).score)
        self.assertNotEqual(0, blue_score.summarize(red_score).score)

        blue_score.playoff_dq = True
        self.assertEqual(0, blue_score.summarize(red_score).score)

    def test_melody_bonus_ranking_point(self):
        red_score = self.score_1()
        blue_score = self.score_2()

        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(17, red_summary.num_notes)
        self.assertEqual(18, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(85, blue_summary.num_notes)
        self.assertEqual(18, blue_summary.num_notes_goal)
        self.assertEqual(True, blue_summary.melody_bonus_ranking_point)

        # Reduce blue notes to 18 and verify that the bonus is still awarded
        blue_score.amp_speaker.teleop_amp_notes = 2
        blue_score.amp_speaker.teleop_amplified_speaker_notes = 5
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(17, red_summary.num_notes)
        self.assertEqual(18, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(18, blue_summary.num_notes)
        self.assertEqual(18, blue_summary.num_notes_goal)
        self.assertEqual(True, blue_summary.melody_bonus_ranking_point)

        # Increase non-coopertition threshold above the blue note count
        game_specific.melody_bouns_threshold_without_coop = 19
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(17, red_summary.num_notes)
        self.assertEqual(19, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(18, blue_summary.num_notes)
        self.assertEqual(19, blue_summary.num_notes_goal)
        self.assertEqual(False, blue_summary.melody_bonus_ranking_point)

        # Reduce red notes to the non-coopertition threshold
        game_specific.melody_bonus_threshold_with_coop = 16
        red_score.amp_speaker.teleop_amp_notes = 3
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(16, red_summary.num_notes)
        self.assertEqual(19, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(18, blue_summary.num_notes)
        self.assertEqual(19, blue_summary.num_notes_goal)
        self.assertEqual(False, blue_summary.melody_bonus_ranking_point)

        # Make blue fulfill the coopertition bonus requirement
        blue_score.amp_speaker.coop_activated = True
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(True, red_summary.coopertition_bonus)
        self.assertEqual(16, red_summary.num_notes)
        self.assertEqual(16, red_summary.num_notes_goal)
        self.assertEqual(True, red_summary.melody_bonus_ranking_point)
        self.assertEqual(True, blue_summary.coopertition_criteria_met)
        self.assertEqual(True, blue_summary.coopertition_bonus)
        self.assertEqual(18, blue_summary.num_notes)
        self.assertEqual(16, blue_summary.num_notes_goal)
        self.assertEqual(True, blue_summary.melody_bonus_ranking_point)

        # Disable the coopertition bonus
        game_specific.melody_bonus_threshold_with_coop = 0
        blue_score.amp_speaker.auto_speaker_notes = 9
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(False, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual(16, red_summary.num_notes)
        self.assertEqual(19, red_summary.num_notes_goal)
        self.assertEqual(False, red_summary.melody_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual(19, blue_summary.num_notes)
        self.assertEqual(19, blue_summary.num_notes_goal)
        self.assertEqual(True, blue_summary.melody_bonus_ranking_point)

    def test_score_ensemble_bonus_ranking_point(self):
        score = Score()

        score.endgame_statuses = [ENDGAME_STATUS.none, ENDGAME_STATUS.none, ENDGAME_STATUS.none]
        score.microphone_statuses = [False, False, False]
        score.trap_statuses = [False, False, False]
        self.assertEqual(False, score.summarize(Score()).ensemble_bonus_ranking_point)

        score.endgame_statuses = [
            ENDGAME_STATUS.stage_left,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_right,
        ]
        self.assertEqual(False, score.summarize(Score()).ensemble_bonus_ranking_point)

        # Try various combinations of Harmony
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_left,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_left,
        ]
        self.assertEqual(11, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_left,
        ]
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_right,
        ]
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_right,
            ENDGAME_STATUS.stage_right,
            ENDGAME_STATUS.stage_center,
        ]
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_center,
        ]
        self.assertEqual(13, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)

        # Try various combinations with microphones
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_left,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_right,
        ]
        score.microphone_statuses = [True, False, False]
        self.assertEqual(10, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.microphone_statuses = [True, True, True]
        self.assertEqual(12, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.none,
            ENDGAME_STATUS.stage_right,
            ENDGAME_STATUS.stage_right,
        ]
        score.microphone_statuses = [False, False, True]
        self.assertEqual(10, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.park,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.stage_right,
        ]
        score.microphone_statuses = [False, True, False]
        self.assertEqual(8, score.summarize(Score()).stage_points)
        self.assertEqual(False, score.summarize(Score()).ensemble_bonus_ranking_point)

        # Try various combinations with traps
        score.microphone_statuses = [False, False, False]
        score.endgame_statuses = [
            ENDGAME_STATUS.stage_left,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.park,
        ]
        score.trap_statuses = [False, False, True]
        self.assertEqual(12, score.summarize(Score()).stage_points)
        self.assertEqual(True, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [
            ENDGAME_STATUS.park,
            ENDGAME_STATUS.stage_center,
            ENDGAME_STATUS.park,
        ]
        score.trap_statuses = [True, True, True]
        self.assertEqual(20, score.summarize(Score()).stage_points)
        self.assertEqual(False, score.summarize(Score()).ensemble_bonus_ranking_point)
        score.endgame_statuses = [ENDGAME_STATUS.park, ENDGAME_STATUS.park, ENDGAME_STATUS.park]
        self.assertEqual(18, score.summarize(Score()).stage_points)
        self.assertEqual(False, score.summarize(Score()).ensemble_bonus_ranking_point)

    def test_score_free_ensemble_bonus_ranking_point_from_foul(self):
        score_1 = Score()
        score_2 = Score()
        foul = Foul(is_technical=True, rule_id=29)

        self.assertEqual(True, foul.rule().is_technical)
        self.assertEqual(True, foul.rule().is_ranking_point)
        score_2.fouls = [foul]

        summary = score_1.summarize(score_2)
        self.assertEqual(5, summary.score)
        self.assertEqual(True, summary.ensemble_bonus_ranking_point)
        self.assertEqual(1, summary.bonus_ranking_points)

        summary = score_2.summarize(score_1)
        self.assertEqual(0, summary.score)
        self.assertEqual(False, summary.ensemble_bonus_ranking_point)
        self.assertEqual(0, summary.bonus_ranking_points)

    def test_score_equals(self):
        score_1 = self.score_1()
        score_2 = self.score_1()
        self.assertTrue(score_1.equals(score_2))
        self.assertTrue(score_2.equals(score_1))

        score_3 = self.score_2()
        self.assertFalse(score_1.equals(score_3))
        self.assertFalse(score_3.equals(score_1))

        score_2 = self.score_1()
        score_2.leave_statuses[0] = False
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.amp_speaker.auto_amp_notes = 5
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.endgame_statuses[1] = ENDGAME_STATUS.park
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.microphone_statuses[0] = True
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.trap_statuses[0] = False
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.fouls[0].is_technical = False
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.fouls[0].team_id += 1
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.fouls[0].rule_id = 1
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))

        score_2 = self.score_1()
        score_2.playoff_dq = not score_2.playoff_dq
        self.assertFalse(score_1.equals(score_2))
        self.assertFalse(score_2.equals(score_1))
