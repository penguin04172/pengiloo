import asyncio
import logging
from datetime import datetime, timedelta

import game
import models
import network
import playoff
from models.event import Event
from network.access_point import AccessPoint

from .arena_notifiers import ArenaNotifiers, ArenaNotifiersMixin
from .display import Display, DisplayMixin
from .driver_station_connection import DriverStationConnection, DriverStationConnectionMixin
from .event_status import EventStatusMixin
from .realtime_score import RealtimeScore
from .scoring_panel_register import ScoringPanelRegister
from .specs import (
    ARENA_LOOP_PERIOD_MS,
    ARENA_LOOP_WARNING_US,
    DS_PACKET_PERIOD_MS,
    DS_PACKET_WARNING_MS,
    MATCH_END_SCORE_DWELL_SEC,
    PERIODIC_TASK_PERIOD_SEC,
    POST_TIMEOUT_SEC,
    PRE_LOAD_NEXT_MATCH_DELAY_SEC,
    SCHEDULED_BREAK_DELAY_SEC,
    MatchState,
)
from .team_sign import TeamSigns


class AllianceStation:
    ds_conn: DriverStationConnection = None
    ethernet: bool = False
    a_stop: bool = False
    e_stop: bool = False
    bypass: bool = False
    team: models.Team = None
    wifi_status: network.TeamWifiStatus = network.TeamWifiStatus()
    a_stop_reset: bool = False


