import models

from .alliance_source import AllianceSelectionSource, MatchupSource
from .match_group import MatchSpec
from .matchup import Matchup
from .single_elimination import new_final_matches
from .specs import BreakSpec


def new_double_elimination_bracket(num_alliances: int):
    if num_alliances != 8:
        raise ValueError('Only 8 alliances are supported for double elimination')

    # Round 1
    m1 = Matchup(
        id='M1',
        num_wins_to_advance=1,
        red_alliance_source=AllianceSelectionSource(alliance_id=1),
        blue_alliance_source=AllianceSelectionSource(alliance_id=8),
        match_specs=new_double_elimination_match(1, 'Round 1 Upper', 540),
    )

    m2 = Matchup(
        id='M2',
        num_wins_to_advance=1,
        red_alliance_source=AllianceSelectionSource(alliance_id=4),
        blue_alliance_source=AllianceSelectionSource(alliance_id=5),
        match_specs=new_double_elimination_match(2, 'Round 1 Upper', 540),
    )

    m3 = Matchup(
        id='M3',
        num_wins_to_advance=1,
        red_alliance_source=AllianceSelectionSource(alliance_id=2),
        blue_alliance_source=AllianceSelectionSource(alliance_id=7),
        match_specs=new_double_elimination_match(3, 'Round 1 Upper', 540),
    )

    m4 = Matchup(
        id='M4',
        num_wins_to_advance=1,
        red_alliance_source=AllianceSelectionSource(alliance_id=3),
        blue_alliance_source=AllianceSelectionSource(alliance_id=6),
        match_specs=new_double_elimination_match(4, 'Round 1 Upper', 540),
    )

    # Round 2
    m5 = Matchup(
        id='M5',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m1, use_winner=False),
        blue_alliance_source=MatchupSource(matchup=m2, use_winner=False),
        match_specs=new_double_elimination_match(5, 'Round 2 Lower', 540),
    )

    m6 = Matchup(
        id='M6',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m3, use_winner=False),
        blue_alliance_source=MatchupSource(matchup=m4, use_winner=False),
        match_specs=new_double_elimination_match(6, 'Round 2 Lower', 540),
    )

    m7 = Matchup(
        id='M7',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m1, use_winner=True),
        blue_alliance_source=MatchupSource(matchup=m2, use_winner=True),
        match_specs=new_double_elimination_match(7, 'Round 2 Upper', 540),
    )

    m8 = Matchup(
        id='M8',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m3, use_winner=True),
        blue_alliance_source=MatchupSource(matchup=m4, use_winner=True),
        match_specs=new_double_elimination_match(8, 'Round 2 Upper', 540),
    )

    # Round 3
    m9 = Matchup(
        id='M9',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m7, use_winner=False),
        blue_alliance_source=MatchupSource(matchup=m6, use_winner=True),
        match_specs=new_double_elimination_match(9, 'Round 3 Lower', 540),
    )

    m10 = Matchup(
        id='M10',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m8, use_winner=False),
        blue_alliance_source=MatchupSource(matchup=m5, use_winner=True),
        match_specs=new_double_elimination_match(10, 'Round 3 Lower', 300),
    )

    # Round 4
    m11 = Matchup(
        id='M11',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m7, use_winner=True),
        blue_alliance_source=MatchupSource(matchup=m8, use_winner=True),
        match_specs=new_double_elimination_match(11, 'Round 4 Upper', 540),
    )

    m12 = Matchup(
        id='M12',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m10, use_winner=True),
        blue_alliance_source=MatchupSource(matchup=m9, use_winner=True),
        match_specs=new_double_elimination_match(12, 'Round 4 Lower', 300),
    )

    # Round 5
    m13 = Matchup(
        id='M13',
        num_wins_to_advance=1,
        red_alliance_source=MatchupSource(matchup=m11, use_winner=False),
        blue_alliance_source=MatchupSource(matchup=m12, use_winner=True),
        match_specs=new_double_elimination_match(13, 'Round 5 Lower', 300),
    )

    # Round 6
    final = Matchup(
        id='F',
        num_wins_to_advance=2,
        red_alliance_source=MatchupSource(matchup=m11, use_winner=True),
        blue_alliance_source=MatchupSource(matchup=m13, use_winner=True),
        match_specs=new_final_matches(14),
    )

    break_specs = [
        BreakSpec(order_before=11, description='Field Break', duration_sec=360),
        BreakSpec(order_before=13, description='Award Break', duration_sec=900),
        BreakSpec(order_before=14, description='Award Break', duration_sec=900),
        BreakSpec(order_before=15, description='Award Break', duration_sec=900),
        BreakSpec(order_before=16, description='Award Break', duration_sec=900),
    ]

    return final, break_specs


def new_double_elimination_alliance_source(matchup: Matchup, num_alliances: int, use_winner: bool):
    red_alliance_id = matchup.red_alliance_id
    blue_alliance_id = matchup.blue_alliance_id

    if blue_alliance_id > red_alliance_id and blue_alliance_id > num_alliances:
        return matchup.red_alliance_source
    if red_alliance_id > blue_alliance_id and red_alliance_id > num_alliances:
        return matchup.blue_alliance_source

    return MatchupSource(matchup=matchup, use_winner=use_winner)


def new_double_elimination_match(
    number: int, name_detail: str, duration_sec: int
) -> list[MatchSpec]:
    return [
        MatchSpec(
            long_name=f'Match {number}',
            short_name=f'M{number}',
            name_detail=name_detail,
            order=number,
            duration_sec=duration_sec,
            use_tiebreak_criteria=True,
            tba_match_key=models.TbaMatchKey(comp_level='sf', set_number=number, match_number=1),
        )
    ]
