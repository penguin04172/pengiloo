from datetime import datetime, timedelta

import game
import models

from .double_elimination import new_double_elimination_bracket
from .match_group import MatchGroup, MatchSpec, collect_match_groups, collect_match_specs
from .matchup import Matchup
from .single_elimination import new_single_elimination_bracket
from .specs import BreakSpec, PlayoffMatchResult


class PlayoffTournament:
    match_groups: dict[str, MatchGroup]
    match_specs: list[MatchSpec]
    break_specs: list[BreakSpec]
    final_matchup: Matchup

    def __init__(self, playoff_type: models.PlayoffType, num_playoff_alliances: int):
        if playoff_type == models.PlayoffType.DOUBLE_ELIMINATION:
            self.final_matchup, self.break_specs = new_double_elimination_bracket(
                num_playoff_alliances
            )
        elif playoff_type == models.PlayoffType.SINGLE_ELIMINATION:
            self.final_matchup, self.break_specs = new_single_elimination_bracket(
                num_playoff_alliances
            )
        else:
            raise ValueError(f'Unsupported playoff type: {playoff_type}')

        self.match_groups = collect_match_groups(self.final_matchup)
        self.match_specs = collect_match_specs(self.final_matchup)

        self.final_matchup.set_source_destinations()
        self.final_matchup.update({})

    def MatchGroups(self):
        return self.match_groups

    def FinalMatchup(self):
        return self.final_matchup

    def is_complete(self):
        return self.final_matchup.is_complete()

    def winning_alliance_id(self):
        return self.final_matchup.winning_alliance_id()

    def finalist_alliance_id(self):
        return self.final_matchup.losing_alliance_id()

    def traverse(self, visit_function):
        return self.final_matchup.traverse(visit_function)

    def create_match_and_breaks(self, start_time: datetime):
        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)

        if len(matches) > 0:
            raise ValueError('Playoff matches already exist')

        scheduled_breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
        if len(scheduled_breaks) > 0:
            raise ValueError('Scheduled breaks already exist')

        alliances = models.read_all_alliances()

        break_index = 0
        match_index = 0
        next_event_time = start_time

        while match_index < len(self.match_specs):
            while (
                break_index < len(self.break_specs)
                and self.break_specs[break_index].order_before < self.match_specs[match_index].order
            ):
                break_index += 1

            if (
                break_index < len(self.break_specs)
                and self.break_specs[break_index].order_before
                == self.match_specs[match_index].order
            ):
                break_spec = self.break_specs[break_index]
                models.create_scheduled_break(
                    models.ScheduledBreak(
                        match_type=models.MatchType.PLAYOFF,
                        type_order_before=break_spec.order_before,
                        time=next_event_time,
                        duration_sec=break_spec.duration_sec,
                        description=break_spec.description,
                    )
                )
                break_index += 1
                next_event_time = next_event_time + timedelta(seconds=break_spec.duration_sec)

            match_spec = self.match_specs[match_index]
            match = models.Match(
                type=models.MatchType.PLAYOFF,
                type_order=match_spec.order,
                scheduled_time=next_event_time,
                long_name=match_spec.long_name,
                short_name=match_spec.short_name,
                name_detail=match_spec.name_detail,
                playoff_match_group_id=match_spec.match_group_id,
                playoff_red_alliance=match_spec.red_alliance_id,
                playoff_blue_alliance=match_spec.blue_alliance_id,
                use_tiebreak_criteria=match_spec.use_tiebreak_criteria,
                tba_match_key=match_spec.tba_match_key,
            )

            if match.playoff_red_alliance > 0 and len(alliances) >= match.playoff_red_alliance:
                self.position_red_teams(match, alliances[match.playoff_red_alliance - 1])

            if match.playoff_blue_alliance > 0 and len(alliances) >= match.playoff_blue_alliance:
                self.position_blue_teams(match, alliances[match.playoff_blue_alliance - 1])

            # print(match)
            if match_spec.is_hidden:
                match.status = game.MatchStatus.MATCH_HIDDEN
            else:
                match.status = game.MatchStatus.MATCH_SCHEDULE

            models.create_match(match)

            match_index += 1
            next_event_time = next_event_time + timedelta(seconds=match_spec.duration_sec)

    def update_matches(self):
        matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
        if len(matches) == 0:
            raise ValueError('No playoff matches exist')

        playoff_match_results = dict[int, PlayoffMatchResult]()
        for match in matches:
            if match.status in [
                game.MatchStatus.RED_WON_MATCH,
                game.MatchStatus.BLUE_WON_MATCH,
                game.MatchStatus.TIE_MATCH,
            ]:
                playoff_match_results[match.type_order] = PlayoffMatchResult(match.status)

        self.final_matchup.update(playoff_match_results)

        matches_by_type_order = dict[int, models.MatchOut]()
        for match in matches:
            matches_by_type_order[match.type_order] = match

        alliances = models.read_all_alliances()
        for match_spec in self.match_specs:
            match = matches_by_type_order.get(match_spec.order)
            if match is None:
                raise ValueError(f'Match {match_spec.order} not found')

            if match.is_complete():
                continue

            if match_spec.is_hidden:
                match.status = game.MatchStatus.MATCH_HIDDEN
            else:
                match.status = game.MatchStatus.MATCH_SCHEDULE

            match.playoff_red_alliance = match_spec.red_alliance_id
            match.playoff_blue_alliance = match_spec.blue_alliance_id

            if (
                match.status == game.MatchStatus.MATCH_SCHEDULE
                and match.playoff_red_alliance > 0
                and len(alliances) >= match.playoff_red_alliance
            ):
                self.position_red_teams(match, alliances[match.playoff_red_alliance - 1])
            else:
                self.position_red_teams(match, models.Alliance(id=0, team_ids=[]))

            if (
                match.status == game.MatchStatus.MATCH_SCHEDULE
                and match.playoff_blue_alliance > 0
                and len(alliances) >= match.playoff_blue_alliance
            ):
                self.position_blue_teams(match, alliances[match.playoff_blue_alliance - 1])
            else:
                self.position_blue_teams(match, models.Alliance(id=0, team_ids=[]))

            models.update_match(match)

    @staticmethod
    def position_red_teams(match: models.Match, alliance: models.Alliance):
        match.red1 = alliance.line_up[0]
        match.red2 = alliance.line_up[1]
        match.red3 = alliance.line_up[2]

    @staticmethod
    def position_blue_teams(match: models.Match, alliance: models.Alliance):
        match.blue1 = alliance.line_up[0]
        match.blue2 = alliance.line_up[1]
        match.blue3 = alliance.line_up[2]
