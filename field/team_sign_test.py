import unittest

import game
import models

from .driver_station_connection import DriverStationConnection
from .realtime_score import RealtimeScore
from .specs import MatchState
from .team_sign import (
    TeamSign,
    TeamSigns,
    blue_color,
    green_color,
    orange_color,
    red_color,
    white_color,
)
from .test_helper import setup_test_arena_with_parameter


class TestTeamSign(unittest.TestCase):
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

    def test_team_sign_generate_in_match_rear_test(self):
        realtime_score1 = RealtimeScore(amplified_time_remaining_sec=9)
        realtime_score2 = RealtimeScore(amplified_time_remaining_sec=15)
        realtime_score3 = RealtimeScore(
            current_score=game.Score(amp_speaker=game.AmpSpeaker(auto_speaker_notes=12))
        )
        realtime_score4 = RealtimeScore(
            current_score=game.Score(amp_speaker=game.AmpSpeaker(teleop_amp_notes=1))
        )

        self.assertEqual(
            TeamSigns.generate_in_match_rear_text(True, '01:23', realtime_score1, realtime_score2),
            '1:23 00/18    Amp: 9',
        )
        self.assertEqual(
            TeamSigns.generate_in_match_rear_text(False, '01:23', realtime_score2, realtime_score1),
            '1:23 00/18    Amp:15',
        )
        game.specific.melody_bonus_threshold_without_coop = 23
        self.assertEqual(
            TeamSigns.generate_in_match_rear_text(True, '34:56', realtime_score3, realtime_score4),
            '4:56 12/23 R060-B001',
        )
        self.assertEqual(
            TeamSigns.generate_in_match_rear_text(False, '34:56', realtime_score4, realtime_score3),
            '4:56 01/23 B001-R060',
        )

    def test_team_sign_timer(self):
        arena = setup_test_arena_with_parameter(self)
        sign = TeamSign(is_timer=True)

        sign.update(arena, None, True, '12:34', 'Rear Text')
        self.assertEqual(sign.packet_data, bytearray())

        sign.set_id(56)
        sign.update(arena, None, True, '12:34', 'Rear Text')
        self.assertEqual(sign.packet_data[0:5].decode('ascii'), 'CYPRX')
        self.assertEqual(sign.packet_data[5], 56)
        self.assertEqual(sign.packet_data[6], 4)
        self.assertEqual(sign.packet_data[10:15].decode('ascii'), '12:34')
        self.assertEqual(sign.packet_data[15:17], bytearray([0, 0]))
        self.assertEqual(sign.packet_data[30:39].decode('ascii'), 'Rear Text')
        self.assertEqual(sign.packet_index, 40)

        def assert_sign(expected_front_text, expected_front_color, expected_rear_text):
            front_text, front_color, rear_text = TeamSign.generate_timer_texts(
                arena, '23:45', 'Rear Text'
            )
            self.assertEqual(front_text, expected_front_text)
            self.assertEqual(front_color, expected_front_color)
            self.assertEqual(rear_text, expected_rear_text)

        arena.field_reset = False
        assert_sign(
            '23:45',
            white_color,
            'Rear Text',
        )
        arena.field_reset = True
        assert_sign(
            'SAFE ',
            green_color,
            'Rear Text',
        )

        arena.field_reset = True
        arena.match_state = MatchState.TIMEOUT_ACTIVE
        assert_sign('23:45', white_color, 'Field Break: 23:45')

        arena.alliance_station_display_mode = 'blank'
        assert_sign('     ', white_color, '')

        arena.alliance_station_display_mode = 'logo'
        arena.audience_display_mode = 'alliance_selection'
        arena.alliance_selection_show_timer = False
        assert_sign('     ', white_color, '')
        arena.alliance_selection_show_timer = True
        assert_sign('23:45', white_color, '')
        arena.alliance_station_display_mode = 'blank'
        assert_sign('     ', white_color, '')

    def test_team_sign_team_number(self):
        arena = setup_test_arena_with_parameter(self)
        alliance_station = arena.alliance_stations['R1']
        models.create_team(models.Team(id=1234))
        sign = TeamSign(is_timer=False)

        sign.update(arena, alliance_station, True, '12:34', 'Rear Text')
        self.assertEqual(sign.packet_data, bytearray())

        sign.set_id(53)
        sign.update(arena, alliance_station, True, '12:34', 'Rear Text')
        self.assertEqual(sign.packet_data[0:5].decode('ascii'), 'CYPRX')
        self.assertEqual(sign.packet_data[5], 53)
        self.assertEqual(sign.packet_data[6], 4)
        self.assertEqual(sign.packet_data[7:10], bytearray([1, 53, 1]))
        self.assertEqual(sign.packet_data[10:15].decode('ascii'), '     ')
        self.assertEqual(sign.packet_data[15:17], bytearray([0, 0]))
        self.assertEqual(sign.packet_data[34:50].decode('ascii'), 'No Team Assigned')
        self.assertEqual(sign.packet_index, 51)

        def assert_sign(
            is_red: bool, expected_front_text, expected_front_color, expected_rear_text
        ):
            front_text, front_color, rear_text = sign.generate_team_number_texts(
                arena, alliance_station, is_red, '12:34', 'Rear Text'
            )
            self.assertEqual(front_text, expected_front_text)
            self.assertEqual(rear_text, expected_rear_text)
            front_color.a = 255
            self.assertEqual(front_color, expected_front_color)

        assert_sign(
            True,
            '     ',
            white_color,
            '    No Team Assigned',
        )

        arena.field_reset = True
        arena.assign_team(1234, 'R1')
        assert_sign(True, ' 1234', green_color, '1234      Connect PC')
        assert_sign(False, ' 1234', green_color, '1234      Connect PC')

        arena.field_reset = False
        assert_sign(True, ' 1234', red_color, '1234      Connect PC')
        assert_sign(False, ' 1234', blue_color, '1234      Connect PC')

        alliance_station.ethernet = True
        assert_sign(True, ' 1234', red_color, '1234        Start DS')
        alliance_station.ds_conn = DriverStationConnection(
            team_id=0, assigned_station='', tcp_conn=None
        )
        assert_sign(True, ' 1234', red_color, '1234        No Radio')
        alliance_station.ds_conn.wrong_station = 'R1'
        assert_sign(True, ' 1234', red_color, '1234    Move Station')
        alliance_station.ds_conn.wrong_station = ''
        alliance_station.ds_conn.radio_linked = True
        assert_sign(True, ' 1234', red_color, '1234          No Rio')
        alliance_station.ds_conn.rio_linked = True
        assert_sign(True, ' 1234', red_color, '1234         No Code')
        alliance_station.ds_conn.robot_linked = True
        assert_sign(True, ' 1234', red_color, '1234           Ready')
        alliance_station.bypass = True
        assert_sign(True, ' 1234', red_color, '1234        Bypassed')

        arena.match_state = MatchState.TIMEOUT_ACTIVE
        assert_sign(True, ' 1234', red_color, '1234        Bypassed')

        arena.match_state = MatchState.AUTO_PERIOD
        assert_sign(True, ' 1234', red_color, 'Rear Text')
        alliance_station.a_stop = True
        assert_sign(True, ' 1234', orange_color, '1234          A-STOP')
        alliance_station.e_stop = True
        assert_sign(False, ' 1234', orange_color, '1234          E-STOP')
        alliance_station.e_stop = False
        arena.match_state = MatchState.TELEOP_PERIOD
        assert_sign(False, ' 1234', blue_color, 'Rear Text')
        alliance_station.e_stop = True
        assert_sign(False, ' 1234', orange_color, '1234          E-STOP')
        arena.match_state = MatchState.POST_MATCH
        assert_sign(False, ' 1234', orange_color, '1234          E-STOP')

        sign.next_match_team_id = 456
        assert_sign(False, ' 1234', orange_color, 'Next Team Up: 456')
        alliance_station.bypass = False
        alliance_station.e_stop = False
        alliance_station.ethernet = False
        arena.match_state = MatchState.PRE_MATCH
        arena.assign_team(456, 'R1')
        assert_sign(False, '  456', blue_color, '456       Connect PC')

        arena.alliance_station_display_mode = 'blank'
        assert_sign(True, '     ', white_color, '')

        arena.alliance_station_display_mode = 'logo'
        arena.audience_display_mode = 'alliance_selection'
        arena.alliance_selection_show_timer = False
        assert_sign(True, '     ', white_color, '')
        arena.alliance_selection_show_timer = True
        assert_sign(True, '12:34', white_color, '')
        arena.alliance_station_display_mode = 'blank'
        assert_sign(True, '     ', white_color, '')
