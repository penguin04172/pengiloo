import models

from .alliance_source import AllianceSelectionSource, MatchupSource
from .matchup import MatchSpec, Matchup
from .specs import BreakSpec


def new_single_elimination_bracket(num_alliances: int):
    if num_alliances < 2:
        raise ValueError('Single elimination bracket requires at least 2 alliances')

    if num_alliances > 16:
        raise ValueError('Single elimination bracket only supports 16 or fewer alliances')

    # Eighthfinal
    ef1 = Matchup(
        id='EF1',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=1),
        blue_alliance_source=AllianceSelectionSource(alliance_id=16),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 1, 1, 1),
            new_single_elemination_match('Eighthfinal', 'EF', 1, 2, 9),
            new_single_elemination_match('Eighthfinal', 'EF', 1, 3, 17),
        ],
    )

    ef2 = Matchup(
        id='EF2',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=8),
        blue_alliance_source=AllianceSelectionSource(alliance_id=9),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 2, 1, 2),
            new_single_elemination_match('Eighthfinal', 'EF', 2, 2, 10),
            new_single_elemination_match('Eighthfinal', 'EF', 2, 3, 18),
        ],
    )

    ef3 = Matchup(
        id='EF3',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=4),
        blue_alliance_source=AllianceSelectionSource(alliance_id=13),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 3, 1, 3),
            new_single_elemination_match('Eighthfinal', 'EF', 3, 2, 11),
            new_single_elemination_match('Eighthfinal', 'EF', 3, 3, 19),
        ],
    )

    ef4 = Matchup(
        id='EF4',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=5),
        blue_alliance_source=AllianceSelectionSource(alliance_id=12),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 4, 1, 4),
            new_single_elemination_match('Eighthfinal', 'EF', 4, 2, 12),
            new_single_elemination_match('Eighthfinal', 'EF', 4, 3, 20),
        ],
    )

    ef5 = Matchup(
        id='EF5',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=2),
        blue_alliance_source=AllianceSelectionSource(alliance_id=15),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 5, 1, 5),
            new_single_elemination_match('Eighthfinal', 'EF', 5, 2, 13),
            new_single_elemination_match('Eighthfinal', 'EF', 5, 3, 21),
        ],
    )

    ef6 = Matchup(
        id='EF6',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=7),
        blue_alliance_source=AllianceSelectionSource(alliance_id=10),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 6, 1, 6),
            new_single_elemination_match('Eighthfinal', 'EF', 6, 2, 14),
            new_single_elemination_match('Eighthfinal', 'EF', 6, 3, 22),
        ],
    )

    ef7 = Matchup(
        id='EF7',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=3),
        blue_alliance_source=AllianceSelectionSource(alliance_id=14),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 7, 1, 7),
            new_single_elemination_match('Eighthfinal', 'EF', 7, 2, 15),
            new_single_elemination_match('Eighthfinal', 'EF', 7, 3, 23),
        ],
    )

    ef8 = Matchup(
        id='EF8',
        num_wins_to_advance=2,
        red_alliance_source=AllianceSelectionSource(alliance_id=6),
        blue_alliance_source=AllianceSelectionSource(alliance_id=11),
        match_specs=[
            new_single_elemination_match('Eighthfinal', 'EF', 8, 1, 8),
            new_single_elemination_match('Eighthfinal', 'EF', 8, 2, 16),
            new_single_elemination_match('Eighthfinal', 'EF', 8, 3, 24),
        ],
    )

    # Quaterfinal
    qf1 = Matchup(
        id='QF1',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=ef1, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=ef2, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Quaterfinal', 'QF', 1, 1, 25),
            new_single_elemination_match('Quaterfinal', 'QF', 1, 2, 29),
            new_single_elemination_match('Quaterfinal', 'QF', 1, 3, 33),
        ],
    )

    qf2 = Matchup(
        id='QF2',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=ef3, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=ef4, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Quaterfinal', 'QF', 2, 1, 26),
            new_single_elemination_match('Quaterfinal', 'QF', 2, 2, 30),
            new_single_elemination_match('Quaterfinal', 'QF', 2, 3, 34),
        ],
    )

    qf3 = Matchup(
        id='QF3',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=ef5, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=ef6, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Quaterfinal', 'QF', 3, 1, 27),
            new_single_elemination_match('Quaterfinal', 'QF', 3, 2, 31),
            new_single_elemination_match('Quaterfinal', 'QF', 3, 3, 35),
        ],
    )

    qf4 = Matchup(
        id='QF4',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=ef7, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=ef8, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Quaterfinal', 'QF', 4, 1, 28),
            new_single_elemination_match('Quaterfinal', 'QF', 4, 2, 32),
            new_single_elemination_match('Quaterfinal', 'QF', 4, 3, 36),
        ],
    )

    # Semifinal
    sf1 = Matchup(
        id='SF1',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=qf1, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=qf2, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Semifinal', 'SF', 1, 1, 37),
            new_single_elemination_match('Semifinal', 'SF', 1, 2, 39),
            new_single_elemination_match('Semifinal', 'SF', 1, 3, 41),
        ],
    )

    sf2 = Matchup(
        id='SF2',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=qf3, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=qf4, num_alliances=num_alliances
        ),
        match_specs=[
            new_single_elemination_match('Semifinal', 'SF', 2, 1, 38),
            new_single_elemination_match('Semifinal', 'SF', 2, 2, 40),
            new_single_elemination_match('Semifinal', 'SF', 2, 3, 42),
        ],
    )

    # finals
    f1 = Matchup(
        id='F',
        num_wins_to_advance=2,
        red_alliance_source=new_single_elimination_alliance_source(
            matchup=sf1, num_alliances=num_alliances
        ),
        blue_alliance_source=new_single_elimination_alliance_source(
            matchup=sf2, num_alliances=num_alliances
        ),
        match_specs=new_final_matches(43),
    )

    # breaks
    breal_specs = []
    if num_alliances > 2:
        breal_specs.append(
            BreakSpec(
                order_before=43,
                duration_sec=480,
                description='Field Break',
            )
        )

    breal_specs.append(
        BreakSpec(
            order_before=44,
            duration_sec=480,
            description='Field Break',
        )
    )
    breal_specs.append(
        BreakSpec(
            order_before=45,
            duration_sec=480,
            description='Field Break',
        )
    )

    return f1, breal_specs


