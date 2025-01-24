import unittest

from .foul import Foul
from .game_specific import specific
from .score import CageStatus, EndgameStatus, Score
from .test_helper import score_1, score_2


class ScoreTest(unittest.TestCase):
    def test_score_summary(self):
        specific.coral_bonus_level_threshold_without_coop = 4
        specific.coral_bonus_level_threshold_with_coop = 3
        red_score = score_1()
        blue_score = score_2()

        red_summary = red_score.summarize(blue_score)
        self.assertEqual(6, red_summary.leave_points)
        self.assertEqual(20, red_summary.auto_points)
        self.assertEqual(39, red_summary.coral_points)
        self.assertEqual(20, red_summary.algae_points)
        self.assertEqual(8, red_summary.barge_points)
        self.assertEqual(73, red_summary.match_points)
        self.assertEqual(0, red_summary.foul_points)
        self.assertEqual(73, red_summary.score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual([2, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(4, red_summary.num_coral_levels_goal)
        self.assertEqual(False, red_summary.auto_bonus_ranking_point)
        self.assertEqual(False, red_summary.coral_bonus_ranking_point)
        self.assertEqual(False, red_summary.barge_bonus_ranking_point)
        self.assertEqual(0, red_summary.bonus_ranking_points)
        self.assertEqual(0, red_summary.num_opponent_major_fouls)

        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(6, blue_summary.leave_points)
        self.assertEqual(29, blue_summary.auto_points)
        self.assertEqual(77, blue_summary.coral_points)
        self.assertEqual(0, blue_summary.algae_points)
        self.assertEqual(14, blue_summary.barge_points)
        self.assertEqual(97, blue_summary.match_points)
        self.assertEqual(34, blue_summary.foul_points)
        self.assertEqual(131, blue_summary.score)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(4, blue_summary.num_coral_levels_goal)
        self.assertEqual(True, blue_summary.auto_bonus_ranking_point)
        self.assertEqual(True, blue_summary.coral_bonus_ranking_point)
        self.assertEqual(True, blue_summary.barge_bonus_ranking_point)
        self.assertEqual(3, blue_summary.bonus_ranking_points)
        self.assertEqual(5, blue_summary.num_opponent_major_fouls)

        # Unsetting team and rule_id don't invalidate fouls
        red_score.fouls[0].team_id = 0
        red_score.fouls[0].rule_id = 0
        self.assertEqual(34, blue_score.summarize(red_score).foul_points)

        # Test playoff_dq
        red_score.playoff_dq = True
        self.assertEqual(0, red_score.summarize(blue_score).score)
        self.assertNotEqual(0, blue_score.summarize(red_score).score)

        blue_score.playoff_dq = True
        self.assertEqual(0, blue_score.summarize(red_score).score)

    def test_coral_bonus_ranking_point(self):
        red_score = score_1()
        blue_score = score_2()

        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual([2, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(4, red_summary.num_coral_levels_goal)
        self.assertEqual(False, red_summary.coral_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(4, blue_summary.num_coral_levels_goal)
        self.assertEqual(True, blue_summary.coral_bonus_ranking_point)

        # Increase non-coopertition threshold above the blue coral levels count
        specific.coral_bonus_level_threshold_without_coop = 5
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual([2, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(5, red_summary.num_coral_levels_goal)
        self.assertEqual(False, red_summary.coral_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(5, blue_summary.num_coral_levels_goal)
        self.assertEqual(False, blue_summary.coral_bonus_ranking_point)

        # Reduce red processor algae to the non-coopertition threshold
        specific.coral_bonus_level_threshold_with_coop = 3
        red_score.score_elements.teleop_processor_algae = 0
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(False, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual([2, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(5, red_summary.num_coral_levels_goal)
        self.assertEqual(False, red_summary.coral_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(5, blue_summary.num_coral_levels_goal)
        self.assertEqual(False, blue_summary.coral_bonus_ranking_point)

        # Make blue fulfill the coopertition bonus requirement
        red_score.score_elements.teleop_processor_algae = 1
        red_score.score_elements.teleop_trough_coral = 5
        blue_score.score_elements.teleop_processor_algae = 2
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(True, red_summary.coopertition_criteria_met)
        self.assertEqual(True, red_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(3, red_summary.num_coral_levels_goal)
        self.assertEqual(True, red_summary.coral_bonus_ranking_point)
        self.assertEqual(True, blue_summary.coopertition_criteria_met)
        self.assertEqual(True, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(3, blue_summary.num_coral_levels_goal)
        self.assertEqual(True, blue_summary.coral_bonus_ranking_point)

        # Disable the coopertition bonus
        specific.coral_bonus_level_threshold_with_coop = 0
        specific.coral_bonus_level_threshold_without_coop = 4
        red_summary = red_score.summarize(blue_score)
        blue_summary = blue_score.summarize(red_score)
        self.assertEqual(False, red_summary.coopertition_criteria_met)
        self.assertEqual(False, red_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 0], red_summary.num_coral_each_level)
        self.assertEqual(4, red_summary.num_coral_levels_goal)
        self.assertEqual(False, red_summary.coral_bonus_ranking_point)
        self.assertEqual(False, blue_summary.coopertition_criteria_met)
        self.assertEqual(False, blue_summary.coopertition_bonus)
        self.assertEqual([5, 5, 5, 5], blue_summary.num_coral_each_level)
        self.assertEqual(4, blue_summary.num_coral_levels_goal)
        self.assertEqual(True, blue_summary.coral_bonus_ranking_point)

    def test_score_barge_bonus_ranking_point(self):
        score = Score()

        score.endgame_statuses = [EndgameStatus.NONE, EndgameStatus.NONE, EndgameStatus.NONE]
        score.cage_statuses = [CageStatus.SHALLOW, CageStatus.DEEP, CageStatus.SHALLOW]
        self.assertEqual(False, score.summarize(Score()).barge_bonus_ranking_point)

        score.endgame_statuses = [
            EndgameStatus.CAGE_LEFT,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_RIGHT,
        ]
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)

        # Try various combinations of BARGE
        score.endgame_statuses = [
            EndgameStatus.CAGE_LEFT,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_LEFT,
        ]
        self.assertEqual(24, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_LEFT,
        ]
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_RIGHT,
        ]
        self.assertEqual(30, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.CAGE_RIGHT,
            EndgameStatus.CAGE_RIGHT,
            EndgameStatus.CAGE_CENTER,
        ]
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.CAGE_CENTER,
        ]
        self.assertEqual(36, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.NONE,
            EndgameStatus.PARK,
            EndgameStatus.CAGE_RIGHT,
        ]
        self.assertEqual(8, score.summarize(Score()).barge_points)
        self.assertEqual(False, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.NONE,
            EndgameStatus.CAGE_RIGHT,
            EndgameStatus.CAGE_RIGHT,
        ]
        self.assertEqual(12, score.summarize(Score()).barge_points)
        self.assertEqual(False, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.PARK,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.NONE,
        ]
        self.assertEqual(14, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.CAGE_RIGHT,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.PARK,
        ]
        self.assertEqual(20, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [
            EndgameStatus.PARK,
            EndgameStatus.CAGE_CENTER,
            EndgameStatus.PARK,
        ]
        self.assertEqual(16, score.summarize(Score()).barge_points)
        self.assertEqual(True, score.summarize(Score()).barge_bonus_ranking_point)
        score.endgame_statuses = [EndgameStatus.PARK, EndgameStatus.PARK, EndgameStatus.PARK]
        self.assertEqual(6, score.summarize(Score()).barge_points)
        self.assertEqual(False, score.summarize(Score()).barge_bonus_ranking_point)

    def test_score_free_barge_bonus_ranking_point_from_foul(self):
        score_1 = Score()
        score_2 = Score()
        foul = Foul(is_major=True, rule_id=29)

        self.assertEqual(True, foul.rule().is_major)
        self.assertEqual(True, foul.rule().is_ranking_point)
        score_2.fouls = [foul]

        summary = score_1.summarize(score_2)
        self.assertEqual(6, summary.score)
        self.assertEqual(True, summary.barge_bonus_ranking_point)
        self.assertEqual(1, summary.bonus_ranking_points)

        summary = score_2.summarize(score_1)
        self.assertEqual(0, summary.score)
        self.assertEqual(False, summary.barge_bonus_ranking_point)
        self.assertEqual(0, summary.bonus_ranking_points)

    def test_score_equals(self):
        s_1 = score_1()
        s_2 = score_1()
        self.assertTrue(s_1.equals(s_2))
        self.assertTrue(s_2.equals(s_1))

        s_3 = score_2()
        self.assertFalse(s_1.equals(s_3))
        self.assertFalse(s_3.equals(s_1))

        s_2 = score_1()
        s_2.leave_statuses[0] = False
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.score_elements.teleop_trough_coral = 5
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.endgame_statuses[1] = EndgameStatus.PARK
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.fouls[0].is_major = False
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.fouls[0].team_id += 1
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.fouls[0].rule_id = 1
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))

        s_2 = score_1()
        s_2.playoff_dq = not s_2.playoff_dq
        self.assertFalse(s_1.equals(s_2))
        self.assertFalse(s_2.equals(s_1))