class Arena(DisplayMixin, EventStatusMixin, DriverStationConnectionMixin, ArenaNotifiersMixin):
    event: Event
    access_point: AccessPoint = AccessPoint()
    # network_switch:
    # plc:
    # tba_client: tba
    # nexus_client:
    # blackmagic_client:
    alliance_stations: dict[str, AllianceStation]
    team_signs: TeamSigns
    arena_notifiers: ArenaNotifiers = ArenaNotifiers()
    scoring_panel_registry: ScoringPanelRegister
    match_state: MatchState
    last_match_state: MatchState
    current_match: models.MatchOut
    match_start_time: datetime
    last_match_time_sec: float
    red_realtime_score: RealtimeScore
    blue_realtime_score: RealtimeScore
    last_ds_packet_time: datetime = datetime.fromtimestamp(0)
    last_period_task_time: datetime = datetime.fromtimestamp(0)
    field_reset: bool = False
    audience_display_mode: str = 'blank'
    saved_match: models.MatchOut
    saved_match_result: models.MatchResult
    saved_rankings: game.Rankings
    alliance_station_display_mode: str = ''
    alliance_selection_alliances: list[models.Alliance] = []
    alliance_selection_ranked_teams: list[models.AllianceSelectionRankedTeam] = []
    alliance_selection_show_timer: bool = False
    alliance_selection_time_remaining_sec: int = 0
    playoff_tournament: playoff.PlayoffTournament
    lower_third: models.LowerThird = models.LowerThird()
    show_lower_third: bool = False
    mute_match_sounds: bool = False
    match_aborted: bool = False
    sounds_played: set[game.MatchSounds] = set()
    break_description: str = ''
    preloaded_teams: list[models.Team] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def new_arena(cls):
        arena = cls()
        arena.alliance_stations = dict[str, AllianceStation]()
        arena.alliance_stations['R1'] = AllianceStation()
        arena.alliance_stations['R2'] = AllianceStation()
        arena.alliance_stations['R3'] = AllianceStation()
        arena.alliance_stations['B1'] = AllianceStation()
        arena.alliance_stations['B2'] = AllianceStation()
        arena.alliance_stations['B3'] = AllianceStation()

        arena.displays = dict[str, Display]()
        arena.team_signs = TeamSigns()

        await arena.load_settings()

        arena.scoring_panel_registry = ScoringPanelRegister()

        arena.match_state = MatchState.PRE_MATCH
        await arena.load_test_match()
        arena.last_match_time_sec = 0
        arena.last_match_state = -1

        arena.audience_display_mode = 'blank'
        arena.saved_match = models.MatchOut(id=0, type=models.MatchType.TEST, type_order=0)
        arena.saved_match_result = models.MatchResult(match_id=0, match_type=models.MatchType.TEST)
        arena.alliance_station_display_mode = 'Match'
        return arena

    async def load_settings(self):
        settings = models.read_event_settings()
        self.event = settings

        self.team_signs.red_1.set_id(settings.team_sign_red_1_id)
        self.team_signs.red_2.set_id(settings.team_sign_red_2_id)
        self.team_signs.red_3.set_id(settings.team_sign_red_3_id)
        self.team_signs.red_timer.set_id(settings.team_sign_red_timer_id)
        self.team_signs.blue_1.set_id(settings.team_sign_blue_1_id)
        self.team_signs.blue_2.set_id(settings.team_sign_blue_2_id)
        self.team_signs.blue_3.set_id(settings.team_sign_blue_3_id)
        self.team_signs.blue_timer.set_id(settings.team_sign_blue_timer_id)

        access_point_wifi_status = [
            self.alliance_stations[station].wifi_status
            for station in ['R1', 'R2', 'R3', 'B1', 'B2', 'B3']
        ]
        self.access_point.set_settings(
            settings.ap_address,
            settings.ap_password,
            settings.ap_channel,
            settings.network_security_enabled,
            access_point_wifi_status,
        )

        # self.network_switch
        # self.plc
        # self.tba_client
        # self.nexus_client
        # self.blackmagic_client

        game.timing.warmup_duration_sec = settings.warmup_duration_sec
        game.timing.auto_duration_sec = settings.auto_duration_sec
        game.timing.pause_duration_sec = settings.pause_duration_sec
        game.timing.teleop_duration_sec = settings.teleop_duration_sec
        game.timing.warning_remaining_duration_sec = settings.warning_remaining_duration_sec
        game.update_match_sounds()
        await self.match_timing_notifier.notify()

        game.specific.melody_bonus_threshold_with_coop = settings.melody_bonus_threshold_with_coop
        game.specific.melody_bonus_threshold_without_coop = (
            settings.melody_bonus_threshold_without_coop
        )
        game.specific.amplification_note_limit = settings.amplification_note_limit
        game.specific.amplification_duration_sec = settings.amplification_duration_sec

        self.create_playoff_tournament()
        self.update_playoff_tournament()

    def create_playoff_tournament(self):
        self.playoff_tournament = playoff.PlayoffTournament(
            self.event.playoff_type, self.event.num_playoff_alliance
        )

    def create_playoff_matches(self, start_time: datetime):
        return self.playoff_tournament.create_match_and_breaks(start_time)

    def update_playoff_tournament(self):
        alliances = models.read_all_alliances()
        if len(alliances) > 0:
            return self.playoff_tournament.update_matches(alliances)

    async def load_match(self, match: models.MatchOut):
        if (
            self.match_state != MatchState.PRE_MATCH
            and self.match_state != MatchState.TIMEOUT_ACTIVE
        ):
            raise RuntimeError('Cannot load match while match is in progress')

        self.current_match = match

        load_by_nexus = False
        # load nexus
        if not load_by_nexus:
            self.assign_team(match.red1, 'R1')
            self.assign_team(match.red2, 'R2')
            self.assign_team(match.red3, 'R3')
            self.assign_team(match.blue1, 'B1')
            self.assign_team(match.blue2, 'B2')
            self.assign_team(match.blue3, 'B3')

            self.setup_network(
                [
                    self.alliance_stations[station].team
                    for station in ['R1', 'R2', 'R3', 'B1', 'B2', 'B3']
                ],
                False,
            )

        self.sounds_played = set[game.MatchSounds]()
        self.red_realtime_score = RealtimeScore()
        self.blue_realtime_score = RealtimeScore()
        self.scoring_panel_registry.reset_score_commited()
        # self.plc.reset_match()

        # Notify any listeners that the match has been loaded
        await self.match_load_notifier.notify()
        await self.realtime_score_notifier.notify()
        self.alliance_station_display_mode = 'match'
        await self.alliance_station_display_mode_notifier.notify()
        await self.scoring_status_notifier.notify()

    async def load_test_match(self):
        return await self.load_match(
            models.MatchOut(
                id=0,
                type=models.MatchType.TEST,
                type_order=0,
                short_name='T',
                long_name='Test Match',
            )
        )

    async def load_next_match(self, start_scheduled_break: bool):
        next_match = self.get_next_match(False)
        if next_match is None:
            return await self.load_test_match()

        await self.load_match(next_match)
        if start_scheduled_break:
            scheduled_break = models.read_scheduled_break_by_match_type_order(
                next_match.type, next_match.type_order
            )
            if scheduled_break is not None:

                async def scheduled_break_delay():
                    await asyncio.sleep(SCHEDULED_BREAK_DELAY_SEC)
                    self.start_timeout(scheduled_break.description, scheduled_break.duration_sec)

                asyncio.create_task(scheduled_break_delay())

    async def substitute_team(
        self, red1: int, red2: int, red3: int, blue1: int, blue2: int, blue3: int
    ):
        if not self.current_match.should_allow_substitution():
            raise ValueError('Match does not allow substitution')

        self.validate_teams([red1, red2, red3, blue1, blue2, blue3])
        self.assign_team(red1, 'R1')
        self.assign_team(red2, 'R2')
        self.assign_team(red3, 'R3')
        self.assign_team(blue1, 'B1')
        self.assign_team(blue2, 'B2')
        self.assign_team(blue3, 'B3')

        self.current_match.red1 = red1
        self.current_match.red2 = red2
        self.current_match.red3 = red3
        self.current_match.blue1 = blue1
        self.current_match.blue2 = blue2
        self.current_match.blue3 = blue3

        self.setup_network(
            [
                self.alliance_stations[station].team
                for station in ['R1', 'R2', 'R3', 'B1', 'B2', 'B3']
            ],
            False,
        )
        await self.match_load_notifier.notify()

        if self.current_match.type != models.MatchType.TEST:
            models.update_match(self.current_match)

    async def start_match(self):
        can_start = self.check_can_start_match()
        if can_start:
            self.current_match.started_at = datetime.now()
            if self.current_match.type != models.MatchType.TEST:
                models.update_match(self.current_match)

            await self.update_cycle_time(self.current_match.started_at)

            for alliance_station in self.alliance_stations.values():
                if alliance_station.ds_conn is not None:
                    alliance_station.ds_conn.signal_match_start(
                        self.current_match, alliance_station.wifi_status
                    )

                if (
                    alliance_station.team is not None
                    and not alliance_station.team.has_connected
                    and alliance_station.ds_conn is not None
                    and alliance_station.ds_conn.robot_linked
                ):
                    alliance_station.team.has_connected = True
                    models.update_team(alliance_station.team)

            self.match_state = MatchState.START_MATCH
            return
        else:
            raise RuntimeError('Cannot start match')

    async def abort_match(self):
        if self.match_state in [
            MatchState.PRE_MATCH,
            MatchState.POST_MATCH,
            MatchState.POST_TIMEOUT,
        ]:
            raise RuntimeError('Cannot abort match while match is not in progress')

        if self.match_state == MatchState.TIMEOUT_ACTIVE:
            self.match_start_time = datetime.now() - timedelta(
                seconds=game.timing.timeout_duration_sec
            )
            return

        if self.match_state != MatchState.WARMUP_PERIOD:
            self.play_sound('abort')

        self.match_state = MatchState.POST_MATCH
        self.match_aborted = True
        self.audience_display_mode = 'blank'
        await self.audience_display_mode_notifier.notify()
        self.alliance_station_display_mode = 'logo'
        await self.alliance_station_display_mode_notifier.notify()

        # stop blackmagic
        return

    def reset_match(self):
        if self.match_state not in [
            MatchState.PRE_MATCH,
            MatchState.POST_MATCH,
            MatchState.TIMEOUT_ACTIVE,
        ]:
            raise RuntimeError('Cannot reset match while match is in progress')

        if self.match_state != MatchState.TIMEOUT_ACTIVE:
            self.match_state = MatchState.PRE_MATCH

        self.match_aborted = False
        self.alliance_stations['R1'].bypass = False
        self.alliance_stations['R2'].bypass = False
        self.alliance_stations['R3'].bypass = False
        self.alliance_stations['B1'].bypass = False
        self.alliance_stations['B2'].bypass = False
        self.alliance_stations['B3'].bypass = False
        self.mute_match_sounds = False
        return

    async def start_timeout(self, description: str, duration_sec: int):
        if self.match_state != MatchState.PRE_MATCH:
            raise RuntimeError(
                'Cannot start timeout while match is in progress or with results pending'
            )

        game.timing.timeout_duration_sec = duration_sec
        game.update_match_sounds()
        self.sounds_played = set[game.MatchSounds]()
        await self.match_timing_notifier.notify()
        self.break_description = description
        await self.match_load_notifier.notify()
        self.match_state = MatchState.TIMEOUT_ACTIVE
        self.match_start_time = datetime.now()
        self.last_match_time_sec = -1
        self.alliance_station_display_mode = 'timeout'
        await self.alliance_station_display_mode_notifier.notify()

    async def set_audience_display_mode(self, mode: str):
        if self.audience_display_mode != mode:
            self.audience_display_mode = mode
            await self.audience_display_mode_notifier.notify()
            if mode == 'score':
                self.play_sound('match_result')

    async def set_alliance_station_display_mode(self, mode: str):
        if self.alliance_station_display_mode != mode:
            self.alliance_station_display_mode = mode
            await self.alliance_station_display_mode_notifier.notify()

    def match_time_sec(self):
        if self.match_state in [
            MatchState.PRE_MATCH,
            MatchState.START_MATCH,
            MatchState.POST_MATCH,
        ]:
            return 0.0
        else:
            return (datetime.now() - self.match_start_time).total_seconds()

    async def update(self):
        auto = False
        enabled = False
        send_ds_packet = False
        match_time_sec = self.match_time_sec()

        if self.match_state == MatchState.PRE_MATCH:
            auto = True
            enabled = False

        elif self.match_state == MatchState.START_MATCH:
            self.match_start_time = datetime.now()
            self.last_match_time_sec = -1
            auto = True
            self.audience_display_mode = 'match'
            await self.audience_display_mode_notifier.notify()
            self.alliance_station_display_mode = 'match'
            await self.alliance_station_display_mode_notifier.notify()

            # start blackmagic
            if game.timing.warmup_duration_sec > 0:
                self.match_state = MatchState.WARMUP_PERIOD
                enabled = False
                send_ds_packet = False
            else:
                self.match_state = MatchState.AUTO_PERIOD
                enabled = True
                send_ds_packet = True

            # reset plc
            self.field_reset = False

        elif self.match_state == MatchState.WARMUP_PERIOD:
            auto = True
            enabled = False
            if match_time_sec >= game.timing.warmup_duration_sec:
                self.match_state = MatchState.AUTO_PERIOD
                auto = True
                enabled = True
                send_ds_packet = True

        elif self.match_state == MatchState.AUTO_PERIOD:
            auto = True
            enabled = True
            if match_time_sec >= game.timing.get_duration_to_auto_end():
                auto = False
                send_ds_packet = True
                if game.timing.pause_duration_sec > 0:
                    self.match_state = MatchState.PAUSE_PERIOD
                    enabled = False
                else:
                    self.match_state = MatchState.TELEOP_PERIOD
                    enabled = True

        elif self.match_state == MatchState.PAUSE_PERIOD:
            auto = False
            enabled = False
            if match_time_sec >= game.timing.get_duration_to_teleop_start():
                self.match_state = MatchState.TELEOP_PERIOD
                auto = False
                enabled = True
                send_ds_packet = True

        elif self.match_state == MatchState.TELEOP_PERIOD:
            auto = False
            enabled = True
            if match_time_sec >= game.timing.get_duration_to_teleop_end():
                self.match_state = MatchState.POST_MATCH
                auto = False
                enabled = False
                send_ds_packet = True
                # stop blackmagic

                async def post_match_dwell():
                    await asyncio.sleep(MATCH_END_SCORE_DWELL_SEC)
                    self.audience_display_mode = 'blank'
                    await self.audience_display_mode_notifier.notify()
                    self.alliance_station_display_mode = 'logo'
                    await self.alliance_station_display_mode_notifier.notify()

                asyncio.create_task(post_match_dwell())

                async def pre_load_next_match_delay():
                    await asyncio.sleep(PRE_LOAD_NEXT_MATCH_DELAY_SEC)
                    self.pre_load_next_match()

                asyncio.create_task(pre_load_next_match_delay())

        elif self.match_state == MatchState.TIMEOUT_ACTIVE:
            if match_time_sec >= game.timing.timeout_duration_sec:
                self.match_state = MatchState.POST_TIMEOUT

                async def post_timeout_dwell():
                    await asyncio.sleep(MATCH_END_SCORE_DWELL_SEC)
                    self.audience_display_mode = 'blank'
                    await self.audience_display_mode_notifier.notify()
                    self.alliance_station_display_mode = 'logo'
                    await self.alliance_station_display_mode_notifier.notify()

                asyncio.create_task(post_timeout_dwell())
        elif self.match_state == MatchState.POST_TIMEOUT:
            if match_time_sec >= game.timing.timeout_duration_sec + POST_TIMEOUT_SEC:
                self.match_state = MatchState.PRE_MATCH

        if (
            int(match_time_sec) != int(self.last_match_time_sec)
            or self.match_state != self.last_match_state
        ):
            await self.match_time_notifier.notify()

        ms_since_last_ds_packet = (datetime.now() - self.last_ds_packet_time).total_seconds() * 1000
        if send_ds_packet or ms_since_last_ds_packet > DS_PACKET_PERIOD_MS:
            if (
                ms_since_last_ds_packet >= DS_PACKET_WARNING_MS
                and self.last_ds_packet_time > datetime.min
            ):
                logging.warning(f'Last DS packet was {ms_since_last_ds_packet}ms ago')
            self.send_ds_packet(auto, enabled)
            await self.arena_status_notifier.notify()

        self.handle_sounds(match_time_sec)
        # self.handle_plc_io()
        self.team_signs.update(self)

        self.last_match_time_sec = match_time_sec
        self.last_match_state = self.match_state

    async def run(self):
        task_list = []
        # task_list.append(asyncio.create_task(self.listen_for_driver_stations()))
        # task_list.append(asyncio.create_task(self.listen_for_ds_udp_packets()))
        # task_list.append(asyncio.create_task(self.access_point.run()))
        # run plc
        self.running = True

        while self.running:
            loop_start_time = datetime.now()
            await self.update()
            if (
                datetime.now() - self.last_period_task_time
            ).total_seconds() > PERIODIC_TASK_PERIOD_SEC:
                self.last_period_task_time = datetime.now()
                asyncio.create_task(self.run_periodic_task())

            loop_run_time = (datetime.now() - loop_start_time).total_seconds() * 1000000
            if loop_run_time > ARENA_LOOP_WARNING_US:
                logging.warning(f'Arena loop took a long time: {loop_run_time}us')

            await asyncio.sleep(ARENA_LOOP_PERIOD_MS / 1000)

        for task in task_list:
            task.cancel()

        await asyncio.gather(*task_list, return_exceptions=True)

    def red_score_summary(self):
        return self.red_realtime_score.current_score.summarize(
            self.blue_realtime_score.current_score
        )

    def blue_score_summary(self):
        return self.blue_realtime_score.current_score.summarize(
            self.red_realtime_score.current_score
        )

    def validate_teams(self, team_ids: list[int]):
        for team_id in team_ids:
            if team_id == 0:
                continue

            team = models.read_team_by_id(team_id)
            if team is None:
                raise ValueError(f'Team {team_id} not present at the event')

    def assign_team(self, team_id: int, station: str):
        if station not in self.alliance_stations:
            raise ValueError(f'Invalid alliance station {station}')

        # Force A-Stop reset if it is already pressed
        self.alliance_stations[station].a_stop_reset = True

        ds_conn = self.alliance_stations[station].ds_conn
        if ds_conn is not None and ds_conn.team_id == team_id:
            return

        if ds_conn is not None:
            ds_conn.close()
            self.alliance_stations[station].team = None
            self.alliance_stations[station].ds_conn = None

        if team_id == 0:
            self.alliance_stations[station].team = None
            return

        team = models.read_team_by_id(team_id)
        if team is None:
            team = models.Team(id=team_id)

        self.alliance_stations[station].team = team
        return

    def get_next_match(self, exclude_current: bool):
        if self.current_match.type == models.MatchType.TEST:
            return None

        matches = models.read_matches_by_type(self.current_match.type, False)
        for match in matches:
            if not match.is_complete() and not (
                exclude_current and match.id == self.current_match.id
            ):
                return match

    def pre_load_next_match(self):
        if self.match_state != MatchState.POST_MATCH:
            return

        next_match = self.get_next_match(True)
        if next_match is None:
            return

        team_ids = [
            next_match.red1,
            next_match.red2,
            next_match.red3,
            next_match.blue1,
            next_match.blue2,
            next_match.blue3,
        ]

        # if nexus

        teams = [models.read_team_by_id(team_id) for team_id in team_ids]
        self.setup_network(teams, True)
        self.team_signs.set_next_match_teams(teams)

    def setup_network(self, teams: list[models.Team], is_preload: bool):
        if is_preload:
            self.preloaded_teams = teams
        elif self.preloaded_teams is not None:
            preloaded_teams = self.preloaded_teams
            self.preloaded_teams = None
            if preloaded_teams == teams:
                return

        if self.event.network_security_enabled:
            try:
                self.access_point.configure_team_wifi(teams)
            except RuntimeError as e:
                logging.error(f'Failed to configure team wifi: {e}')
                return

            # network switch

    def check_can_start_match(self):
        if self.match_state != MatchState.PRE_MATCH:
            return False

        result = self.check_alliance_stations_ready('R1', 'R2', 'R3', 'B1', 'B2', 'B3')
        if not result:
            return False

        return True

    def check_alliance_stations_ready(self, *args):
        for station in args:
            alliance_station = self.alliance_stations.get(station, None)
            if alliance_station is not None:
                if alliance_station.e_stop:
                    return False
                if not alliance_station.a_stop_reset:
                    return False
                if not alliance_station.bypass:
                    if (
                        alliance_station.ds_conn is None
                        or not alliance_station.ds_conn.robot_linked
                    ):
                        return False
        return True

    def send_ds_packet(self, auto: bool, enabled: bool):
        for alliance_station in self.alliance_stations.values():
            ds_conn = alliance_station.ds_conn
            if ds_conn is not None:
                ds_conn.auto = auto
                ds_conn.enabled = (
                    enabled
                    and not alliance_station.e_stop
                    and not (auto and alliance_station.a_stop)
                    and not alliance_station.bypass
                )
                ds_conn.e_stop = alliance_station.e_stop
                ds_conn.a_stop = alliance_station.a_stop
                ds_conn.update(self)

        self.last_ds_packet_time = datetime.now()

    def get_assigned_alliance_station(self, team_id):
        for station, alliance_station in self.alliance_stations.items():
            if alliance_station.team is not None and alliance_station.team.id == team_id:
                return station

        return ''

    def handle_team_stop(self, station: str, e_stop: bool, a_stop: bool):
        alliance_station = self.alliance_stations[station]

        if e_stop:
            alliance_station.e_stop = True
        elif self.match_time_sec() == 0:
            alliance_station.e_stop = False

        if a_stop:
            alliance_station.a_stop = True
        elif self.match_state != MatchState.AUTO_PERIOD:
            alliance_station.a_stop = False
            alliance_station.a_stop_reset = True

    def handle_sounds(self, match_time_sec: float):
        if self.match_state in [
            MatchState.PRE_MATCH,
            MatchState.TIMEOUT_ACTIVE,
            MatchState.POST_TIMEOUT,
        ]:
            return

        for sound in game.sounds:
            if sound.match_time_sec < 0:
                continue

            if sound not in self.sounds_played:
                if (
                    match_time_sec >= sound.match_time_sec
                    and match_time_sec - sound.match_time_sec < 1
                ):
                    self.play_sound(sound.name)
                    self.sounds_played.add(sound)

    def play_sound(self, name: str):
        if not self.mute_match_sounds:
            self.play_sound_notifier.notify_with_message(name)

    def alliance_post_match_score_ready(self, alliance: str):
        num_panels = self.scoring_panel_registry.get_num_panels(alliance)
        return (
            num_panels > 0
            and self.scoring_panel_registry.get_num_score_commited(alliance) >= num_panels
        )

    async def run_periodic_task(self):
        await self.update_early_late_message()
        await self.purge_disconnected_displays()
