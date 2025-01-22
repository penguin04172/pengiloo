import socket
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import models

from .driver_station_connection import DriverStationConnection
from .specs import MatchState
from .test_helper import setup_test_arena_with_parameter


class TestDriverStationConnection(unittest.TestCase):
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

    @staticmethod
    def setup_fake_tcp_connection():
        tcp_conn = MagicMock(spec=socket.socket)
        tcp_conn.getpeername.return_value = ('127.0.0.1', 9999)
        return tcp_conn

    def test_encode_control_packet(self):
        arena = setup_test_arena_with_parameter(self)
        tcp_conn = self.setup_fake_tcp_connection()
        ds_conn = DriverStationConnection(1234, 'R1', tcp_conn)

        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x00)
        self.assertEqual(data[6], 0x00)
        self.assertEqual(data[20], 0x00)
        self.assertEqual(data[21], 0x0F)

        ds_conn.alliance_station = 'R2'
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x01)
        ds_conn.alliance_station = 'R3'
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x02)
        ds_conn.alliance_station = 'B1'
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x03)
        ds_conn.alliance_station = 'B2'
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x04)
        ds_conn.alliance_station = 'B3'
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[5], 0x05)

        ds_conn.packet_count = 255
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[0], 0x00)
        self.assertEqual(data[1], 0xFF)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[0], 0x01)
        self.assertEqual(data[1], 0x00)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[0], 0x01)
        self.assertEqual(data[1], 0x01)
        ds_conn.packet_count = 65535
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[0], 0xFF)
        self.assertEqual(data[1], 0xFF)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[0], 0x00)
        self.assertEqual(data[1], 0x00)

        ds_conn.auto = True
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[3], 0x02)

        ds_conn.enabled = True
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[3], 0x06)

        ds_conn.auto = False
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[3], 0x04)

        ds_conn.e_stop = True
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[3], 0x84)

        ds_conn.a_stop = True
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[3], 0xC4)

        arena.current_match.type = models.MatchType.PRACTICE
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[6], 0x01)
        arena.current_match.type = models.MatchType.QUALIFICATION
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[6], 0x02)
        arena.current_match.type = models.MatchType.PLAYOFF
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[6], 0x03)

        arena.current_match.type = models.MatchType.PRACTICE
        arena.current_match.type_order = 42
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[7], 0)
        self.assertEqual(data[8], 42)
        arena.current_match.type = models.MatchType.QUALIFICATION
        arena.current_match.type_order = 258
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[7], 1)
        self.assertEqual(data[8], 2)
        arena.current_match.type = models.MatchType.PLAYOFF
        arena.current_match.type_order = 13
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[7], 0)
        self.assertEqual(data[8], 13)

        arena.match_state = MatchState.AUTO_PERIOD
        arena.match_start_time = datetime.now() - timedelta(seconds=4)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[21], 11)
        arena.match_state = MatchState.PAUSE_PERIOD
        arena.match_start_time = datetime.now() - timedelta(seconds=16)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[21], 135)
        arena.match_state = MatchState.TELEOP_PERIOD
        arena.match_start_time = datetime.now() - timedelta(seconds=33)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[21], 120)
        arena.match_start_time = datetime.now() - timedelta(seconds=150)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[21], 3)
        arena.match_state = MatchState.POST_MATCH
        arena.match_start_time = datetime.now() - timedelta(seconds=180)
        data = ds_conn.encode_control_packet(arena)
        self.assertEqual(data[21], 0)

    def test_send_control_packet(self):
        arena = setup_test_arena_with_parameter(self)
        tcp_conn = self.setup_fake_tcp_connection()
        ds_conn = DriverStationConnection(1234, 'R1', tcp_conn)

        ds_conn.send_control_packet(arena)

    def test_decode_status_packet(self):
        tcp_conn = self.setup_fake_tcp_connection()
        ds_conn = DriverStationConnection(1234, 'R1', tcp_conn)

        data = bytearray(
            [
                22,
                28,
                103,
                19,
                192,
                0,
                246,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
        )
        ds_conn.decode_status_packet(data)
        self.assertEqual(ds_conn.missed_packet_count, 103)
        self.assertEqual(ds_conn.ds_robot_trip_time_ms, 14)

    # def test_listen_for_driver_station(self):
    #     arena = setup_test_arena_with_parameter(self)

    #     old_address = network.server_ip_address
    #     network.server_ip_address = '127.0.0.1'

    #     asyncio.create_task(arena.listen_for_driver_stations())
    #     time.sleep(0.01)
    #     network.server_ip_address = old_address

    #     tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     tcp_conn.connect(('127.0.0.1', 1750))
    #     data_send = bytearray([0, 3, 29, 0, 0])
    #     tcp_conn.send(data_send)
    #     data_recv = tcp_conn.recv(100)
    #     tcp_conn.close()

    #     tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     tcp_conn.connect(('127.0.0.1', 1750))
    #     data_send = bytearray([0, 3, 24, 5, 223])
    #     tcp_conn.send(data_send)
    #     data_recv = tcp_conn.recv(5)
    #     tcp_conn.close()

    #     arena.assign_team(1503, 'B2')
    #     tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     tcp_conn.connect(('127.0.0.1', 1750))
    #     data_send = bytearray([0, 3, 24, 5, 223])
    #     tcp_conn.send(data_send)
    #     data_recv = tcp_conn.recv(5)
    #     self.assertEqual(data_recv, bytes([0, 3, 25, 4, 0]))

    #     time.sleep(0.01)
    #     ds_conn = arena.alliance_stations['B2'].ds_conn
    #     self.assertEqual(ds_conn.team_id, 1503)
    #     self.assertEqual(ds_conn.alliance_station, 'B2')

    #     data_send = bytearray([0, 3, 37, 0, 0])
    #     tcp_conn.send(data_send)
    #     time.sleep(0.01)
    #     data_send2 = bytearray(
    #         [
    #             0,
    #             36,
    #             22,
    #             28,
    #             103,
    #             19,
    #             192,
    #             0,
    #             246,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #         ]
    #     )
    #     tcp_conn.send(data_send2)
    #     time.sleep(0.01)
    #     self.assertEqual(ds_conn.missed_packet_count, 103)
    #     self.assertEqual(ds_conn.ds_robot_trip_time_ms, 14)
    #     tcp_conn.close()
