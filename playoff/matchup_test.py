import unittest

import game

from .alliance_source import AllianceSelectionSource
from .double_elimination import new_double_elimination_bracket
from .match_group import collect_match_groups, collect_match_specs
from .matchup import Matchup
from .single_elimination import (
    new_final_matches,
    new_single_elemination_match,
    new_single_elimination_bracket,
)


class TestMatchup(unittest.TestCase):
    def test_matchup_alliance_source_display_names(self):
        matchup, _ = new_double_elimination_bracket(8)

        self.assertEqual(matchup.red_alliance_source_display_name(), 'W M11')
        self.assertEqual(matchup.blue_alliance_source_display_name(), 'W M13')

        match_groups = collect_match_groups(matchup)

        match_13 = match_groups['M13']
        self.assertEqual(match_13.red_alliance_source_display_name(), 'L M11')
        self.assertEqual(match_13.blue_alliance_source_display_name(), 'W M12')

        matchup, _ = new_single_elimination_bracket(5)
        self.assertEqual(matchup.red_alliance_source_display_name(), 'W SF1')
        self.assertEqual(matchup.blue_alliance_source_display_name(), 'W SF2')

        match_groups = collect_match_groups(matchup)

        sf1 = match_groups['SF1']
        self.assertEqual(sf1.red_alliance_source_display_name(), 'A 1')
        self.assertEqual(sf1.blue_alliance_source_display_name(), 'W QF2')

    def test_matchup_status_text(self):
        matchup = Matchup(num_wins_to_advance=1)

        leader, status = matchup.status_text()
        self.assertEqual(leader, '')
        self.assertEqual(status, '')

        matchup.red_alliance_wins = 1
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'red')
        self.assertEqual(status, 'Red Advances 1-0')

        matchup.red_alliance_wins = 0
        matchup.blue_alliance_wins = 2
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'blue')
        self.assertEqual(status, 'Blue Advances 2-0')

        matchup.num_wins_to_advance = 3
        matchup.blue_alliance_wins = 2
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'blue')
        self.assertEqual(status, 'Blue Leads 2-0')

        matchup.red_alliance_wins = 2
        leader, status = matchup.status_text()
        self.assertEqual(leader, '')
        self.assertEqual(status, 'Series Tied 2-2')

        matchup.blue_alliance_wins = 1
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'red')
        self.assertEqual(status, 'Red Leads 2-1')

        matchup.id = 'F'
        matchup.red_alliance_wins = 3
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'red')
        self.assertEqual(status, 'Red Wins 3-1')

        matchup.red_alliance_wins = 2
        matchup.blue_alliance_wins = 4
        leader, status = matchup.status_text()
        self.assertEqual(leader, 'blue')
        self.assertEqual(status, 'Blue Wins 4-2')

        matchup.red_alliance_wins = 0
        matchup.blue_alliance_wins = 0
        leader, status = matchup.status_text()
        self.assertEqual(leader, '')
        self.assertEqual(status, '')

    def test_matchup_hide_unnecessary_matches(self):
        qf1 = Matchup(
            id='QF1',
            num_wins_to_advance=2,
            red_alliance_source=AllianceSelectionSource(1),
            blue_alliance_source=AllianceSelectionSource(8),
            match_specs=[
                new_single_elemination_match('Quaterfinal', 'QF', 1, 1, 1),
                new_single_elemination_match('Quaterfinal', 'QF', 1, 2, 5),
                new_single_elemination_match('Quaterfinal', 'QF', 1, 3, 9),
            ],
        )

        match_specs = collect_match_specs(qf1)

        for match_spec in match_specs:
            self.assertFalse(match_spec.is_hidden)

        playoff_match_results = {1: game.MATCH_STATUS.blue_won_match}
        qf1.update(playoff_match_results)
        for match_spec in match_specs:
            self.assertFalse(match_spec.is_hidden)

        playoff_match_results[5] = game.MATCH_STATUS.blue_won_match
        qf1.update(playoff_match_results)
        self.assertFalse(match_specs[0].is_hidden)
        self.assertFalse(match_specs[1].is_hidden)
        self.assertTrue(match_specs[2].is_hidden)

        playoff_match_results[5] = game.MATCH_STATUS.red_won_match
        qf1.update(playoff_match_results)
        for match_spec in match_specs:
            self.assertFalse(match_spec.is_hidden)

    def test_matchup_overtime(self):
        final = Matchup(
            id='F',
            num_wins_to_advance=2,
            red_alliance_source=AllianceSelectionSource(1),
            blue_alliance_source=AllianceSelectionSource(8),
            match_specs=new_final_matches(1),
        )

        match_specs = collect_match_specs(final)
        for i in range(6):
            self.assertEqual(match_specs[i].is_hidden, i > 2)

        playoff_match_results = {1: game.MATCH_STATUS.red_won_match, 2: game.MATCH_STATUS.tie_match}
        final.update(playoff_match_results)
        for i in range(6):
            self.assertEqual(match_specs[i].is_hidden, i > 2)

        playoff_match_results[3] = game.MATCH_STATUS.blue_won_match
        final.update(playoff_match_results)
        for i in range(6):
            self.assertEqual(match_specs[i].is_hidden, i > 3)

        playoff_match_results[4] = game.MATCH_STATUS.tie_match
        final.update(playoff_match_results)
        for i in range(6):
            self.assertEqual(match_specs[i].is_hidden, i > 4)

        playoff_match_results[5] = game.MATCH_STATUS.blue_won_match
        final.update(playoff_match_results)
        for i in range(6):
            self.assertEqual(match_specs[i].is_hidden, i > 4)
