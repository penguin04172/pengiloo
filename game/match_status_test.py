import unittest

from .match_status import MatchStatus, ScoreSummary, determine_match_status


class MatchStatusTest(unittest.TestCase):
    def test_score_summary_determine_match_status(self):
        red_score_summary = ScoreSummary(score=10)
        blue_score_summary = ScoreSummary(score=10)
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.TIE_MATCH,
        )

        red_score_summary.score = 11
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.RED_WON_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.RED_WON_MATCH,
        )

        blue_score_summary.score = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.BLUE_WON_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.BLUE_WON_MATCH,
        )

        red_score_summary.score = 12
        red_score_summary.num_opponent_tech_fouls = 11
        red_score_summary.auto_points = 11
        red_score_summary.stage_points = 11

        blue_score_summary.num_opponent_tech_fouls = 10
        blue_score_summary.auto_points = 10
        blue_score_summary.stage_points = 10

        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.RED_WON_MATCH,
        )

        blue_score_summary.num_opponent_tech_fouls = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.BLUE_WON_MATCH,
        )

        red_score_summary.num_opponent_tech_fouls = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.RED_WON_MATCH,
        )

        blue_score_summary.auto_points = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.BLUE_WON_MATCH,
        )

        red_score_summary.auto_points = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.RED_WON_MATCH,
        )

        blue_score_summary.stage_points = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.BLUE_WON_MATCH,
        )

        red_score_summary.stage_points = 12
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, False),
            MatchStatus.TIE_MATCH,
        )
        self.assertEqual(
            determine_match_status(red_score_summary, blue_score_summary, True),
            MatchStatus.TIE_MATCH,
        )
