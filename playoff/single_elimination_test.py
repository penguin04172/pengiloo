import unittest

import game
import models

from .match_group import MatchSpec, collect_match_groups, collect_match_specs
from .playoff_tournament import PlayoffTournament
from .single_elimination import new_single_elimination_bracket
from .specs import BreakSpec, PlayoffMatchResult
from .test_helper import (
    ExpectedAlliance,
    assertMatchGroups,
    assertMatchOutcome,
    assertMatchSpecAlliances,
    assertMatchSpecsEqual,
)


def assert_full_finals(self, match_specs, starting_index):
    self.assertEqual(len(match_specs), starting_index + 6)
    assertMatchSpecsEqual(
        self,
        match_specs[starting_index : starting_index + 6],
        [
            MatchSpec(
                long_name='Final 1',
                short_name='F1',
                name_detail='',
                order=43,
                match_group_id='F',
                use_tiebreak_criteria=False,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=1),
            ),
            MatchSpec(
                long_name='Final 2',
                short_name='F2',
                name_detail='',
                order=44,
                match_group_id='F',
                use_tiebreak_criteria=False,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=2),
            ),
            MatchSpec(
                long_name='Final 3',
                short_name='F3',
                name_detail='',
                order=45,
                match_group_id='F',
                use_tiebreak_criteria=False,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=3),
            ),
            MatchSpec(
                long_name='Overtime 1',
                short_name='O1',
                name_detail='',
                order=46,
                match_group_id='F',
                use_tiebreak_criteria=True,
                is_hidden=True,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=4),
            ),
            MatchSpec(
                long_name='Overtime 2',
                short_name='O2',
                name_detail='',
                order=47,
                match_group_id='F',
                use_tiebreak_criteria=True,
                is_hidden=True,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=5),
            ),
            MatchSpec(
                long_name='Overtime 3',
                short_name='O3',
                name_detail='',
                order=48,
                match_group_id='F',
                use_tiebreak_criteria=True,
                is_hidden=True,
                tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=6),
            ),
        ],
    )


def assert_full_semifinals_onward(self, match_specs, starting_index):
    self.assertEqual(len(match_specs), starting_index + 12)
    assertMatchSpecsEqual(
        self,
        match_specs[starting_index : starting_index + 6],
        [
            MatchSpec(
                long_name='Semifinal 1-1',
                short_name='SF1-1',
                name_detail='',
                order=37,
                match_group_id='SF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=1, match_number=1),
            ),
            MatchSpec(
                long_name='Semifinal 2-1',
                short_name='SF2-1',
                name_detail='',
                order=38,
                match_group_id='SF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=1),
            ),
            MatchSpec(
                long_name='Semifinal 1-2',
                short_name='SF1-2',
                name_detail='',
                order=39,
                match_group_id='SF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=1, match_number=2),
            ),
            MatchSpec(
                long_name='Semifinal 2-2',
                short_name='SF2-2',
                name_detail='',
                order=40,
                match_group_id='SF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=2),
            ),
            MatchSpec(
                long_name='Semifinal 1-3',
                short_name='SF1-3',
                name_detail='',
                order=41,
                match_group_id='SF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=1, match_number=3),
            ),
            MatchSpec(
                long_name='Semifinal 2-3',
                short_name='SF2-3',
                name_detail='',
                order=42,
                match_group_id='SF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=3),
            ),
        ],
    )
    assert_full_finals(self, match_specs, starting_index + 6)


