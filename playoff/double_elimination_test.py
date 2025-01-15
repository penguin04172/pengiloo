import unittest

import game
import models

from .double_elimination import new_double_elimination_bracket
from .match_group import MatchSpec, collect_match_groups, collect_match_specs
from .playoff_tournament import PlayoffTournament
from .specs import PlayoffMatchResult
from .test_helper import (
    ExpectedAlliance,
    assertMatchGroups,
    assertMatchOutcome,
    assertMatchSpecAlliances,
    assertMatchSpecsEqual,
)


class TestDoubleElimination(unittest.TestCase):
    def test_double_elimination_initial(self):
        try:
            final_matchup, _ = new_double_elimination_bracket(8)
        except Exception as e:
            self.fail(f'Unexpected exception: {e}')

        match_specs = collect_match_specs(final_matchup)
        self.assertEqual(len(match_specs), 19)
        assertMatchSpecsEqual(
            self,
            match_specs,
            [
                MatchSpec(
                    long_name='Match 1',
                    short_name='M1',
                    name_detail='Round 1 Upper',
                    match_group_id='M1',
                    order=1,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=1, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 2',
                    short_name='M2',
                    name_detail='Round 1 Upper',
                    match_group_id='M2',
                    order=2,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 3',
                    short_name='M3',
                    name_detail='Round 1 Upper',
                    match_group_id='M3',
                    order=3,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 4',
                    short_name='M4',
                    name_detail='Round 1 Upper',
                    match_group_id='M4',
                    order=4,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 5',
                    short_name='M5',
                    name_detail='Round 2 Lower',
                    match_group_id='M5',
                    order=5,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=5, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 6',
                    short_name='M6',
                    name_detail='Round 2 Lower',
                    match_group_id='M6',
                    order=6,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 7',
                    short_name='M7',
                    name_detail='Round 2 Upper',
                    match_group_id='M7',
                    order=7,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=7, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 8',
                    short_name='M8',
                    name_detail='Round 2 Upper',
                    match_group_id='M8',
                    order=8,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 9',
                    short_name='M9',
                    name_detail='Round 3 Lower',
                    match_group_id='M9',
                    order=9,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=9, match_number=1),
                ),
                MatchSpec(
                    long_name='Match 10',
                    short_name='M10',
                    name_detail='Round 3 Lower',
                    match_group_id='M10',
                    order=10,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(
                        comp_level='sf', set_number=10, match_number=1
                    ),
                ),
                MatchSpec(
                    long_name='Match 11',
                    short_name='M11',
                    name_detail='Round 4 Upper',
                    match_group_id='M11',
                    order=11,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(
                        comp_level='sf', set_number=11, match_number=1
                    ),
                ),
                MatchSpec(
                    long_name='Match 12',
                    short_name='M12',
                    name_detail='Round 4 Lower',
                    match_group_id='M12',
                    order=12,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(
                        comp_level='sf', set_number=12, match_number=1
                    ),
                ),
                MatchSpec(
                    long_name='Match 13',
                    short_name='M13',
                    name_detail='Round 5 Lower',
                    match_group_id='M13',
                    order=13,
                    duration_sec=540,
                    use_tiebreak_criteria=True,
                    tba_match_key=models.TbaMatchKey(
                        comp_level='sf', set_number=13, match_number=1
                    ),
                ),
                MatchSpec(
                    long_name='Final 1',
                    short_name='F1',
                    name_detail='',
                    match_group_id='F',
                    order=14,
                    duration_sec=540,
                    use_tiebreak_criteria=False,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=1),
                ),
                MatchSpec(
                    long_name='Final 2',
                    short_name='F2',
                    name_detail='',
                    match_group_id='F',
                    order=15,
                    duration_sec=540,
                    use_tiebreak_criteria=False,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=2),
                ),
                MatchSpec(
                    long_name='Final 3',
                    short_name='F3',
                    name_detail='',
                    match_group_id='F',
                    order=16,
                    duration_sec=540,
                    use_tiebreak_criteria=False,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=3),
                ),
                MatchSpec(
                    long_name='Overtime 1',
                    short_name='O1',
                    name_detail='',
                    match_group_id='F',
                    order=17,
                    duration_sec=360,
                    use_tiebreak_criteria=True,
                    is_hidden=True,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=4),
                ),
                MatchSpec(
                    long_name='Overtime 2',
                    short_name='O2',
                    name_detail='',
                    match_group_id='F',
                    order=18,
                    duration_sec=360,
                    use_tiebreak_criteria=True,
                    is_hidden=True,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=5),
                ),
                MatchSpec(
                    long_name='Overtime 3',
                    short_name='O3',
                    name_detail='',
                    match_group_id='F',
                    order=19,
                    duration_sec=360,
                    use_tiebreak_criteria=True,
                    is_hidden=True,
                    tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=6),
                ),
            ],
        )

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:4],
            [
                ExpectedAlliance(1, 8),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
            ],
        )

        for i in range(4, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'F'],
        )

    def test_double_elimination_errors(self):
        self.assertRaises(ValueError, new_double_elimination_bracket, 7)
        self.assertRaises(ValueError, new_double_elimination_bracket, 9)

    def test_double_elimination_progression(self):
        try:
            playoff_tournament = PlayoffTournament(models.PLAYOFF_TYPE.double_elimination, 8)
        except Exception as e:
            self.fail(f'Unexpected exception: {e}')

        final_matchup = playoff_tournament.FinalMatchup()
        match_specs = playoff_tournament.match_specs
        match_groups = playoff_tournament.MatchGroups()
        playoff_match_results = dict[int, PlayoffMatchResult]()

        assertMatchOutcome(self, match_groups['M1'], '', '')

        playoff_match_results[1] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[4:7],
            [ExpectedAlliance(8, 0), ExpectedAlliance(0, 0), ExpectedAlliance(1, 0)],
        )

        for i in range(7, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        assertMatchOutcome(
            self,
            match_groups['M1'],
            'Advances to Match 7 - Round 2 Upper',
            'Advances to Match 5 - Round 2 Lower',
        )

        playoff_match_results[1] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[4:7],
            [ExpectedAlliance(1, 0), ExpectedAlliance(0, 0), ExpectedAlliance(8, 0)],
        )
        for i in range(7, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M1'],
            'Advances to Match 5 - Round 2 Lower',
            'Advances to Match 7 - Round 2 Upper',
        )

        playoff_match_results[2] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[4:7],
            [ExpectedAlliance(1, 5), ExpectedAlliance(0, 0), ExpectedAlliance(8, 4)],
        )
        for i in range(7, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M2'],
            'Advances to Match 7 - Round 2 Upper',
            'Advances to Match 5 - Round 2 Lower',
        )

        playoff_match_results[3] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[5:8],
            [ExpectedAlliance(2, 0), ExpectedAlliance(8, 4), ExpectedAlliance(7, 0)],
        )
        for i in range(8, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M3'],
            'Advances to Match 6 - Round 2 Lower',
            'Advances to Match 8 - Round 2 Upper',
        )

        playoff_match_results[4] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[5:8],
            [ExpectedAlliance(2, 6), ExpectedAlliance(8, 4), ExpectedAlliance(7, 3)],
        )
        for i in range(8, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        playoff_match_results[5] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[8:10],
            [ExpectedAlliance(0, 0), ExpectedAlliance(0, 5)],
        )
        for i in range(10, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M5'],
            'Eliminated',
            'Advances to Match 10 - Round 3 Lower',
        )

        playoff_match_results[6] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[8:10],
            [ExpectedAlliance(0, 2), ExpectedAlliance(0, 5)],
        )
        for i in range(10, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        playoff_match_results[7] = PlayoffMatchResult(status=game.MATCH_STATUS.tie_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[8:10],
            [ExpectedAlliance(0, 2), ExpectedAlliance(0, 5)],
        )
        for i in range(10, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        playoff_match_results[7] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[8:11],
            [ExpectedAlliance(8, 2), ExpectedAlliance(0, 5), ExpectedAlliance(4, 0)],
        )
        for i in range(11, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 0)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        playoff_match_results[8] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[8:11],
            [ExpectedAlliance(8, 2), ExpectedAlliance(7, 5), ExpectedAlliance(4, 3)],
        )

        playoff_match_results[9] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        playoff_match_results[10] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[11:12],
            [ExpectedAlliance(7, 8)],
        )

        playoff_match_results[11] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[12:13],
            [ExpectedAlliance(3, 0)],
        )
        final_matchup.update(playoff_match_results)
        for i in range(13, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 4)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M11'],
            'Advances to Final 1',
            'Advances to Match 13 - Round 5 Lower',
        )

        playoff_match_results[12] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[12:13],
            [ExpectedAlliance(3, 7)],
        )
        for i in range(13, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 4)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)

        playoff_match_results[13] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        for i in range(13, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 4)
            self.assertEqual(match_specs[i].blue_alliance_id, 3)
        assertMatchOutcome(
            self,
            match_groups['M13'],
            'Advances to Final 1',
            'Eliminated',
        )

        del playoff_match_results[13]
        final_matchup.update(playoff_match_results)
        assertMatchSpecAlliances(
            self,
            match_specs[12:13],
            [ExpectedAlliance(3, 7)],
        )
        for i in range(13, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 4)
            self.assertEqual(match_specs[i].blue_alliance_id, 0)
        assertMatchOutcome(
            self,
            match_groups['M13'],
            '',
            '',
        )

        playoff_match_results[13] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        for i in range(13, 19):
            self.assertEqual(match_specs[i].red_alliance_id, 4)
            self.assertEqual(match_specs[i].blue_alliance_id, 7)
        assertMatchOutcome(
            self,
            match_groups['M13'],
            'Eliminated',
            'Advances to Final 1',
        )

        playoff_match_results[14] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(
            self,
            match_groups['F'],
            '',
            '',
        )

        playoff_match_results[15] = PlayoffMatchResult(status=game.MATCH_STATUS.red_won_match)
        final_matchup.update(playoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(
            self,
            match_groups['F'],
            '',
            '',
        )

        playoff_match_results[16] = PlayoffMatchResult(status=game.MATCH_STATUS.tie_match)
        final_matchup.update(playoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(
            self,
            match_groups['F'],
            '',
            '',
        )

        playoff_match_results[17] = PlayoffMatchResult(status=game.MATCH_STATUS.tie_match)
        final_matchup.update(playoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(
            self,
            match_groups['F'],
            '',
            '',
        )

        playoff_match_results[18] = PlayoffMatchResult(status=game.MATCH_STATUS.blue_won_match)
        final_matchup.update(playoff_match_results)
        self.assertTrue(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 7)
        self.assertEqual(final_matchup.losing_alliance_id(), 4)
        assertMatchOutcome(
            self,
            match_groups['F'],
            'Tournament Finalist',
            'Tournament Winner',
        )
