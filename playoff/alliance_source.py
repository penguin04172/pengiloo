from collections.abc import Callable
from typing import Protocol

from playoff.match_group import MatchGroup

from .specs import PlayoffMatchResult


class AllianceSource(Protocol):
    def AllianceId(self):
        pass

    def DisplayName(self):
        pass

    def setDestination(self, destination: MatchGroup):
        pass

    def update(self, playoff_match_result):
        pass

    def traverse(self, visit_function: Callable):
        pass


class AllianceSelectionSource:
    alliance_id: int

    def __init__(self, alliance_id: int):
        self.alliance_id = alliance_id

    def AllianceId(self):
        return self.alliance_id

    def DisplayName(self):
        return f'A {self.alliance_id}'

    def setDestination(self, destination: MatchGroup):
        pass

    def update(self, playoff_match_result: dict[int, PlayoffMatchResult]):
        pass

    def traverse(self, visit_function: Callable):
        return None


class MatchupSource:
    from playoff.matchup import Matchup

    matchup: Matchup
    use_winner: bool

    def __init__(self, matchup: Matchup, use_winner: bool):
        self.matchup = matchup
        self.use_winner = use_winner

    def AllianceId(self):
        if self.use_winner:
            return self.matchup.winning_alliance_id()
        else:
            return self.matchup.losing_alliance_id()

    def DisplayName(self):
        if self.use_winner:
            return f'W {self.matchup.id}'
        else:
            return f'L {self.matchup.id}'

    def setDestination(self, destination: MatchGroup):
        if self.use_winner:
            self.matchup.winning_alliance_destination = destination
        else:
            self.matchup.losing_alliance_destination = destination

        self.matchup.set_source_destinations()

    def update(self, playoff_match_result: dict[int, PlayoffMatchResult]):
        if self.use_winner:
            self.matchup.update(playoff_match_result)

    def traverse(self, visit_function: Callable):
        if self.use_winner:
            return self.matchup.traverse(visit_function)
