import unittest

import models

from .alliance_source import AllianceSelectionSource, MatchupSource
from .double_elimination import new_double_elimination_match
from .match_group import MatchSpec, collect_match_groups, collect_match_specs
from .matchup import Matchup


class TestMatchGroup(unittest.TestCase):
    def test_collect_match_groups_error(self):
        match_group1 = Matchup(
            id='M1',
            num_wins_to_advance=1,
            red_alliance_source=AllianceSelectionSource(alliance_id=2),
            blue_alliance_source=AllianceSelectionSource(alliance_id=3),
            match_specs=new_double_elimination_match(1, '', 300),
        )
        match_group2 = Matchup(
            id='M1',
            num_wins_to_advance=1,
            red_alliance_source=AllianceSelectionSource(alliance_id=1),
            blue_alliance_source=MatchupSource(matchup=match_group1, use_winner=True),
            match_specs=new_double_elimination_match(1, '', 300),
        )

        self.assertRaises(ValueError, collect_match_groups, match_group2)

    def test_collect_match_specs_error(self):
        match1 = MatchSpec(
            long_name='Final 1',
            short_name='F1',
            order=1,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=1),
        )
        match2 = MatchSpec(
            long_name='Final 2',
            short_name='F2',
            order=2,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=2),
        )
        match3 = MatchSpec(
            long_name='Final 3',
            short_name='F3',
            order=3,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=3),
        )

        match_group1 = Matchup(
            id='F',
            num_wins_to_advance=2,
            red_alliance_source=AllianceSelectionSource(alliance_id=1),
            blue_alliance_source=AllianceSelectionSource(alliance_id=2),
            match_specs=[match3, match2, match1],
        )

        try:
            match_specs = collect_match_specs(match_group1)
        except Exception as e:
            self.fail(f'collect_match_specs() raised {type(e)} with message: {e}')

        self.assertEqual(match_specs, [match1, match2, match3])

        match3.long_name = 'Final 1'
        self.assertRaises(ValueError, collect_match_specs, match_group1)

        match3.long_name = 'Final 3'
        match3.short_name = 'F1'
        self.assertRaises(ValueError, collect_match_specs, match_group1)

        match3.short_name = 'F3'
        match3.order = 1
        self.assertRaises(ValueError, collect_match_specs, match_group1)

        match3.order = 3
        match3.tba_match_key = models.TbaMatchKey(comp_level='f', set_number=1, match_number=1)
        self.assertRaises(ValueError, collect_match_specs, match_group1)
