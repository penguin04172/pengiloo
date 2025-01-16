from collections.abc import Callable

import game

from .alliance_source import AllianceSource
from .match_group import MatchGroup, MatchSpec
from .specs import PlayoffMatchResult


class Matchup:
    id: str
    num_wins_to_advance: int
    red_alliance_source: AllianceSource
    blue_alliance_source: AllianceSource
    match_specs: list[MatchSpec]
    red_alliance_id: int
    red_alliance_wins: int
    blue_alliance_id: int
    blue_alliance_wins: int
    num_matches_played: int
    winning_alliance_destination: MatchGroup
    losing_alliance_destination: MatchGroup

    def __init__(
        self,
        id: str = '',
        num_wins_to_advance: int = 0,
        red_alliance_source: AllianceSource = None,
        blue_alliance_source: AllianceSource = None,
        match_specs: list[MatchSpec] = None,
    ):
        if match_specs is None:
            match_specs = []
        self.id = id
        self.num_wins_to_advance = num_wins_to_advance
        self.red_alliance_source = red_alliance_source
        self.blue_alliance_source = blue_alliance_source
        self.match_specs = match_specs
        self.red_alliance_id = 0
        self.red_alliance_wins = 0
        self.blue_alliance_id = 0
        self.blue_alliance_wins = 0
        self.num_matches_played = 0
        self.winning_alliance_destination = None
        self.losing_alliance_destination = None

    def Id(self):
        return self.id

    def MatchSpecs(self):
        return self.match_specs

    def update(self, playoff_match_result: dict[int, PlayoffMatchResult]):
        self.red_alliance_source.update(playoff_match_result)
        self.blue_alliance_source.update(playoff_match_result)

        self.red_alliance_id = self.red_alliance_source.AllianceId()
        self.blue_alliance_id = self.blue_alliance_source.AllianceId()

        for match in self.match_specs:
            match.red_alliance_id = self.red_alliance_id
            match.blue_alliance_id = self.blue_alliance_id

        self.red_alliance_wins = 0
        self.blue_alliance_wins = 0
        self.num_matches_played = 0
        unplayed_matches = list[MatchSpec]()

        for match in self.match_specs:
            match_result = playoff_match_result.get(match.order)
            if match_result is not None:
                if match_result.status == game.MatchStatus.RED_WON_MATCH:
                    self.red_alliance_wins += 1
                    self.num_matches_played += 1
                elif match_result.status == game.MatchStatus.BLUE_WON_MATCH:
                    self.blue_alliance_wins += 1
                    self.num_matches_played += 1
                elif match_result.status == game.MatchStatus.TIE_MATCH:
                    self.num_matches_played += 1
            else:
                unplayed_matches.append(match)

        num_matches_to_schedule = int(
            min(
                self.num_wins_to_advance - self.red_alliance_wins,
                self.num_wins_to_advance - self.blue_alliance_wins,
            )
        )

        for match in unplayed_matches:
            if num_matches_to_schedule > 0:
                match.is_hidden = False
                num_matches_to_schedule -= 1
            elif self.is_complete():
                match.is_hidden = True

    def set_source_destinations(self):
        self.red_alliance_source.setDestination(self)
        self.blue_alliance_source.setDestination(self)

    def traverse(self, visit_function: Callable):
        visit_function(self)
        self.red_alliance_source.traverse(visit_function)
        self.blue_alliance_source.traverse(visit_function)

    def red_alliance_source_display_name(self):
        return self.red_alliance_source.DisplayName()

    def blue_alliance_source_display_name(self):
        return self.blue_alliance_source.DisplayName()

    def red_alliance_destination(self):
        return self.alliance_destination(self.red_alliance_id)

    def blue_alliance_destination(self):
        return self.alliance_destination(self.blue_alliance_id)

    def status_text(self):
        leader = ''
        status = ''
        win_text = 'Advances'

        if self.is_final():
            win_text = 'Wins'

        if self.red_alliance_wins >= self.num_wins_to_advance:
            leader = 'red'
            status = f'Red {win_text} {self.red_alliance_wins}-{self.blue_alliance_wins}'
        elif self.blue_alliance_wins >= self.num_wins_to_advance:
            leader = 'blue'
            status = f'Blue {win_text} {self.blue_alliance_wins}-{self.red_alliance_wins}'
        elif self.red_alliance_wins > self.blue_alliance_wins:
            leader = 'red'
            status = f'Red Leads {self.red_alliance_wins}-{self.blue_alliance_wins}'
        elif self.blue_alliance_wins > self.red_alliance_wins:
            leader = 'blue'
            status = f'Blue Leads {self.blue_alliance_wins}-{self.red_alliance_wins}'
        elif self.red_alliance_wins > 0:
            status = f'Series Tied {self.red_alliance_wins}-{self.blue_alliance_wins}'

        return (leader, status)

    def winning_alliance_id(self):
        if self.red_alliance_wins >= self.num_wins_to_advance:
            return self.red_alliance_id
        if self.blue_alliance_wins >= self.num_wins_to_advance:
            return self.blue_alliance_id
        return 0

    def losing_alliance_id(self):
        if self.red_alliance_wins >= self.num_wins_to_advance:
            return self.blue_alliance_id
        if self.blue_alliance_wins >= self.num_wins_to_advance:
            return self.red_alliance_id
        return 0

    def is_complete(self):
        return self.winning_alliance_id() > 0

    def is_final(self):
        return self.id == 'F'

    def alliance_destination(self, alliance_id: int):
        if not self.is_complete():
            return ''

        if self.is_final():
            if self.winning_alliance_id() == alliance_id:
                return 'Tournament Winner'
            else:
                return 'Tournament Finalist'

        if self.winning_alliance_id() == alliance_id:
            return f'Advances to {format_destination_match_name(self.winning_alliance_destination)}'
        else:
            if self.losing_alliance_destination is None:
                return 'Eliminated'
            return f'Advances to {format_destination_match_name(self.losing_alliance_destination)}'


def format_destination_match_name(destination: MatchGroup):
    if destination is None or len(destination.MatchSpecs()) == 0:
        return ''
    destination_match = destination.MatchSpecs()[0]
    destination_match_name = destination_match.long_name
    if destination_match.name_detail != '':
        destination_match_name += f' - {destination_match.name_detail}'

    return destination_match_name