def assert_full_quaterfinals_onward(self, match_specs, starting_index):
    self.assertEqual(len(match_specs), starting_index + 24)
    assertMatchSpecsEqual(
        self,
        match_specs[starting_index : starting_index + 12],
        [
            MatchSpec(
                long_name='Quaterfinal 1-1',
                short_name='QF1-1',
                name_detail='',
                order=25,
                match_group_id='QF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=1, match_number=1),
            ),
            MatchSpec(
                long_name='Quaterfinal 2-1',
                short_name='QF2-1',
                name_detail='',
                order=26,
                match_group_id='QF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=1),
            ),
            MatchSpec(
                long_name='Quaterfinal 3-1',
                short_name='QF3-1',
                name_detail='',
                order=27,
                match_group_id='QF3',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=1),
            ),
            MatchSpec(
                long_name='Quaterfinal 4-1',
                short_name='QF4-1',
                name_detail='',
                order=28,
                match_group_id='QF4',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=1),
            ),
            MatchSpec(
                long_name='Quaterfinal 1-2',
                short_name='QF1-2',
                name_detail='',
                order=29,
                match_group_id='QF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=1, match_number=2),
            ),
            MatchSpec(
                long_name='Quaterfinal 2-2',
                short_name='QF2-2',
                name_detail='',
                order=30,
                match_group_id='QF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=2),
            ),
            MatchSpec(
                long_name='Quaterfinal 3-2',
                short_name='QF3-2',
                name_detail='',
                order=31,
                match_group_id='QF3',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=2),
            ),
            MatchSpec(
                long_name='Quaterfinal 4-2',
                short_name='QF4-2',
                name_detail='',
                order=32,
                match_group_id='QF4',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=2),
            ),
            MatchSpec(
                long_name='Quaterfinal 1-3',
                short_name='QF1-3',
                name_detail='',
                order=33,
                match_group_id='QF1',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=1, match_number=3),
            ),
            MatchSpec(
                long_name='Quaterfinal 2-3',
                short_name='QF2-3',
                name_detail='',
                order=34,
                match_group_id='QF2',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=3),
            ),
            MatchSpec(
                long_name='Quaterfinal 3-3',
                short_name='QF3-3',
                name_detail='',
                order=35,
                match_group_id='QF3',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=3),
            ),
            MatchSpec(
                long_name='Quaterfinal 4-3',
                short_name='QF4-3',
                name_detail='',
                order=36,
                match_group_id='QF4',
                use_tiebreak_criteria=True,
                is_hidden=False,
                tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=3),
            ),
        ],
    )
    assert_full_semifinals_onward(self, match_specs, starting_index + 12)


