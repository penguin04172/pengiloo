from collections.abc import Callable
from typing import Any, Protocol

import models

from .specs import PlayoffMatchResult


class MatchGroup(Protocol):
    def Id(self):
        pass

    def MatchSpecs(self):
        pass

    def update(self, playoff_match_result: dict[int, PlayoffMatchResult]):
        pass

    def traverse(self, visit_function: Callable):
        pass


class MatchSpec:
    long_name: str
    short_name: str
    name_detail: str
    match_group_id: str
    order: int
    duration_sec: int
    use_tiebreak_criteria: bool
    is_hidden: bool
    tba_match_key: models.TbaMatchKey
    red_alliance_id: int
    blue_alliance_id: int

    def __init__(
        self,
        long_name: str = '',
        short_name: str = '',
        name_detail: str = '',
        match_group_id: str = '',
        order: int = 0,
        duration_sec: int = 0,
        use_tiebreak_criteria: bool = False,
        is_hidden: bool = False,
        tba_match_key: models.TbaMatchKey = models.TbaMatchKey(),
    ):
        self.long_name = long_name
        self.short_name = short_name
        self.name_detail = name_detail
        self.match_group_id = match_group_id
        self.order = order
        self.duration_sec = duration_sec
        self.use_tiebreak_criteria = use_tiebreak_criteria
        self.is_hidden = is_hidden
        self.tba_match_key = tba_match_key
        self.red_alliance_id = 0
        self.blue_alliance_id = 0


def collect_match_groups(root_match_group: MatchGroup):
    match_groups = dict[str, MatchGroup]()

    def visit(match_group: MatchGroup):
        if match_group.Id() in match_groups:
            raise ValueError(f'Duplicate match group ID: {match_group.Id()}')
        match_groups[match_group.Id()] = match_group

    root_match_group.traverse(visit)
    return match_groups


def collect_match_specs(root_match_group: MatchGroup):
    unique_long_names = dict[str, Any]()
    unique_short_names = dict[str, Any]()
    unique_orders = dict[int, Any]()
    unique_tba_keys = dict[str, Any]()

    matches = []

    def visit(match_group: MatchGroup):
        for match_spec in match_group.MatchSpecs():
            if match_spec.long_name in unique_long_names:
                raise ValueError(f'Duplicate long name: {match_spec.long_name}')

            if match_spec.short_name in unique_short_names:
                raise ValueError(f'Duplicate short name: {match_spec.short_name}')

            if match_spec.order in unique_orders:
                raise ValueError(f'Duplicate order: {match_spec.order}')

            if str(match_spec.tba_match_key) in unique_tba_keys:
                raise ValueError(f'Duplicate TBA key: {match_spec.tba_match_key}')

            match_spec.match_group_id = match_group.Id()
            matches.append(match_spec)

            unique_long_names[match_spec.long_name] = {}
            unique_short_names[match_spec.short_name] = {}
            unique_orders[match_spec.order] = {}
            unique_tba_keys[str(match_spec.tba_match_key)] = {}

    root_match_group.traverse(visit)
    matches.sort(key=lambda match: match.order)
    return matches