def new_single_elimination_alliance_source(matchup: Matchup, num_alliances: int):
    red_alliance_id = matchup.red_alliance_source.AllianceId()
    blue_alliance_id = matchup.blue_alliance_source.AllianceId()

    if blue_alliance_id > red_alliance_id and blue_alliance_id > num_alliances:
        return matchup.red_alliance_source

    if red_alliance_id > blue_alliance_id and red_alliance_id > num_alliances:
        return matchup.blue_alliance_source

    return MatchupSource(matchup=matchup, use_winner=True)


def new_single_elemination_match(
    long_round_name: str, short_round_name: str, set_number: int, match_number: int, order: int
):
    return MatchSpec(
        long_name=f'{long_round_name} {set_number}-{match_number}',
        short_name=f'{short_round_name}{set_number}-{match_number}',
        order=order,
        duration_sec=600,
        use_tiebreak_criteria=True,
        tba_match_key=models.TbaMatchKey(
            comp_level=short_round_name.lower(), set_number=set_number, match_number=match_number
        ),
    )


def new_final_matches(starting_order: int):
    return [
        MatchSpec(
            long_name='Final 1',
            short_name='F1',
            order=starting_order,
            duration_sec=300,
            use_tiebreak_criteria=False,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=1),
        ),
        MatchSpec(
            long_name='Final 2',
            short_name='F2',
            order=starting_order + 1,
            duration_sec=300,
            use_tiebreak_criteria=False,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=2),
        ),
        MatchSpec(
            long_name='Final 3',
            short_name='F3',
            order=starting_order + 2,
            duration_sec=300,
            use_tiebreak_criteria=False,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=3),
        ),
        MatchSpec(
            long_name='Overtime 1',
            short_name='O1',
            order=starting_order + 3,
            duration_sec=600,
            use_tiebreak_criteria=True,
            is_hidden=True,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=4),
        ),
        MatchSpec(
            long_name='Overtime 2',
            short_name='O2',
            order=starting_order + 4,
            duration_sec=600,
            use_tiebreak_criteria=True,
            is_hidden=True,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=5),
        ),
        MatchSpec(
            long_name='Overtime 3',
            short_name='O3',
            order=starting_order + 5,
            duration_sec=600,
            use_tiebreak_criteria=True,
            is_hidden=True,
            tba_match_key=models.TbaMatchKey(comp_level='f', set_number=1, match_number=6),
        ),
    ]
