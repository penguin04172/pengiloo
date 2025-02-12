import asyncio
import logging
import re
from datetime import datetime

import game
import models
import network

from .specs import MatchState

logger = logging.getLogger(__name__)

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
    tcp_conn: tuple[asyncio.StreamReader, asyncio.StreamWriter] = None
    udp_conn: asyncio.DatagramTransport = None
    log: None = None
    wrong_station: str = ''

    @classmethod
    async def new_driver_station_conncetion(
        cls,
        team_id: int,
        alliance_station: str = '',
        tcp_conn: tuple[asyncio.StreamReader, asyncio.StreamWriter] = None,
    ):
        ds_conn = cls()
        ds_conn.team_id = team_id
        ds_conn.alliance_station = alliance_station
        ds_conn.tcp_conn = tcp_conn
        if ds_conn.tcp_conn is not None:
            ip_address, _ = ds_conn.tcp_conn[1].get_extra_info('peername')
            logger.info(f'Driver station for Team {ds_conn.team_id} connected from {ip_address}')
            loop = asyncio.get_running_loop()
            ds_conn.udp_conn, _ = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                remote_addr=(ip_address, DRIVER_STATION_UDP_SEND_PORT),
            )
        return ds_conn

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

    async def close(self):
        if self.log is not None:
            self.log.close()

        if self.udp_conn is not None:
            self.udp_conn.close()

        if self.tcp_conn is not None:
            self.tcp_conn[1].close()
            await self.tcp_conn[1].wait_closed()

    def signal_match_start(self, match: models.Match, wifi_status: network.TeamWifiStatus):
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
            self.udp_conn.sendto(packet)

    def decode_status_packet(self, data: bytes):
        # average ds-robot time in ms
        self.ds_robot_trip_time_ms = int(data[1]) / 2
        # number of missed packet from ds to robot
        self.missed_packet_count = int(data[2]) - self.missed_packet_offset

    async def handle_tcp_connection(self, arena):
        try:
            while True:
                try:
                    packet = await asyncio.wait_for(
                        self.tcp_conn[0].read(38), timeout=DRIVER_STATION_TCP_LINK_TIMEOUT_SEC
                    )
                except asyncio.TimeoutError:  # noqa: UP041
                    logger.error(f'TCP connection timeout for Team {self.team_id}')
                    break
                except Exception as err:
                    logger.error(f'Error reading from connection for Team {self.team_id}: {err}')
                    break

                packet_type = int(packet[2])
                match packet_type:
                    case 29:
                        # Keepalive packet
                        continue
                    case 22:
                        status_packet = bytearray(36)
                        status_packet[:] = packet[2:38]
                        self.decode_status_packet(status_packet)

                        match_time_sec = arena.match_time_sec()
                        if match_time_sec > 0 and self.log is not None:
                            pass
                    case _:
                        logger.info(
                            f'Received unknown packet type {packet_type} from Team {self.team_id}'
                        )
        finally:
            await self.close()
            arena.alliance_stations[self.alliance_station].ds_conn = None

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
            self.tcp_conn[1].write(packet)

    def to_dict(self):
        return {
            'team_id': self.team_id,
            'alliance_station': self.alliance_station,
            'auto': self.auto,
            'enabled': self.enabled,
            'e_stop': self.e_stop,
            'a_stop': self.a_stop,
            'ds_linked': self.ds_linked,
            'radio_linked': self.radio_linked,
            'rio_linked': self.rio_linked,
            'robot_linked': self.robot_linked,
            'battery_voltage': self.battery_voltage,
            'ds_robot_trip_time_ms': self.ds_robot_trip_time_ms,
            'missed_packet_count': self.missed_packet_count,
            'seconds_since_last_robot_link': self.seconds_since_last_robot_link,
            'last_packet_time': self.last_packet_time.isoformat()
            if self.last_packet_time
            else None,
            'last_robot_linked_time': self.last_robot_linked_time.isoformat()
            if self.last_robot_linked_time
            else None,
            'packet_count': self.packet_count,
            'missed_packet_offset': self.missed_packet_offset,
            'tcp_conn': str(self.tcp_conn) if self.tcp_conn else None,  # 轉換為字串，避免無法序列化
            'udp_conn': str(self.udp_conn) if self.udp_conn else None,  # 轉換為字串
            'log': str(self.log) if self.log else None,  # 轉換為字串
            'wrong_station': self.wrong_station,
        }


class AsyncUDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, alliance_stations):
        self.alliance_stations = alliance_stations

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.create_task(self.process_udp_packet(data, addr))

    async def process_udp_packet(self, data, addr):
        if len(data) < 8:
            return

        team_id = (data[4] << 8) + data[5]
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


class DriverStationConnectionMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def listen_for_ds_udp_packets(self):
        try:
            loop = asyncio.get_running_loop()
            transport, _ = await loop.create_datagram_endpoint(
                lambda: AsyncUDPServerProtocol(self.alliance_stations),
                local_addr=('0.0.0.0', DRIVER_STATION_UDP_RECEIVE_PORT),
            )
        except OSError as err:
            logger.error(f'Error starting driver station UDP listener: {err}')
            return

        logger.info(f'Listening for driver stations on UDP port {DRIVER_STATION_UDP_RECEIVE_PORT}')
        try:
            while True:
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
        finally:
            transport.close()

    async def listen_for_driver_stations(self):
        try:
            listener = await asyncio.start_server(
                self.handle_ds_tcp_connection,
                network.server_ip_address,
                DRIVER_STATION_TCP_LISTEN_PORT,
            )
        except OSError as err:
            logger.error(f'Error starting driver station listener: {err}')
            return
        logger.info(f'Listening for ds on TCP port {DRIVER_STATION_TCP_LISTEN_PORT}')
        async with listener:
            await listener.serve_forever()

    async def handle_rejected_connection(team_id, writer: asyncio.StreamWriter):
        logger.warning(
            f'Rejecting connection from Team {team_id}, who is not in the current match.'
        )
        await asyncio.sleep(1)  # 等待 1 秒
        writer.close()  # 關閉連接
        await writer.wait_closed()  # 等待連接關閉
        logger.info(f'Closed connection for Team {team_id}.')

    async def handle_ds_tcp_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        ip_address, port = writer.get_extra_info('peername')
        try:
            packet = await reader.read(5)

            if not (packet[0] == 0 and packet[1] == 3 and packet[2] == 24):
                logger.info(f'Invalid initial packet received: {packet}')
                writer.close()
                await writer.wait_closed()
                return

            team_id = (int(packet[3]) << 8) + int(packet[4])

            assigned_station = self.get_assigned_alliance_station(team_id)
            if assigned_station == '':
                logger.info(
                    f'Rejecting connection from Team {team_id}, is not in current match, soon.'
                )
                asyncio.create_task(self.handle_rejected_connection(team_id, writer))
                return

            station_status = 0
            team_re = re.compile(r'\d+\.(\d+)\.(\d+)\.')
            team_digits = team_re.search(ip_address)
            team_digit_1 = int(team_digits.group(1))
            team_digit_2 = int(team_digits.group(2))
            station_team_id = team_digit_1 * 100 + team_digit_2
            wrong_assigned_station = ''
            if station_team_id != team_id:
                wrong_assigned_station = self.get_assigned_alliance_station(station_team_id)
                if wrong_assigned_station != '':
                    logger.info(f'Team {team_id} is in incorrect station {wrong_assigned_station}')
                    station_status = 1

            assignment_packet = bytearray(
                [0, 3, 25, alliance_station_position_map[assigned_station], station_status]
            )
            logger.info(f'Accepting connection from Team {team_id} in station {assigned_station}')
            writer.write(assignment_packet)
            await writer.drain()

            ds_conn = await DriverStationConnection.new_driver_station_conncetion(
                team_id=team_id, assigned_station=assigned_station, tcp_conn=(reader, writer)
            )
            self.alliance_stations[assigned_station].ds_conn = ds_conn

            if wrong_assigned_station != '':
                ds_conn.wrong_station = wrong_assigned_station

            await ds_conn.handle_tcp_connection(self)

        except Exception as err:
            logger.error(f'Error handling connection from {ip_address}: {err}')
        finally:
            writer.close()
            await writer.wait_closed()
