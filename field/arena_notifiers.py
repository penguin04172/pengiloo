from pydantic import BaseModel

import game
import models
from ws.notifier import Notifier

from .display import Display
from .realtime_score import RealtimeScore
from .specs import MatchState


class MatchTimeMessage(BaseModel):
    match_state: MatchState
    match_time_sec: int


class AudienceAllianceScoreFields(BaseModel):
    score: game.Score
    score_summary: game.ScoreSummary
    amplified_time_remaining_sec: int


class ArenaNotifiersMixin:
    alliance_selection_notifier: Notifier
    alliance_station_display_mode_notifier: Notifier
    arena_status_notifier: Notifier
    audience_display_mode_notifier: Notifier
    display_configuration_notifier: Notifier
    event_status_notifier: Notifier
    lower_third_notifier: Notifier
    match_load_notifier: Notifier
    match_time_notifier: Notifier
    match_timing_notifier: Notifier
    play_sound_notifier: Notifier
    realtime_score_notifier: Notifier
    reload_displays_notifier: Notifier
    score_posted_notifier: Notifier
    scoring_status_notifier: Notifier

    @staticmethod
    def get_audience_alliance_score_fields(
        alliance_score: RealtimeScore, alliance_score_summary: game.ScoreSummary
    ):
        fields = AudienceAllianceScoreFields(
            score=alliance_score.current_score,
            score_summary=alliance_score_summary,
            amplified_time_remaining_sec=alliance_score.amplified_time_remaining_sec,
        )
        return fields

    @staticmethod
    def get_rules_violated(red_fouls: list[game.Foul], blue_fouls: list[game.Foul]):
        rules = dict[int, game.Rule]()
        for foul in red_fouls:
            rules[foul.rule_id] = game.get_rule_by_id(foul.rule_id)

        for foul in blue_fouls:
            rules[foul.rule_id] = game.get_rule_by_id(foul.rule_id)

        return rules

    def __init__(self, *args, **kwargs):
        self.alliance_selection_notifier = Notifier(
            'alliance_selection', self.generate_alliance_selection_message
        )
        self.alliance_station_display_mode_notifier = Notifier(
            'alliance_station_display_mode', self.generate_alliance_station_display_mode_message
        )
        self.arena_status_notifier = Notifier('arena_status', self.generate_arena_status_message)
        self.audience_display_mode_notifier = Notifier(
            'audience_display_mode', self.generate_alliance_station_display_mode_message
        )
        self.display_configuration_notifier = Notifier(
            'display_configuration', self.generate_display_configuration_message
        )
        self.event_status_notifier = Notifier('event_status', self.generate_event_status_message)
        self.lower_third_notifier = Notifier('lower_third', self.generate_lower_third_message)
        self.match_load_notifier = Notifier('match_load', self.generate_match_load_message)
        self.match_time_notifier = Notifier('match_time', self.generate_match_time_message)
        self.match_timing_notifier = Notifier('match_timing', self.generate_match_timing_message)
        self.play_sound_notifier = Notifier('play_sound', None)
        self.realtime_score_notifier = Notifier(
            'realtime_score', self.generate_realtime_score_message
        )
        self.reload_displays_notifier = Notifier('reload_displays', None)
        self.score_posted_notifier = Notifier('score_posted', self.generate_score_posted_message)
        self.scoring_status_notifier = Notifier(
            'scoring_status', self.generate_scoring_status_message
        )
        super().__init__(*args, **kwargs)

    def generate_alliance_selection_message(self):
        return {
            'alliances': self.alliance_selection_alliances,
            'show_timer': self.alliance_selection_show_timer,
            'time_remaining_sec': self.alliance_selection_time_remaining_sec,
            'ranked_teams': self.alliance_selection_ranked_teams,
        }

    def generate_alliance_station_display_mode_message(self):
        return self.alliance_station_display_mode

    def generate_arena_status_message(self):
        return {
            'match_id': self.current_match.id,
            'alliance_stations': self.alliance_stations,
            'match_state': self.match_state,
            'can_start_match': self.check_can_start_match(),
            'access_point_status': self.access_point.status,
            # "switch_status": self.network_switch.status,
            # "plc_is_healthy": self.plc.is_healthy(),
            # "field_e_stop": self.plc.get_field_e_stop(),
            # "plc_armor_block_status": self.plc.get_armor_block_status(),
        }

    def generate_audience_display_mode_message(self):
        return self.audience_display_mode

    def generate_display_configuration_message(self):
        displays_copy = dict[str, Display]()
        for i, display in self.displays.items():
            displays_copy[i] = display

        return displays_copy

    def generate_event_status_message(self):
        return self.event_status

    def generate_lower_third_message(self):
        return {'lower_third': self.lower_third, 'show_lower_third': self.show_lower_third}

    def generate_match_load_message(self):
        teams = dict[str, models.Team]()
        all_team_ids = []

        for station, alliance_station in self.alliance_stations.items():
            teams[station] = alliance_station.team
            if alliance_station.team is not None:
                all_team_ids.append(alliance_station.team.id)

        match_result = models.read_match_result_for_match(self.current_match.id)
        is_replay = match_result is not None

        red_off_field_teams = []
        blue_off_field_team = []
        match_group = None
        if self.current_match.type == models.MatchType.PLAYOFF:
            match_group = self.playoff_tournament.MatchGroups()[
                self.current_match.playoff_match_group_id
            ]
            red_off_field_team_ids, blue_off_field_team_ids = models.read_off_field_team_ids(
                self.current_match
            )
            for team_id in red_off_field_team_ids:
                team = models.read_team_by_id(team_id)
                red_off_field_teams.append(team)
                all_team_ids.append(team_id)

            for team_id in blue_off_field_team_ids:
                team = models.read_team_by_id(team_id)
                blue_off_field_team.append(team)
                all_team_ids.append(team_id)

        rankings = dict[str, int]()
        for team_id in all_team_ids:
            ranking = models.read_ranking_for_team(team_id)
            if ranking is not None:
                rankings[team_id] = ranking.rank

        return {
            'match': self.current_match,
            'allow_substitution': self.current_match.should_allow_substitution(),
            'is_replay': is_replay,
            'teams': teams,
            'rankings': rankings,
            'matchup': match_group,
            'red_off_field_teams': red_off_field_teams,
            'blue_off_field_teams': blue_off_field_team,
            'break_description': self.break_description,
        }

    def generate_match_time_message(self):
        return MatchTimeMessage(
            match_state=self.match_state, match_time_sec=int(self.match_time_sec())
        )

    def generate_match_timing_message(self):
        return game.timing

    def generate_realtime_score_message(self):
        return {
            'red': self.get_audience_alliance_score_fields(
                self.red_realtime_score, self.red_score_summary()
            ),
            'blue': self.get_audience_alliance_score_fields(
                self.blue_realtime_score, self.blue_score_summary()
            ),
            'red_cards': self.red_realtime_score.cards,
            'blue_cards': self.blue_realtime_score.cards,
            'match_state': self.match_state,
        }

    def generate_score_posted_message(self):
        red_score_summary = self.saved_match_result.red_score_summary()
        blue_score_summary = self.saved_match_result.blue_score_summary()
        red_ranking_points = red_score_summary.bonus_ranking_points
        blue_ranking_points = blue_score_summary.bonus_ranking_points

        match self.saved_match.status:
            case game.MATCH_STATUS.red_won_match:
                red_ranking_points += 2
            case game.MATCH_STATUS.blue_won_match:
                blue_ranking_points += 2
            case game.MATCH_STATUS.tie_match:
                red_ranking_points += 1
                blue_ranking_points += 1

        # playoff
        red_wins = 0
        blue_wins = 0
        red_off_field_team_ids = []
        blue_off_field_team_ids = []
        if self.saved_match.type == models.MATCH_TYPE.playoff:
            matchup = self.playoff_tournament.MatchGroups()[self.saved_match.playoff_match_group_id]
            red_wins = matchup.red_alliance_wins
            blue_wins = matchup.blue_alliance_wins
            red_destination = matchup.red_alliance_destination()
            blue_destination = matchup.blue_alliance_destination()
            red_off_field_team_ids, blue_off_field_team_ids = models.read_off_field_team_ids(
                self.saved_match
            )

        red_rankings = {
            self.saved_match.red1: None,
            self.saved_match.red2: None,
            self.saved_match.red3: None,
        }
        blue_rankings = {
            self.saved_match.blue1: None,
            self.saved_match.blue2: None,
            self.saved_match.blue3: None,
        }
        for ranking in self.saved_rankings:
            if ranking.team_id in red_rankings:
                red_rankings[ranking.team_id] = ranking

            if ranking.team_id in blue_rankings:
                blue_rankings[ranking.team_id] = ranking

        return {
            'match': self.saved_match,
            'red_score_summary': red_score_summary,
            'blue_score_summary': blue_score_summary,
            'red_ranking_points': red_ranking_points,
            'blue_ranking_points': blue_ranking_points,
            'red_fouls': self.saved_match_result.red_score.fouls,
            'blue_fouls': self.saved_match_result.blue_score.fouls,
            'rules_violated': self.get_rules_violated(
                self.saved_match_result.red_score.fouls, self.saved_match_result.blue_score.fouls
            ),
            'red_cards': self.saved_match_result.red_cards,
            'blue_cards': self.saved_match_result.blue_cards,
            'red_rankings': red_rankings,
            'blue_rankings': blue_rankings,
            'red_off_field_team_ids': red_off_field_team_ids,
            'blue_off_field_team_ids': blue_off_field_team_ids,
            'red_won': self.saved_match.status == game.MATCH_STATUS.red_won_match,
            'blue_won': self.saved_match.status == game.MATCH_STATUS.blue_won_match,
            'red_wins': red_wins,
            'blue_wins': blue_wins,
            'red_destination': red_destination,
            'blue_destination': blue_destination,
        }

    def generate_scoring_status_message(self):
        return {
            'referee_score_ready': self.red_realtime_score.fouls_commited
            and self.blue_realtime_score.fouls_commited,
            'red_score_ready': self.alliance_post_match_score_ready('red'),
            'blue_score_ready': self.alliance_post_match_score_ready('blue'),
            'num_red_scoring_panels': self.scoring_panel_registry.get_num_panels('red'),
            'num_red_scoring_panels_ready': self.scoring_panel_registry.get_num_score_commited(
                'red'
            ),
            'num_blue_scoring_panels': self.scoring_panel_registry.get_num_panels('blue'),
            'num_blue_scoring_panels_ready': self.scoring_panel_registry.get_num_score_commited(
                'blue'
            ),
        }
