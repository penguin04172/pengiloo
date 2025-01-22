import asyncio
import unittest
from datetime import datetime, timedelta

import game
import models
import playoff

from .driver_station_connection import DriverStationConnection
from .specs import POST_TIMEOUT_SEC, MatchState
from .test_helper import setup_test_arena_with_parameter


def create_test_alliance(allianceCount: int):
    for i in range(1, allianceCount + 1):
        alliance = models.Alliance(
            id=i,
            team_ids=[100 * i + 1, 100 * i + 2, 100 * i + 3, 100 * i + 4],
            line_up=[100 * i + 2, 100 * i + 1, 100 * i + 3],
        )
        alliance = models.create_alliance(alliance)


class TestArena(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
        models.db.generate_mapping(create_tables=True)

    @classmethod
    def tearDownClass(cls) -> None:
        models.db.disconnect()

    def setUp(self) -> None:
        models.db.create_tables(True)

    def tearDown(self) -> None:
        models.db.drop_all_tables(with_all_data=True)

    def test_assign_team(self):
        arena = setup_test_arena_with_parameter(self)

        team = models.Team(id=123)
        models.create_team(team)
        models.create_team(models.Team(id=234))

        arena.assign_team(123, 'B1')
        self.assertEqual(arena.alliance_stations['B1'].team, team)
        dummy_ds = DriverStationConnection(123)
        arena.alliance_stations['B1'].ds_conn = dummy_ds

        arena.assign_team(123, 'B1')
        self.assertEqual(arena.alliance_stations['B1'].team, team)
        self.assertIsNotNone(arena.alliance_stations['B1'])
        self.assertEqual(arena.alliance_stations['B1'].ds_conn, dummy_ds)

        arena.assign_team(234, 'B1')
        self.assertNotEqual(arena.alliance_stations['B1'].team, team)
        self.assertIsNone(arena.alliance_stations['B1'].ds_conn)

        arena.assign_team(0, 'R2')
        self.assertIsNone(arena.alliance_stations['R2'].team)
        self.assertIsNone(arena.alliance_stations['R2'].ds_conn)

        with self.assertRaises(ValueError):
            arena.assign_team(123, 'R4')

    def test_arena_check_can_start_match(self):
        arena = setup_test_arena_with_parameter(self)

        self.assertFalse(arena.check_can_start_match())
        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].bypass = True
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].bypass = True
        self.assertFalse(arena.check_can_start_match())

        arena.alliance_stations['B3'].bypass = True
        self.assertTrue(arena.check_can_start_match())

        # PLC

    def test_arena_match_flow(self):
        arena = setup_test_arena_with_parameter(self)

        models.create_team(models.Team(id=123))
        arena.assign_team(123, 'B3')
        dummy_ds = DriverStationConnection(123, 'B3')
        arena.alliance_stations['B3'].ds_conn = dummy_ds

        self.assertEqual(arena.match_state, MatchState.PRE_MATCH)
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=300)
        asyncio.run(arena.update())
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        last_packet_count = arena.alliance_stations['B3'].ds_conn.packet_count
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=10)
        asyncio.run(arena.update())
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.packet_count, last_packet_count)
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.packet_count, last_packet_count + 1)

        game.timing.warmup_duration_sec = 5
        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].bypass = True
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].bypass = True
        arena.alliance_stations['B3'].ds_conn.robot_linked = True
        asyncio.run(arena.start_match())
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.WARMUP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.WARMUP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        arena.match_start_time = datetime.now() - timedelta(seconds=game.timing.warmup_duration_sec)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.AUTO_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, True)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.AUTO_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, True)
        arena.match_start_time = datetime.now() - timedelta(
            seconds=game.timing.warmup_duration_sec + game.timing.auto_duration_sec
        )
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.PAUSE_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.PAUSE_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        arena.match_start_time = datetime.now() - timedelta(
            seconds=game.timing.warmup_duration_sec
            + game.timing.auto_duration_sec
            + game.timing.pause_duration_sec
        )
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, True)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, True)

        arena.alliance_stations['B3'].e_stop = True
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        arena.alliance_stations['B3'].bypass = True
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        arena.alliance_stations['B3'].e_stop = False
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        arena.alliance_stations['B3'].bypass = False
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.TELEOP_PERIOD)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, True)

        arena.match_start_time = datetime.now() - timedelta(
            seconds=game.timing.warmup_duration_sec
            + game.timing.auto_duration_sec
            + game.timing.pause_duration_sec
            + game.timing.teleop_duration_sec
        )
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.POST_MATCH)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.POST_MATCH)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, False)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)

        arena.alliance_stations['R1'].bypass = True
        arena.reset_match()
        arena.last_ds_packet_time = arena.last_ds_packet_time - timedelta(milliseconds=550)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.PRE_MATCH)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.auto, True)
        self.assertEqual(arena.alliance_stations['B3'].ds_conn.enabled, False)
        self.assertEqual(arena.alliance_stations['R1'].bypass, False)

    def test_arena_state_enforcement(self):
        arena = setup_test_arena_with_parameter(self)

        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].bypass = True
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].bypass = True
        arena.alliance_stations['B3'].bypass = True

        asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.abort_match())

        asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            arena.reset_match()

        arena.match_state = MatchState.AUTO_PERIOD
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            arena.reset_match()

        arena.match_state = MatchState.PAUSE_PERIOD
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            arena.reset_match()

        arena.match_state = MatchState.TELEOP_PERIOD
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            arena.reset_match()

        arena.match_state = MatchState.POST_MATCH
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.abort_match())

        arena.reset_match()
        self.assertEqual(arena.match_state, MatchState.PRE_MATCH)
        arena.reset_match()
        asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))

    def test_match_start_robot_link_enforcement(self):
        arena = setup_test_arena_with_parameter(self)

        models.create_team(models.Team(id=101))
        models.create_team(models.Team(id=102))
        models.create_team(models.Team(id=103))
        models.create_team(models.Team(id=104))
        models.create_team(models.Team(id=105))
        models.create_team(models.Team(id=106))
        match = models.MatchOut(
            type=models.MatchType.TEST,
            type_order=0,
            red1=101,
            red2=102,
            red3=103,
            blue1=104,
            blue2=105,
            blue3=106,
        )
        models.create_match(match)

        asyncio.run(arena.load_match(match))
        arena.alliance_stations['R1'].ds_conn = DriverStationConnection(101, 'R1')
        arena.alliance_stations['R2'].ds_conn = DriverStationConnection(102, 'R2')
        arena.alliance_stations['R3'].ds_conn = DriverStationConnection(103, 'R3')
        arena.alliance_stations['B1'].ds_conn = DriverStationConnection(104, 'B1')
        arena.alliance_stations['B2'].ds_conn = DriverStationConnection(105, 'B2')
        arena.alliance_stations['B3'].ds_conn = DriverStationConnection(106, 'B3')

        for station in arena.alliance_stations.values():
            station.ds_conn.robot_linked = True

        asyncio.run(arena.start_match())
        arena.match_state = MatchState.PRE_MATCH

        arena.alliance_stations['R1'].e_stop = True
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())

        arena.alliance_stations['R1'].e_stop = False
        arena.alliance_stations['R1'].a_stop_reset = False
        arena.alliance_stations['R1'].a_stop = True
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())

        arena.alliance_stations['R1'].a_stop_reset = True
        arena.alliance_stations['R1'].ds_conn.robot_linked = False
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())

        arena.alliance_stations['R1'].bypass = True
        asyncio.run(arena.start_match())
        arena.alliance_stations['R1'].bypass = False
        arena.match_state = MatchState.PRE_MATCH

        arena.assign_team(0, 'R1')
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        arena.alliance_stations['R1'].bypass = True
        asyncio.run(arena.start_match())
        arena.match_state = MatchState.PRE_MATCH

        asyncio.run(arena.load_match(models.MatchOut(type=models.MatchType.TEST, type_order=0)))
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].bypass = True
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].bypass = True
        arena.alliance_stations['B3'].bypass = True
        arena.alliance_stations['B3'].e_stop = True
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_match())
        arena.alliance_stations['B3'].e_stop = False
        asyncio.run(arena.start_match())

    def test_load_next_match(self):
        arena = setup_test_arena_with_parameter(self)

        models.create_team(models.Team(id=123))
        pratice_match1 = models.MatchOut(type=models.MatchType.PRACTICE, type_order=1)
        pratice_match2 = models.MatchOut(
            type=models.MatchType.PRACTICE, type_order=2, status=game.MatchStatus.RED_WON_MATCH
        )
        pratice_match3 = models.MatchOut(type=models.MatchType.PRACTICE, type_order=3)
        pratice_match1 = models.create_match(pratice_match1)
        pratice_match2 = models.create_match(pratice_match2)
        pratice_match3 = models.create_match(pratice_match3)
        qual_match1 = models.MatchOut(
            type=models.MatchType.QUALIFICATION,
            type_order=1,
            status=game.MatchStatus.BLUE_WON_MATCH,
        )
        qual_match2 = models.MatchOut(type=models.MatchType.QUALIFICATION, type_order=2)
        qual_match1 = models.create_match(qual_match1)
        qual_match2 = models.create_match(qual_match2)

        self.assertEqual(arena.current_match.id, 0)
        asyncio.run(arena.substitute_team(123, 0, 0, 0, 0, 0))
        arena.current_match.status = game.MatchStatus.TIE_MATCH
        asyncio.run(arena.load_next_match(False))
        self.assertEqual(arena.current_match.id, 0)
        self.assertEqual(arena.current_match.red1, 0)
        self.assertEqual(arena.current_match.is_complete(), False)

        asyncio.run(arena.load_match(pratice_match2))
        asyncio.run(arena.load_next_match(False))
        self.assertEqual(arena.current_match.id, pratice_match1.id)
        pratice_match1.status = game.MatchStatus.RED_WON_MATCH
        models.update_match(pratice_match1)
        asyncio.run(arena.load_next_match(False))
        self.assertEqual(arena.current_match.id, pratice_match3.id)
        pratice_match3.status = game.MatchStatus.BLUE_WON_MATCH
        models.update_match(pratice_match3)
        asyncio.run(arena.load_next_match(False))
        self.assertEqual(arena.current_match.id, 0)
        self.assertEqual(arena.current_match.type, models.MatchType.TEST)

        asyncio.run(arena.load_match(qual_match1))
        asyncio.run(arena.load_next_match(False))
        self.assertEqual(arena.current_match.id, qual_match2.id)

    def test_substitute_team(self):
        arena = setup_test_arena_with_parameter(self)

        create_test_alliance(2)
        arena.playoff_tournament = playoff.PlayoffTournament(
            models.PlayoffType.SINGLE_ELIMINATION, 2
        )

        models.create_team(models.Team(id=101))
        models.create_team(models.Team(id=102))
        models.create_team(models.Team(id=103))
        models.create_team(models.Team(id=104))
        models.create_team(models.Team(id=105))
        models.create_team(models.Team(id=106))
        models.create_team(models.Team(id=107))

        asyncio.run(arena.substitute_team(0, 0, 0, 101, 0, 0))
        self.assertEqual(arena.current_match.blue1, 101)
        self.assertEqual(arena.alliance_stations['B1'].team.id, 101)
        with self.assertRaises(ValueError):
            arena.assign_team(104, 'R4')

        match = models.Match(
            type=models.MatchType.PRACTICE,
            type_order=1,
            red1=101,
            red2=102,
            red3=103,
            blue1=104,
            blue2=105,
            blue3=106,
        )
        match = models.create_match(match)
        asyncio.run(arena.load_match(match))
        asyncio.run(arena.substitute_team(107, 102, 103, 104, 105, 106))
        self.assertEqual(arena.current_match.red1, 107)
        self.assertEqual(arena.alliance_stations['R1'].team.id, 107)
        match_result = models.MatchResult(match_id=match.id, match_type=models.MatchType.PRACTICE)

        match = models.Match(
            type=models.MatchType.QUALIFICATION,
            type_order=1,
            red1=101,
            red2=102,
            red3=103,
            blue1=104,
            blue2=105,
            blue3=106,
        )
        match = models.create_match(match)
        asyncio.run(arena.load_match(match))
        with self.assertRaises(ValueError):
            asyncio.run(arena.substitute_team(107, 102, 103, 104, 105, 106))
        match = models.Match(
            type=models.MatchType.PLAYOFF,
            type_order=1,
            playoff_match_group_id='F',
            playoff_blue_alliance=1,
            playoff_red_alliance=2,
            red1=101,
            red2=102,
            red3=103,
            blue1=104,
            blue2=105,
            blue3=106,
        )
        match = models.create_match(match)
        asyncio.run(arena.load_match(match))
        asyncio.run(arena.substitute_team(107, 102, 103, 104, 105, 106))

        with self.assertRaises(ValueError):
            asyncio.run(arena.substitute_team(101, 102, 103, 104, 105, 108))

    def test_arena_timeout(self):
        arena = setup_test_arena_with_parameter(self)
        create_test_alliance(2)

        timeout_duration_sec = 9
        asyncio.run(arena.start_timeout('Break 1', timeout_duration_sec))
        self.assertEqual(game.timing.timeout_duration_sec, timeout_duration_sec)
        self.assertEqual(arena.match_state, MatchState.TIMEOUT_ACTIVE)
        self.assertEqual(arena.break_description, 'Break 1')
        arena.match_start_time = datetime.now() - timedelta(seconds=timeout_duration_sec)
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.POST_TIMEOUT)
        arena.match_start_time = datetime.now() - timedelta(
            seconds=timeout_duration_sec + POST_TIMEOUT_SEC
        )
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.PRE_MATCH)

        timeout_duration_sec = 28
        asyncio.run(arena.start_timeout('Break 2', timeout_duration_sec))
        self.assertEqual(game.timing.timeout_duration_sec, timeout_duration_sec)
        self.assertEqual(arena.match_state, MatchState.TIMEOUT_ACTIVE)
        self.assertEqual(arena.break_description, 'Break 2')
        asyncio.run(arena.abort_match())
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.POST_TIMEOUT)
        arena.match_start_time = datetime.now() - timedelta(
            seconds=timeout_duration_sec + POST_TIMEOUT_SEC
        )
        asyncio.run(arena.update())
        self.assertEqual(arena.match_state, MatchState.PRE_MATCH)

        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].bypass = True
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].bypass = True
        arena.alliance_stations['B3'].bypass = True
        asyncio.run(arena.start_match())
        asyncio.run(arena.update())
        with self.assertRaises(RuntimeError):
            asyncio.run(arena.start_timeout('Timeout', 1))
        self.assertNotEqual(arena.match_state, MatchState.TIMEOUT_ACTIVE)
        self.assertEqual(game.timing.timeout_duration_sec, timeout_duration_sec)
        arena.match_start_time = datetime.now() - timedelta(
            seconds=game.timing.warmup_duration_sec
            + game.timing.auto_duration_sec
            + game.timing.pause_duration_sec
            + game.timing.teleop_duration_sec
        )

        while arena.match_state != MatchState.POST_MATCH:
            asyncio.run(arena.update())
            with self.assertRaises(RuntimeError):
                asyncio.run(arena.start_timeout('Timeout', 1))

        arena.reset_match()
        asyncio.run(arena.load_test_match())
        asyncio.run(arena.start_timeout('Break2', 10))
        self.assertEqual(arena.match_state, MatchState.TIMEOUT_ACTIVE)
        match = models.MatchOut(
            type=models.MatchType.PLAYOFF,
            type_order=1,
            short_name='F1',
            playoff_match_group_id='F',
            playoff_red_alliance=1,
            playoff_blue_alliance=2,
            red1=1,
            red2=2,
            red3=3,
            blue1=4,
            blue2=5,
            blue3=6,
        )
        match = models.create_match(match)
        asyncio.run(arena.load_match(match))
        self.assertEqual(arena.match_state, MatchState.TIMEOUT_ACTIVE)
        self.assertEqual(arena.current_match, match)

    def test_save_team_has_connected(self):
        arena = setup_test_arena_with_parameter(self)

        models.create_team(models.Team(id=101))
        models.create_team(models.Team(id=102))
        models.create_team(models.Team(id=103))
        models.create_team(models.Team(id=104))
        models.create_team(models.Team(id=105))
        models.create_team(models.Team(id=106, city='Tainan', has_connected=True))
        match = models.Match(
            type=models.MatchType.TEST,
            type_order=1,
            red1=101,
            red2=102,
            red3=103,
            blue1=104,
            blue2=105,
            blue3=106,
        )
        match = models.create_match(match)
        asyncio.run(arena.load_match(match))
        arena.alliance_stations['R1'].ds_conn = DriverStationConnection(101, 'R1')
        arena.alliance_stations['R1'].bypass = True
        arena.alliance_stations['R2'].ds_conn = DriverStationConnection(102, 'R2')
        arena.alliance_stations['R2'].ds_conn.robot_linked = True
        arena.alliance_stations['R3'].ds_conn = DriverStationConnection(103, 'R3')
        arena.alliance_stations['R3'].bypass = True
        arena.alliance_stations['B1'].ds_conn = DriverStationConnection(104, 'B1')
        arena.alliance_stations['B1'].bypass = True
        arena.alliance_stations['B2'].ds_conn = DriverStationConnection(105, 'B2')
        arena.alliance_stations['B2'].ds_conn.robot_linked = True
        arena.alliance_stations['B3'].ds_conn = DriverStationConnection(106, 'B3')
        arena.alliance_stations['B3'].ds_conn.robot_linked = True
        arena.alliance_stations['B3'].team.city = 'TiNn'
        asyncio.run(arena.start_match())

        teams = models.read_all_teams()
        self.assertEqual(len(teams), 6)
        self.assertEqual(teams[0].has_connected, False)
        self.assertEqual(teams[1].has_connected, True)
        self.assertEqual(teams[2].has_connected, False)
        self.assertEqual(teams[3].has_connected, False)
        self.assertEqual(teams[4].has_connected, True)
        self.assertEqual(teams[5].has_connected, True)
        self.assertEqual(teams[5].city, 'Tainan')
