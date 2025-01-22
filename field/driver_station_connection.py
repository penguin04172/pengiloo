import asyncio
import logging
import re
import socket
from datetime import datetime

import game
import models
import network

from .specs import MatchState

DRIVER_STATION_TCP_LISTEN_PORT = 1750
DRIVER_STATION_UDP_SEND_PORT = 1121
DRIVER_STATION_UDP_RECEIVE_PORT = 1160
DRIVER_STATION_TCP_LINK_TIMEOUT_SEC = 5
DRIVER_STATION_UDP_LINK_TIMEOUT_SEC = 1
MAX_TCP_PACKET_BYTES = 4096

alliance_station_position_map = {'R1': 0, 'R2': 1, 'R3': 2, 'B1': 3, 'B2': 4, 'B3': 5}


class DriverStationConnection:
    team_id: int = 0
    alliance_station: str = ''
    auto: bool = False
    enabled: bool = False
    e_stop: bool = False
    a_stop: bool = False
    ds_linked: bool = False
    radio_linked: bool = False
    rio_linked: bool = False
    robot_linked: bool = False
    battery_voltage: float = 0.0
    ds_robot_trip_time_ms: int = 0
    missed_packet_count: int = 0
    seconds_since_last_robot_link: float = 0.0
    last_packet_time: datetime = datetime.now()
    last_robot_linked_time: datetime = datetime.now()
    packet_count: int = 0
    missed_packet_offset: int = 0
    tcp_conn: socket.socket
    udp_conn: socket.socket = None
    log: None = None
    wrong_station: str = ''

    def __init__(self, team_id: int, alliance_station: str = '', tcp_conn: socket.socket = None):
        self.team_id = team_id
        self.alliance_station = alliance_station
        self.tcp_conn = tcp_conn
        if self.tcp_conn is not None:
            ip_address, _ = self.tcp_conn.getpeername()
            logging.info(f'Driver station for Team {self.team_id} connected from {ip_address}')
            self.udp_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_conn.connect((ip_address, DRIVER_STATION_UDP_SEND_PORT))

    def update(self, arena):
        self.send_control_packet(arena)

        if (
            datetime.now() - self.last_packet_time
        ).total_seconds() > DRIVER_STATION_UDP_LINK_TIMEOUT_SEC:
            self.ds_linked = False
            self.radio_linked = False
            self.rio_linked = False
            self.robot_linked = False
            self.battery_voltage = 0

        self.seconds_since_last_robot_link = (
            datetime.now() - self.last_robot_linked_time
        ).total_seconds()

    def close(self):
        if self.log is not None:
            self.log.close()

        if self.udp_conn is not None:
            self.udp_conn.close()

        if self.tcp_conn is not None:
            self.tcp_conn.close()

    def signal_match_start(self, match: models.MatchOut, wifi_status: network.TeamWifiStatus):
        self.missed_packet_offset = self.missed_packet_count
        # self.log =

    def encode_control_packet(self, arena):
        packet = bytearray(22)

        # packet number
        packet[0] = (self.packet_count >> 8) & 0xFF
        packet[1] = (self.packet_count) & 0xFF

        # protocol version
        packet[2] = 0

        # robot status
        packet[3] = 0
        packet[3] |= 0x02 if self.auto else 0
        packet[3] |= 0x04 if self.enabled else 0
        packet[3] |= 0x40 if self.a_stop else 0
        packet[3] |= 0x80 if self.e_stop else 0

        # unused
        packet[4] = 0

        # alliance station
        packet[5] = alliance_station_position_map[self.alliance_station]

        # match type
        packet[6] = 0
        match = arena.current_match
        if match.type == models.MatchType.PRACTICE:
            packet[6] = 1
        elif match.type == models.MatchType.QUALIFICATION:
            packet[6] = 2
        elif match.type == models.MatchType.PLAYOFF:
            packet[6] = 3

        # match number
        packet[7] = match.type_order >> 8
        packet[8] = match.type_order & 0xFF
        packet[9] = 1

        # current time
        current_time = datetime.now()
        packet[10] = (current_time.microsecond >> 24) & 0xFF
        packet[11] = (current_time.microsecond >> 16) & 0xFF
        packet[12] = (current_time.microsecond >> 8) & 0xFF
        packet[13] = current_time.microsecond & 0xFF
        packet[14] = current_time.second
        packet[15] = current_time.minute
        packet[16] = current_time.hour
        packet[17] = current_time.day
        packet[18] = current_time.month
        packet[19] = current_time.year - 1900

        # match remaining time
        if arena.match_state in [
            MatchState.PRE_MATCH,
            MatchState.TIMEOUT_ACTIVE,
            MatchState.POST_TIMEOUT,
        ]:
            match_seconds_remaining = game.timing.auto_duration_sec
        elif arena.match_state in [MatchState.START_MATCH, MatchState.AUTO_PERIOD]:
            match_seconds_remaining = game.timing.auto_duration_sec - int(arena.match_time_sec())
        elif arena.match_state in [MatchState.PAUSE_PERIOD]:
            match_seconds_remaining = game.timing.teleop_duration_sec
        elif arena.match_state in [MatchState.TELEOP_PERIOD]:
            match_seconds_remaining = (
                game.timing.auto_duration_sec
                + game.timing.teleop_duration_sec
                + game.timing.pause_duration_sec
                - int(arena.match_time_sec())
            )
        else:
            match_seconds_remaining = 0
        packet[20] = (match_seconds_remaining >> 8) & 0xFF
        packet[21] = match_seconds_remaining & 0xFF

        self.packet_count += 1
        return packet

    def send_control_packet(self, arena):
        packet = self.encode_control_packet(arena)
        if self.udp_conn is not None:
            self.udp_conn.send(packet)

    def decode_status_packet(self, data: bytes):
        # average ds-robot time in ms
        self.ds_robot_trip_time_ms = int(data[1]) / 2
        # number of missed packet from ds to robot
        self.missed_packet_count = int(data[2]) - self.missed_packet_offset

    async def handle_tcp_connection(self, arena):
        buffer = bytearray(MAX_TCP_PACKET_BYTES)
        while True:
            self.tcp_conn.settimeout(DRIVER_STATION_TCP_LINK_TIMEOUT_SEC)
            try:
                _ = self.tcp_conn.recv_into(buffer)
            except Exception as err:
                logging.error(f'Error reading from connection for Team {self.team_id}: {err}')
                self.close()
                arena.alliance_stations[self.alliance_station].ds_conn = None
                break

            packet_type = int(buffer[2])
            match packet_type:
                case 29:
                    # Keepalive packet
                    continue
                case 22:
                    status_packet = bytearray(36)
                    status_packet[:] = buffer[2:38]
                    self.decode_status_packet(status_packet)

                    match_time_sec = arena.match_time_sec()
                    if match_time_sec > 0 and self.log is not None:
                        pass
                case _:
                    logging.info(
                        f'Received unknown packet type {packet_type} from Team {self.team_id}'
                    )

    def send_game_data_packet(self, game_data: str):
        byte_data = game_data.encode('ascii')
        size = len(byte_data)
        packet = bytearray(4)

        packet[0] = 0  # packet size
        packet[1] = size + 2
        packet[2] = 28
        packet[3] = size
        packet.extend(byte_data)

        if self.tcp_conn is not None:
            self.tcp_conn.send(packet)


class DriverStationConnectionMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def listen_for_ds_udp_packets(self):
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listener.bind(('0.0.0.0', DRIVER_STATION_UDP_RECEIVE_PORT))
        except Exception as err:
            logging.error(f'Error opening ds udp socket: {err}')

        logging.info(f'Listening for driver stations on UDP port {DRIVER_STATION_UDP_RECEIVE_PORT}')

        while True:
            data = listener.recv(50)

            team_id = int(data[4]) << 8 + int(data[5])

            ds_conn = None
            for _, alliance_station in self.alliance_stations.items():
                if alliance_station.team is not None and alliance_station.team.id == team_id:
                    ds_conn = alliance_station.ds_conn
                    break

            if ds_conn is not None:
                ds_conn.ds_linked = True
                ds_conn.last_packet_time = datetime.now()

                ds_conn.rio_linked = (data[3] & 0x08) != 0
                ds_conn.radio_linked = (data[3] & 0x10) != 0
                ds_conn.robot_linked = (data[3] & 0x20) != 0

                if ds_conn.robot_linked:
                    ds_conn.last_robot_linked_time = datetime.now()
                    ds_conn.battery_voltage = float(data[6]) + float(data[7]) / 256

    async def listen_for_driver_stations(self):
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.bind((network.server_ip_address, DRIVER_STATION_TCP_LISTEN_PORT))
            listener.listen(20)
        except Exception as err:
            logging.info(f'Error opening driver station TCP socket {err}')
            logging.info(
                f'Change IP address to {network.server_ip_address} and restart server to fix'
            )
            return

        logging.info(f'Listening for ds on TCP port {DRIVER_STATION_TCP_LISTEN_PORT}')
        with listener:
            while True:
                try:
                    tcp_conn, (ip_address, port) = listener.accept()
                except Exception as err:
                    logging.info(f'Error accepting driver station connection: {err}')
                    continue

                try:
                    packet = tcp_conn.recv(5)
                except Exception as err:
                    logging.info(f'Error reading initial function: {err}')
                    continue

                if not (packet[0] == 0 and packet[1] == 3 and packet[2] == 24):
                    logging.info(f'Invalid initial packet received: {packet}')
                    tcp_conn.close()
                    continue

                team_id = int(packet[3]) << 8 + int(packet[4])

                assigned_station = self.get_assigned_alliance_station(team_id)
                if assigned_station == '':
                    logging.info(
                        f'Rejecting connection from Team {team_id}, is not in current match, soon.'
                    )

                    async def handle_rejected_connection(team_id, tcp_conn):
                        print(
                            f'Rejecting connection from Team {team_id}, who is not in the current match.'
                        )
                        await asyncio.sleep(1)  # 等待 1 秒
                        tcp_conn.close()  # 關閉連接
                        print(f'Closed connection for Team {team_id}.')

                    asyncio.create_task(handle_rejected_connection(team_id, tcp_conn))
                    continue

                station_status = bytes([0])
                team_re = re.compile(r'\d+\.(\d+)\.(\d+)\.')
                team_digits = team_re.search(ip_address)
                team_digit_1 = int(team_digits.group(1))
                team_digit_2 = int(team_digits.group(2))
                station_team_id = team_digit_1 * 100 + team_digit_2
                wrong_assigned_station = ''
                if station_team_id != team_id:
                    wrong_assigned_station = self.get_assigned_alliance_station(station_team_id)
                    if wrong_assigned_station != '':
                        logging.info(
                            f'Team {team_id} is in incorrect station {wrong_assigned_station}'
                        )
                        station_status = 1

                assignment_packet = bytearray(5)
                assignment_packet[0] = 0
                assignment_packet[1] = 3
                assignment_packet[2] = 25
                logging.info(
                    f'Accepting connection from Team {team_id} in station {assigned_station}'
                )
                assignment_packet[3] = alliance_station_position_map[assigned_station]
                assignment_packet[4] = station_status

                try:
                    tcp_conn.send(assignment_packet)
                except Exception as err:
                    logging.info(f'Error sending driver station assignment packet: {err}')
                    tcp_conn.close()
                    continue

                try:
                    ds_conn = DriverStationConnection(
                        team_id=team_id, assigned_station=assigned_station, tcp_conn=tcp_conn
                    )
                except Exception as err:
                    logging.info(f'Error registering driver station connection: {err}')
                    tcp_conn.close()
                    continue
                self.alliance_stations[assigned_station].ds_conn = ds_conn

                if wrong_assigned_station != '':
                    ds_conn.wrong_station = wrong_assigned_station

                asyncio.create_task(ds_conn.handle_tcp_connection(self))