class TestSingleElimination(unittest.TestCase):
    def test_single_elimination_inital_with_2_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(2)
        match_specs = collect_match_specs(final_matchup)

        assert_full_finals(self, match_specs, 0)

        final_matchup.update({})
        for i in range(6):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 2)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F'])

        self.assertEqual(len(break_specs), 2)
        self.assertEqual(
            break_specs[0],
            BreakSpec(order_before=44, description='Field Break', duration_sec=480),
        )
        self.assertEqual(
            break_specs[1],
            BreakSpec(order_before=45, description='Field Break', duration_sec=480),
        )

    def test_single_elimination_inital_with_3_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(3)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 9)
        assertMatchSpecsEqual(
            self,
            match_specs[0:3],
            [
                MatchSpec(
                    long_name='Semifinal 2-1',
                    short_name='SF2-1',
                    name_detail='',
                    order=38,
                    match_group_id='SF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Semifinal 2-2',
                    short_name='SF2-2',
                    name_detail='',
                    order=40,
                    match_group_id='SF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Semifinal 2-3',
                    short_name='SF2-3',
                    name_detail='',
                    order=42,
                    match_group_id='SF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=2, match_number=3),
                ),
            ],
        )

        assert_full_finals(self, match_specs, 3)

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:3],
            [ExpectedAlliance(2, 3), ExpectedAlliance(2, 3), ExpectedAlliance(2, 3)],
        )

        for i in range(3, 9):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF2'])

        self.assertEqual(len(break_specs), 3)
        self.assertEqual(
            break_specs[0],
            BreakSpec(order_before=43, description='Field Break', duration_sec=480),
        )
        self.assertEqual(
            break_specs[1],
            BreakSpec(order_before=44, description='Field Break', duration_sec=480),
        )
        self.assertEqual(
            break_specs[2],
            BreakSpec(order_before=45, description='Field Break', duration_sec=480),
        )

    def test_single_elimination_inital_with_4_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(4)
        match_specs = collect_match_specs(final_matchup)

        assert_full_semifinals_onward(self, match_specs, 0)
        final_matchup.update({})

        assertMatchSpecAlliances(
            self,
            match_specs[0:6],
            [
                ExpectedAlliance(1, 4),
                ExpectedAlliance(2, 3),
                ExpectedAlliance(1, 4),
                ExpectedAlliance(2, 3),
                ExpectedAlliance(1, 4),
                ExpectedAlliance(2, 3),
            ],
        )

        for i in range(6, 12):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF1', 'SF2'])

    def test_single_elimination_inital_with_5_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(5)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 15)
        assertMatchSpecsEqual(
            self,
            match_specs[0:3],
            [
                MatchSpec(
                    long_name='Quaterfinal 2-1',
                    short_name='QF2-1',
                    name_detail='',
                    order=26,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-2',
                    short_name='QF2-2',
                    name_detail='',
                    order=30,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-3',
                    short_name='QF2-3',
                    name_detail='',
                    order=34,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=3),
                ),
            ],
        )

        assert_full_semifinals_onward(self, match_specs, 3)
        final_matchup.update({})

        assertMatchSpecAlliances(
            self,
            match_specs[0:9],
            [
                ExpectedAlliance(4, 5),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 3),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 3),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 3),
            ],
        )

        for i in range(9, 15):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF1', 'SF2', 'QF2'])

    def test_single_elimination_inital_with_6_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(6)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 18)
        assertMatchSpecsEqual(
            self,
            match_specs[0:6],
            [
                MatchSpec(
                    long_name='Quaterfinal 2-1',
                    short_name='QF2-1',
                    name_detail='',
                    order=26,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-1',
                    short_name='QF4-1',
                    name_detail='',
                    order=28,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-2',
                    short_name='QF2-2',
                    name_detail='',
                    order=30,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-2',
                    short_name='QF4-2',
                    name_detail='',
                    order=32,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-3',
                    short_name='QF2-3',
                    name_detail='',
                    order=34,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-3',
                    short_name='QF4-3',
                    name_detail='',
                    order=36,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=3),
                ),
            ],
        )
        assert_full_semifinals_onward(self, match_specs, 6)

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:12],
            [
                ExpectedAlliance(4, 5),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(2, 0),
            ],
        )

        for i in range(12, 18):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF1', 'SF2', 'QF2', 'QF4'])

    def test_single_elimination_inital_with_7_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(7)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 21)
        assertMatchSpecsEqual(
            self,
            match_specs[0:9],
            [
                MatchSpec(
                    long_name='Quaterfinal 2-1',
                    short_name='QF2-1',
                    name_detail='',
                    order=26,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 3-1',
                    short_name='QF3-1',
                    name_detail='',
                    order=27,
                    match_group_id='QF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-1',
                    short_name='QF4-1',
                    name_detail='',
                    order=28,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-2',
                    short_name='QF2-2',
                    name_detail='',
                    order=30,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 3-2',
                    short_name='QF3-2',
                    name_detail='',
                    order=31,
                    match_group_id='QF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-2',
                    short_name='QF4-2',
                    name_detail='',
                    order=32,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Quaterfinal 2-3',
                    short_name='QF2-3',
                    name_detail='',
                    order=34,
                    match_group_id='QF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Quaterfinal 3-3',
                    short_name='QF3-3',
                    name_detail='',
                    order=35,
                    match_group_id='QF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=3, match_number=3),
                ),
                MatchSpec(
                    long_name='Quaterfinal 4-3',
                    short_name='QF4-3',
                    name_detail='',
                    order=36,
                    match_group_id='QF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='qf', set_number=4, match_number=3),
                ),
            ],
        )
        assert_full_semifinals_onward(self, match_specs, 9)

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:15],
            [
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
            ],
        )

        for i in range(15, 21):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF1', 'SF2', 'QF2', 'QF3', 'QF4'])

    def test_single_elimination_inital_with_8_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(8)
        match_specs = collect_match_specs(final_matchup)

        assert_full_quaterfinals_onward(self, match_specs, 0)

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:12],
            [
                ExpectedAlliance(1, 8),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 8),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 8),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
            ],
        )

        for i in range(12, 24):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(self, match_groups, ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4'])

        self.assertEqual(len(break_specs), 3)
        self.assertEqual(
            break_specs[0],
            BreakSpec(order_before=43, description='Field Break', duration_sec=480),
        )
        self.assertEqual(
            break_specs[1],
            BreakSpec(order_before=44, description='Field Break', duration_sec=480),
        )
        self.assertEqual(
            break_specs[2],
            BreakSpec(order_before=45, description='Field Break', duration_sec=480),
        )

    def test_single_elimination_inital_with_9_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(9)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 27)
        assertMatchSpecsEqual(
            self,
            match_specs[0:3],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 3)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:15],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 7),
                ExpectedAlliance(3, 6),
            ],
        )

        for i in range(15, 27):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self, match_groups, ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4', 'EF2']
        )

    def test_single_elimination_inital_with_10_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(10)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 30)
        assertMatchSpecsEqual(
            self,
            match_specs[0:6],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
            ],
        )
        assert_full_quaterfinals_onward(self, match_specs, 6)

        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:18],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 6),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 6),
            ],
        )
        for i in range(18, 30):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self, match_groups, ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4', 'EF2', 'EF6']
        )

    def test_single_elimination_inital_with_11_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(11)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 33)
        assertMatchSpecsEqual(
            self,
            match_specs[0:9],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 9)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:21],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 5),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
            ],
        )

        for i in range(21, 33):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self, match_groups, ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4', 'EF2', 'EF6', 'EF8']
        )

    def test_single_elimination_inital_with_12_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(12)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 36)
        assertMatchSpecsEqual(
            self,
            match_specs[0:12],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-1',
                    short_name='EF4-1',
                    name_detail='',
                    order=4,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-2',
                    short_name='EF4-2',
                    name_detail='',
                    order=12,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-3',
                    short_name='EF4-3',
                    name_detail='',
                    order=20,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 12)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:24],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(4, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
            ],
        )

        for i in range(24, 36):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4', 'EF2', 'EF4', 'EF6', 'EF8'],
        )

    def test_single_elimination_inital_with_13_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(13)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 39)
        assertMatchSpecsEqual(
            self,
            match_specs[0:15],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-1',
                    short_name='EF3-1',
                    name_detail='',
                    order=3,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-1',
                    short_name='EF4-1',
                    name_detail='',
                    order=4,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-2',
                    short_name='EF3-2',
                    name_detail='',
                    order=11,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-2',
                    short_name='EF4-2',
                    name_detail='',
                    order=12,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-3',
                    short_name='EF3-3',
                    name_detail='',
                    order=19,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-3',
                    short_name='EF4-3',
                    name_detail='',
                    order=20,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 15)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:27],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(3, 0),
            ],
        )

        for i in range(27, 39):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            ['F', 'SF1', 'SF2', 'QF1', 'QF2', 'QF3', 'QF4', 'EF2', 'EF3', 'EF4', 'EF6', 'EF8'],
        )

    def test_single_elimination_inital_with_14_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(14)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 42)
        assertMatchSpecsEqual(
            self,
            match_specs[0:18],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-1',
                    short_name='EF3-1',
                    name_detail='',
                    order=3,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-1',
                    short_name='EF4-1',
                    name_detail='',
                    order=4,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-1',
                    short_name='EF7-1',
                    name_detail='',
                    order=7,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-2',
                    short_name='EF3-2',
                    name_detail='',
                    order=11,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-2',
                    short_name='EF4-2',
                    name_detail='',
                    order=12,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-2',
                    short_name='EF7-2',
                    name_detail='',
                    order=15,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-3',
                    short_name='EF3-3',
                    name_detail='',
                    order=19,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-3',
                    short_name='EF4-3',
                    name_detail='',
                    order=20,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-3',
                    short_name='EF7-3',
                    name_detail='',
                    order=23,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 18)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:30],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(2, 0),
                ExpectedAlliance(0, 0),
            ],
        )

        for i in range(30, 42):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            [
                'F',
                'SF1',
                'SF2',
                'QF1',
                'QF2',
                'QF3',
                'QF4',
                'EF2',
                'EF3',
                'EF4',
                'EF6',
                'EF7',
                'EF8',
            ],
        )

    def test_single_elimination_inital_with_15_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(15)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 45)
        assertMatchSpecsEqual(
            self,
            match_specs[0:21],
            [
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-1',
                    short_name='EF3-1',
                    name_detail='',
                    order=3,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-1',
                    short_name='EF4-1',
                    name_detail='',
                    order=4,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-1',
                    short_name='EF5-1',
                    name_detail='',
                    order=5,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-1',
                    short_name='EF7-1',
                    name_detail='',
                    order=7,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-2',
                    short_name='EF3-2',
                    name_detail='',
                    order=11,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-2',
                    short_name='EF4-2',
                    name_detail='',
                    order=12,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-2',
                    short_name='EF5-2',
                    name_detail='',
                    order=13,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-2',
                    short_name='EF7-2',
                    name_detail='',
                    order=15,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-3',
                    short_name='EF3-3',
                    name_detail='',
                    order=19,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-3',
                    short_name='EF4-3',
                    name_detail='',
                    order=20,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-3',
                    short_name='EF5-3',
                    name_detail='',
                    order=21,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-3',
                    short_name='EF7-3',
                    name_detail='',
                    order=23,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 21)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:33],
            [
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(1, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
                ExpectedAlliance(0, 0),
            ],
        )

        for i in range(33, 45):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            [
                'F',
                'SF1',
                'SF2',
                'QF1',
                'QF2',
                'QF3',
                'QF4',
                'EF2',
                'EF3',
                'EF4',
                'EF5',
                'EF6',
                'EF7',
                'EF8',
            ],
        )

    def test_single_elimination_inital_with_16_alliance(self):
        final_matchup, break_specs = new_single_elimination_bracket(16)
        match_specs = collect_match_specs(final_matchup)

        self.assertEqual(len(match_specs), 48)
        assertMatchSpecsEqual(
            self,
            match_specs[0:24],
            [
                MatchSpec(
                    long_name='Eighthfinal 1-1',
                    short_name='EF1-1',
                    name_detail='',
                    order=1,
                    match_group_id='EF1',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=1, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-1',
                    short_name='EF2-1',
                    name_detail='',
                    order=2,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-1',
                    short_name='EF3-1',
                    name_detail='',
                    order=3,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-1',
                    short_name='EF4-1',
                    name_detail='',
                    order=4,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-1',
                    short_name='EF5-1',
                    name_detail='',
                    order=5,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-1',
                    short_name='EF6-1',
                    name_detail='',
                    order=6,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-1',
                    short_name='EF7-1',
                    name_detail='',
                    order=7,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-1',
                    short_name='EF8-1',
                    name_detail='',
                    order=8,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=1),
                ),
                MatchSpec(
                    long_name='Eighthfinal 1-2',
                    short_name='EF1-2',
                    name_detail='',
                    order=9,
                    match_group_id='EF1',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=1, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-2',
                    short_name='EF2-2',
                    name_detail='',
                    order=10,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-2',
                    short_name='EF3-2',
                    name_detail='',
                    order=11,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-2',
                    short_name='EF4-2',
                    name_detail='',
                    order=12,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-2',
                    short_name='EF5-2',
                    name_detail='',
                    order=13,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-2',
                    short_name='EF6-2',
                    name_detail='',
                    order=14,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-2',
                    short_name='EF7-2',
                    name_detail='',
                    order=15,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-2',
                    short_name='EF8-2',
                    name_detail='',
                    order=16,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=2),
                ),
                MatchSpec(
                    long_name='Eighthfinal 1-3',
                    short_name='EF1-3',
                    name_detail='',
                    order=17,
                    match_group_id='EF1',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=1, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 2-3',
                    short_name='EF2-3',
                    name_detail='',
                    order=18,
                    match_group_id='EF2',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=2, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 3-3',
                    short_name='EF3-3',
                    name_detail='',
                    order=19,
                    match_group_id='EF3',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=3, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 4-3',
                    short_name='EF4-3',
                    name_detail='',
                    order=20,
                    match_group_id='EF4',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=4, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 5-3',
                    short_name='EF5-3',
                    name_detail='',
                    order=21,
                    match_group_id='EF5',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=5, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 6-3',
                    short_name='EF6-3',
                    name_detail='',
                    order=22,
                    match_group_id='EF6',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=6, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 7-3',
                    short_name='EF7-3',
                    name_detail='',
                    order=23,
                    match_group_id='EF7',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=7, match_number=3),
                ),
                MatchSpec(
                    long_name='Eighthfinal 8-3',
                    short_name='EF8-3',
                    name_detail='',
                    order=24,
                    match_group_id='EF8',
                    use_tiebreak_criteria=True,
                    is_hidden=False,
                    tba_match_key=models.TbaMatchKey(comp_level='ef', set_number=8, match_number=3),
                ),
            ],
        )

        assert_full_quaterfinals_onward(self, match_specs, 24)
        final_matchup.update({})
        assertMatchSpecAlliances(
            self,
            match_specs[0:24],
            [
                ExpectedAlliance(1, 16),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 16),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
                ExpectedAlliance(1, 16),
                ExpectedAlliance(8, 9),
                ExpectedAlliance(4, 13),
                ExpectedAlliance(5, 12),
                ExpectedAlliance(2, 15),
                ExpectedAlliance(7, 10),
                ExpectedAlliance(3, 14),
                ExpectedAlliance(6, 11),
            ],
        )

        for i in range(24, 48):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(0, 0)])

        match_groups = collect_match_groups(final_matchup)
        assertMatchGroups(
            self,
            match_groups,
            [
                'F',
                'SF1',
                'SF2',
                'QF1',
                'QF2',
                'QF3',
                'QF4',
                'EF1',
                'EF2',
                'EF3',
                'EF4',
                'EF5',
                'EF6',
                'EF7',
                'EF8',
            ],
        )

        self.assertEqual(len(break_specs), 3)
        self.assertEqual(break_specs[0], BreakSpec(43, 480, 'Field Break'))
        self.assertEqual(break_specs[1], BreakSpec(44, 480, 'Field Break'))
        self.assertEqual(break_specs[2], BreakSpec(45, 480, 'Field Break'))

    def test_single_elimination_errors(self):
        self.assertRaises(ValueError, new_single_elimination_bracket, 1)
        self.assertRaises(ValueError, new_single_elimination_bracket, 17)

    def test_single_elimination_progression(self):
        playoff_tournament = PlayoffTournament(models.PlayoffType.SINGLE_ELIMINATION, 3)

        final_matchup = playoff_tournament.FinalMatchup()
        match_specs = playoff_tournament.match_specs
        match_groups = playoff_tournament.match_groups
        plaoff_match_results = dict[int, PlayoffMatchResult]()

        assertMatchOutcome(self, match_groups['SF2'], '', '')

        plaoff_match_results[38] = PlayoffMatchResult(game.MatchStatus.RED_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        for i in range(3, 9):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 0)])

        assertMatchOutcome(self, match_groups['SF2'], '', '')

        plaoff_match_results[40] = PlayoffMatchResult(game.MatchStatus.RED_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        for i in range(3, 9):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 2)])

        assertMatchOutcome(self, match_groups['SF2'], 'Advances to Final 1', 'Eliminated')

        plaoff_match_results[40] = PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        for i in range(3, 9):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 0)])

        assertMatchOutcome(self, match_groups['SF2'], '', '')

        plaoff_match_results[42] = PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        for i in range(3, 9):
            assertMatchSpecAlliances(self, [match_specs[i]], [ExpectedAlliance(1, 3)])

        assertMatchOutcome(self, match_groups['SF2'], 'Eliminated', 'Advances to Final 1')

        plaoff_match_results[43] = PlayoffMatchResult(game.MatchStatus.TIE_MATCH)
        final_matchup.update(plaoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(self, match_groups['F'], '', '')

        plaoff_match_results[44] = PlayoffMatchResult(game.MatchStatus.RED_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(self, match_groups['F'], '', '')

        plaoff_match_results[45] = PlayoffMatchResult(game.MatchStatus.RED_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        self.assertTrue(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 1)
        self.assertEqual(final_matchup.losing_alliance_id(), 3)
        assertMatchOutcome(self, match_groups['F'], 'Tournament Winner', 'Tournament Finalist')

        del plaoff_match_results[45]
        final_matchup.update(plaoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(self, match_groups['F'], '', '')

        plaoff_match_results[45] = PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        self.assertFalse(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 0)
        self.assertEqual(final_matchup.losing_alliance_id(), 0)
        assertMatchOutcome(self, match_groups['F'], '', '')

        plaoff_match_results[46] = PlayoffMatchResult(game.MatchStatus.BLUE_WON_MATCH)
        final_matchup.update(plaoff_match_results)
        self.assertTrue(final_matchup.is_complete())
        self.assertEqual(final_matchup.winning_alliance_id(), 3)
        self.assertEqual(final_matchup.losing_alliance_id(), 1)
        assertMatchOutcome(self, match_groups['F'], 'Tournament Finalist', 'Tournament Winner')
