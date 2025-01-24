import unittest
from datetime import timedelta

from .score_elements import BranchLevel, ScoreElements

match_start_time = timedelta()


def time_after_start(sec: float) -> timedelta:
    return match_start_time + timedelta(seconds=sec)


class AmpSpeakerTest(unittest.TestCase):
    def test_calculation_methods(self):
        score_elements = ScoreElements(
            auto_trough_coral=3,
            teleop_trough_coral=2,
            auto_processor_algae=1,
            teleop_processor_algae=2,
            auto_net_algae=3,
            teleop_net_algae=4,
        )
        self.assertEqual(5, score_elements.num_coral_each_level_scored(BranchLevel.LEVEL_TROUGH))
        self.assertEqual(5, score_elements.total_coral_scored())
        self.assertEqual(10, score_elements.total_algae_scored())
        self.assertEqual(46, score_elements.total_algae_points())
        self.assertEqual(13, score_elements.total_coral_points())

    def test_branches(self):
        score_elements = ScoreElements(
            branches=[
                [False, False, False],
                [True, False, False],
                [False, True, False],
                [False, False, True],
                [False, True, True],
                [True, False, True],
                [True, True, False],
                [False, False, False],
                [True, True, True],
                [False, False, True],
                [False, True, False],
                [True, False, False],
            ],
        )
        self.assertEqual(score_elements.total_coral_scored(), 15)
        self.assertEqual(score_elements.total_coral_points(), 60)
        self.assertEqual(score_elements.total_algae_scored(), 0)

        score_elements.auto_scoring = [
            [False, False, False],
            [False, False, False],
            [False, True, False],
            [False, False, False],
            [False, True, True],
            [False, False, False],
            [False, False, False],
            [False, False, False],
            [True, True, True],
            [True, True, True],
            [False, False, False],
            [True, False, False],
        ]
        self.assertEqual(score_elements.total_coral_scored(), 15)
        self.assertEqual(score_elements.total_coral_points(), 74)
        self.assertEqual(score_elements.total_algae_scored(), 0)

        score_elements.branch_algaes = [
            [True, False],
            [False, False],
            [False, True],
            [False, False],
            [True, False],
            [False, False],
        ]
        self.assertEqual(score_elements.total_coral_scored(), 12)
        self.assertEqual(score_elements.total_coral_points(), 61)
        self.assertEqual(score_elements.total_algae_scored(), 0)
