import unittest
from datetime import datetime, timedelta

import game
import models
from models.base import db

from .playoff_tournament import PlayoffTournament
from .specs import PlayoffMatchResult
from .test_helper import assert_break, assert_match, create_test_alliance


class PlayoffTournamentTest(unittest.TestCase):
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

    def test_new_playoff_tournament_errors(self):
        with self.assertRaises(ValueError):
            PlayoffTournament(5, 8)

    def test_playoff_tournament_getters(self):
        playoff_tournament = PlayoffTournament(models.PlayoffType.SINGLE_ELIMINATION, 2)
        self.assertEqual(len(playoff_tournament.MatchGroups()), 1)
        self.assertIn('F', playoff_tournament.MatchGroups())
        self.assertEqual(playoff_tournament.FinalMatchup(), playoff_tournament.MatchGroups()['F'])
        self.assertFalse(playoff_tournament.is_complete())
        self.assertEqual(playoff_tournament.winning_alliance_id(), 0)
        self.assertEqual(playoff_tournament.finalist_alliance_id(), 0)

        playoff_tournament.FinalMatchup().update(
            {
                43: PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH),
                44: PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH),
            }
        )
        self.assertTrue(playoff_tournament.is_complete())
        self.assertEqual(playoff_tournament.winning_alliance_id(), 2)
        self.assertEqual(playoff_tournament.finalist_alliance_id(), 1)

    def test_playoff_tournament_matches_and_breaks(self):
        create_test_alliance(8)

        playoff_tournament = PlayoffTournament(models.PlayoffType.DOUBLE_ELIMINATION, 8)
        start_time = datetime.fromtimestamp(5000)
        playoff_tournament.create_match_and_breaks(start_time)
        with self.assertRaises(ValueError):
            playoff_tournament.create_match_and_breaks(start_time + timedelta(hours=1))

        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(len(matches), 19)
        assert_match(
            self,
            matches[0],
            1,
            5000,
            'Match 1',
            'M1',
            'Round 1 Upper',
            'M1',
            1,
            8,
            True,
            'sf',
            1,
            1,
        )
        assert_match(
            self,
            matches[1],
            2,
            5540,
            'Match 2',
            'M2',
            'Round 1 Upper',
            'M2',
            4,
            5,
            True,
            'sf',
            2,
            1,
        )
        assert_match(
            self,
            matches[2],
            3,
            6080,
            'Match 3',
            'M3',
            'Round 1 Upper',
            'M3',
            2,
            7,
            True,
            'sf',
            3,
            1,
        )
        assert_match(
            self,
            matches[3],
            4,
            6620,
            'Match 4',
            'M4',
            'Round 1 Upper',
            'M4',
            3,
            6,
            True,
            'sf',
            4,
            1,
        )
        assert_match(
            self,
            matches[4],
            5,
            7160,
            'Match 5',
            'M5',
            'Round 2 Lower',
            'M5',
            0,
            0,
            True,
            'sf',
            5,
            1,
        )
        assert_match(
            self,
            matches[5],
            6,
            7700,
            'Match 6',
            'M6',
            'Round 2 Lower',
            'M6',
            0,
            0,
            True,
            'sf',
            6,
            1,
        )
        assert_match(
            self,
            matches[6],
            7,
            8240,
            'Match 7',
            'M7',
            'Round 2 Upper',
            'M7',
            0,
            0,
            True,
            'sf',
            7,
            1,
        )
        assert_match(
            self,
            matches[7],
            8,
            8780,
            'Match 8',
            'M8',
            'Round 2 Upper',
            'M8',
            0,
            0,
            True,
            'sf',
            8,
            1,
        )
        assert_match(
            self,
            matches[8],
            9,
            9320,
            'Match 9',
            'M9',
            'Round 3 Lower',
            'M9',
            0,
            0,
            True,
            'sf',
            9,
            1,
        )
        assert_match(
            self,
            matches[9],
            10,
            9860,
            'Match 10',
            'M10',
            'Round 3 Lower',
            'M10',
            0,
            0,
            True,
            'sf',
            10,
            1,
        )
        assert_match(
            self,
            matches[10],
            11,
            10520,
            'Match 11',
            'M11',
            'Round 4 Upper',
            'M11',
            0,
            0,
            True,
            'sf',
            11,
            1,
        )
        assert_match(
            self,
            matches[11],
            12,
            11060,
            'Match 12',
            'M12',
            'Round 4 Lower',
            'M12',
            0,
            0,
            True,
            'sf',
            12,
            1,
        )
        assert_match(
            self,
            matches[12],
            13,
            12260,
            'Match 13',
            'M13',
            'Round 5 Lower',
            'M13',
            0,
            0,
            True,
            'sf',
            13,
            1,
        )
        assert_match(self, matches[13], 14, 13460, 'Final 1', 'F1', '', 'F', 0, 0, False, 'f', 1, 1)
        assert_match(self, matches[14], 15, 14660, 'Final 2', 'F2', '', 'F', 0, 0, False, 'f', 1, 2)
        assert_match(self, matches[15], 16, 15860, 'Final 3', 'F3', '', 'F', 0, 0, False, 'f', 1, 3)
        assert_match(
            self, matches[16], 17, 16160, 'Overtime 1', 'O1', '', 'F', 0, 0, True, 'f', 1, 4
        )
        assert_match(
            self, matches[17], 18, 16760, 'Overtime 2', 'O2', '', 'F', 0, 0, True, 'f', 1, 5
        )
        assert_match(
            self, matches[18], 19, 17360, 'Overtime 3', 'O3', '', 'F', 0, 0, True, 'f', 1, 6
        )

        for i in range(16):
            self.assertEqual(matches[i].status, game.MatchStatus.MATCH_SCHEDULE)
        for i in range(17, 19):
            self.assertEqual(matches[i].status, game.MatchStatus.MATCH_HIDDEN)

        scheduled_breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
        self.assertEqual(len(scheduled_breaks), 5)
        assert_break(self, scheduled_breaks[0], 11, 10160, 360, 'Field Break')
        assert_break(self, scheduled_breaks[1], 13, 11360, 900, 'Award Break')
        assert_break(self, scheduled_breaks[2], 14, 12560, 900, 'Award Break')
        assert_break(self, scheduled_breaks[3], 15, 13760, 900, 'Award Break')
        assert_break(self, scheduled_breaks[4], 16, 14960, 900, 'Award Break')

        models.truncate_matches()
        models.truncate_scheduled_breaks()
        playoff_tournament = PlayoffTournament(models.PlayoffType.SINGLE_ELIMINATION, 3)
        start_time = datetime.fromtimestamp(1000)
        playoff_tournament.create_match_and_breaks(start_time)
        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(len(matches), 9)
        assert_match(
            self, matches[0], 38, 1000, 'Semifinal 2-1', 'SF2-1', '', 'SF2', 2, 3, True, 'sf', 2, 1
        )
        assert_match(
            self, matches[1], 40, 1600, 'Semifinal 2-2', 'SF2-2', '', 'SF2', 2, 3, True, 'sf', 2, 2
        )
        assert_match(
            self, matches[2], 42, 2200, 'Semifinal 2-3', 'SF2-3', '', 'SF2', 2, 3, True, 'sf', 2, 3
        )
        assert_match(self, matches[3], 43, 3280, 'Final 1', 'F1', '', 'F', 1, 0, False, 'f', 1, 1)
        assert_match(self, matches[4], 44, 4060, 'Final 2', 'F2', '', 'F', 1, 0, False, 'f', 1, 2)
        assert_match(self, matches[5], 45, 4840, 'Final 3', 'F3', '', 'F', 1, 0, False, 'f', 1, 3)
        assert_match(self, matches[6], 46, 5140, 'Overtime 1', 'O1', '', 'F', 1, 0, True, 'f', 1, 4)
        assert_match(self, matches[7], 47, 5740, 'Overtime 2', 'O2', '', 'F', 1, 0, True, 'f', 1, 5)
        assert_match(self, matches[8], 48, 6340, 'Overtime 3', 'O3', '', 'F', 1, 0, True, 'f', 1, 6)

        for i in range(6):
            self.assertEqual(matches[i].status, game.MatchStatus.MATCH_SCHEDULE)
        for i in range(6, 9):
            self.assertEqual(matches[i].status, game.MatchStatus.MATCH_HIDDEN)

        scheduled_breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
        self.assertEqual(len(scheduled_breaks), 3)
        assert_break(self, scheduled_breaks[0], 43, 2800, 480, 'Field Break')
        assert_break(self, scheduled_breaks[1], 44, 3580, 480, 'Field Break')
        assert_break(self, scheduled_breaks[2], 45, 4360, 480, 'Field Break')

    def test_playoff_tournament_update_matches(self):
        create_test_alliance(4)

        playoff_tournament = PlayoffTournament(models.PlayoffType.SINGLE_ELIMINATION, 4)
        self.assertRaises(ValueError, playoff_tournament.update_matches)

        playoff_tournament.create_match_and_breaks(datetime.fromtimestamp(0))

        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(matches[0].red1, 102)
        self.assertEqual(matches[0].red2, 101)
        self.assertEqual(matches[0].red3, 103)
        self.assertEqual(matches[0].blue1, 402)
        self.assertEqual(matches[0].blue2, 401)
        self.assertEqual(matches[0].blue3, 403)

        matches[0].status = game.MatchStatus.BLUE_WON_MATCH
        models.update_match(matches[0])
        models.update_alliance_from_match(1, [103, 102, 101])
        models.update_alliance_from_match(4, [404, 405, 406])

        playoff_tournament.update_matches()

        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(matches[0].red1, 102)
        self.assertEqual(matches[0].red2, 101)
        self.assertEqual(matches[0].red3, 103)
        self.assertEqual(matches[0].blue1, 402)
        self.assertEqual(matches[0].blue2, 401)
        self.assertEqual(matches[0].blue3, 403)
        self.assertEqual(matches[2].status, game.MatchStatus.MATCH_SCHEDULE)
        self.assertEqual(matches[2].red1, 103)
        self.assertEqual(matches[2].red2, 102)
        self.assertEqual(matches[2].red3, 101)
        self.assertEqual(matches[2].blue1, 404)
        self.assertEqual(matches[2].blue2, 405)
        self.assertEqual(matches[2].blue3, 406)
        self.assertEqual(matches[4].status, game.MatchStatus.MATCH_SCHEDULE)
        self.assertEqual(matches[4].red1, 103)
        self.assertEqual(matches[4].red2, 102)
        self.assertEqual(matches[4].red3, 101)
        self.assertEqual(matches[4].blue1, 404)
        self.assertEqual(matches[4].blue2, 405)
        self.assertEqual(matches[4].blue3, 406)

        matches[1].status = game.MatchStatus.BLUE_WON_MATCH
        models.update_match(matches[1])
        matches[2].status = game.MatchStatus.BLUE_WON_MATCH
        models.update_match(matches[2])
        matches[3].status = game.MatchStatus.BLUE_WON_MATCH
        models.update_match(matches[3])
        models.update_alliance_from_match(4, [403, 402, 406])

        playoff_tournament.update_matches()

        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(matches[2].red1, 103)
        self.assertEqual(matches[2].red2, 102)
        self.assertEqual(matches[2].red3, 101)
        self.assertEqual(matches[2].blue1, 404)
        self.assertEqual(matches[2].blue2, 405)
        self.assertEqual(matches[2].blue3, 406)
        self.assertEqual(matches[4].status, game.MatchStatus.MATCH_HIDDEN)
        self.assertEqual(matches[5].status, game.MatchStatus.MATCH_HIDDEN)
        self.assertEqual(matches[6].playoff_red_alliance, 4)
        self.assertEqual(matches[6].playoff_blue_alliance, 3)
        self.assertEqual(matches[6].red1, 403)
        self.assertEqual(matches[6].red2, 402)
        self.assertEqual(matches[6].red3, 406)
        self.assertEqual(matches[6].blue1, 302)
        self.assertEqual(matches[6].blue2, 301)
        self.assertEqual(matches[6].blue3, 303)

        matches[1].status = game.MatchStatus.RED_WON_MATCH
        models.update_match(matches[1])
        matches[2].status = game.MatchStatus.RED_WON_MATCH
        models.update_match(matches[2])

        playoff_tournament.update_matches()

        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        self.assertEqual(matches[4].status, game.MatchStatus.MATCH_SCHEDULE)
        self.assertEqual(matches[5].status, game.MatchStatus.MATCH_SCHEDULE)
        self.assertEqual(matches[6].playoff_red_alliance, 0)
        self.assertEqual(matches[6].playoff_blue_alliance, 0)
        self.assertEqual(matches[6].red1, 0)
        self.assertEqual(matches[6].red2, 0)
        self.assertEqual(matches[6].red3, 0)
        self.assertEqual(matches[6].blue1, 0)
        self.assertEqual(matches[6].blue2, 0)
        self.assertEqual(matches[6].blue3, 0)
