import logging
import socket
from datetime import datetime

from pydantic import dataclasses

import game
from models import MatchOut

from .realtime_score import RealtimeScore
from .specs import MatchState


@dataclasses.dataclass
class RGBA:
    r: int
    g: int
    b: int
    a: int


TEAM_SIGN_ADDRESS_PREFIX = '10.0.100.'
TEAM_SIGN_PORT = 10011
TEAM_SIGN_PACKET_MAGIC_STRING = 'CYPRX'
TEAM_SIGN_PACKET_HEADER_LENGTH = 7
TEAM_SIGN_COMMAND_SET_DISPLAY = bytearray([0x04])
TEAM_SIGN_ADDRESS_SINGLE = bytearray([0x01])
TEAM_SIGN_PACKET_TYPE_FRONT_TEXT = bytearray([0x01])
TEAM_SIGN_PACKET_TYPE_REAR_TEXT = bytearray([0x02])
TEAM_SIGN_PACKET_TYPE_FRONT_INTENSITY = bytearray([0x03])
TEAM_SIGN_PACKET_TYPE_COLOR = bytearray([0x04])
TEAM_SIGN_PACKET_PERIOD_MS = 5000
TEAM_SIGN_BLINK_PERIOD_MS = 750

red_color = RGBA(255, 0, 0, 255)
blue_color = RGBA(0, 50, 255, 255)
green_color = RGBA(0, 255, 0, 255)
orange_color = RGBA(255, 50, 0, 255)
white_color = RGBA(255, 200, 180, 255)


def blink_color(original_color: RGBA):
    if (
        int(datetime.now().timestamp() * 1000) % TEAM_SIGN_BLINK_PERIOD_MS
        < TEAM_SIGN_BLINK_PERIOD_MS / 2
    ):
        return original_color
    return RGBA(original_color.r, original_color.g, original_color.b, 0)


class TeamSign:
    is_timer: bool = False
    address: bytearray = bytearray()
    next_match_team_id: int = 0
    front_text: str = ''
    front_color: RGBA = RGBA(0, 0, 0, 0)
    rear_text: str = ''
    last_front_text: str = ''
    last_front_color: RGBA = RGBA(0, 0, 0, 0)
    last_rear_text: str = ''
    udp_conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_data: bytearray = bytearray()
    packet_index: int = 0
    last_packet_time: datetime = datetime.min

    def __init__(self, is_timer: bool = False):
        self.is_timer = is_timer

    @staticmethod
    def generate_timer_texts(arena, countdown: str, in_match_rear_text: str):
        if arena.alliance_station_display_mode == 'blank':
            return ('     ', white_color, '')

        if arena.audience_display_mode == 'alliance_selection':
            if arena.alliance_selection_show_timer:
                return (countdown, white_color, '')
            else:
                return ('     ', white_color, '')

        front_text = countdown
        front_color = white_color
        rear_text = in_match_rear_text
        if arena.match_state == MatchState.TIMEOUT_ACTIVE:
            rear_text = f'Field Break: {countdown}'
        elif arena.field_reset and arena.match_state != MatchState.TIMEOUT_ACTIVE:
            front_text = 'SAFE '
            front_color = green_color
        else:
            front_text = countdown
            front_color = white_color

        return (front_text, front_color, rear_text)

    def generate_team_number_texts(
        self,
        arena,
        alliance_station,
        is_red: bool,
        countdown: str,
        in_match_rear_text: str,
    ):
        if arena.alliance_station_display_mode == 'blank':
            return ('     ', white_color, '')

        if arena.audience_display_mode == 'alliance_selection':
            if arena.alliance_selection_show_timer:
                return (countdown, white_color, '')
            else:
                return ('     ', white_color, '')

        if alliance_station.team is None:
            return ('     ', white_color, f'{"No Team Assigned":>20}')

        front_text = f'{alliance_station.team.id: 5d}'
        if (
            alliance_station.e_stop
            or alliance_station.a_stop
            and arena.match_state == MatchState.AUTO_PERIOD
        ):
            front_color = blink_color(orange_color)
        elif arena.field_reset:
            front_color = green_color
        elif is_red:
            front_color = red_color
        else:
            front_color = blue_color

        message = ''
        if alliance_station.e_stop:
            message = 'E-STOP'
        elif alliance_station.a_stop and arena.match_state == MatchState.AUTO_PERIOD:
            message = 'A-STOP'
        elif (
            arena.match_state == MatchState.PRE_MATCH
            or arena.match_state == MatchState.TIMEOUT_ACTIVE
        ):
            if alliance_station.bypass:
                message = 'Bypassed'
            elif not alliance_station.ethernet:
                message = 'Connect PC'
            elif alliance_station.ds_conn is None:
                message = 'Start DS'
            elif alliance_station.ds_conn.wrong_station != '':
                message = 'Move Station'
            elif not alliance_station.ds_conn.radio_linked:
                message = 'No Radio'
            elif not alliance_station.ds_conn.rio_linked:
                message = 'No Rio'
            elif not alliance_station.ds_conn.robot_linked:
                message = 'No Code'
            else:
                message = 'Ready'

        rear_text = ''
        if (
            arena.match_state == MatchState.POST_MATCH
            and self.next_match_team_id > 0
            and self.next_match_team_id != alliance_station.team.id
        ):
            rear_text = f'Next Team Up: {self.next_match_team_id}'
        elif len(message) > 0:
            rear_text = f'{alliance_station.team.id:<5} {message:>14}'
        else:
            rear_text = in_match_rear_text

        return (front_text, front_color, rear_text)

    def send_packet(self):
        if self.packet_index == 0:
            self.write_packet_data(bytearray(TEAM_SIGN_PACKET_MAGIC_STRING, 'ascii'))
            self.write_packet_data(self.address + TEAM_SIGN_COMMAND_SET_DISPLAY)
        else:
            self.packet_index = TEAM_SIGN_PACKET_HEADER_LENGTH

        is_stale = (
            datetime.now() - self.last_packet_time
        ).total_seconds() * 1000 >= TEAM_SIGN_PACKET_PERIOD_MS

        if self.front_text != self.last_front_text or is_stale:
            self.write_packet_data(
                TEAM_SIGN_ADDRESS_SINGLE + self.address + TEAM_SIGN_PACKET_TYPE_FRONT_TEXT
            )
            self.write_packet_data(bytearray(self.front_text, 'ascii'))
            self.write_packet_data(bytearray([0, 0]))
            self.last_front_text = self.front_text

        if self.front_color != self.last_front_color or is_stale:
            self.write_packet_data(
                TEAM_SIGN_ADDRESS_SINGLE + self.address + TEAM_SIGN_PACKET_TYPE_COLOR
            )
            self.write_packet_data(
                bytearray([self.front_color.r, self.front_color.g, self.front_color.b])
            )
            self.write_packet_data(
                TEAM_SIGN_ADDRESS_SINGLE + self.address + TEAM_SIGN_PACKET_TYPE_FRONT_INTENSITY
            )
            self.write_packet_data(bytearray([self.front_color.a]))
            self.last_front_color = self.front_color

        if self.rear_text != self.last_rear_text or is_stale:
            self.write_packet_data(
                TEAM_SIGN_ADDRESS_SINGLE + self.address + TEAM_SIGN_PACKET_TYPE_FRONT_TEXT
            )
            self.write_packet_data(bytearray(self.rear_text, 'ascii'))
            self.write_packet_data(bytearray([0]))
            self.last_rear_text = self.rear_text

        if self.packet_index > TEAM_SIGN_PACKET_HEADER_LENGTH:
            self.last_packet_time = datetime.now()
            self.udp_conn.send(self.packet_data[: self.packet_index])

    def write_packet_data(self, data: bytearray):
        self.packet_data.extend(data)
        self.packet_index += len(data)

    def update(
        self,
        arena,
        alliance_station,
        is_red: bool,
        countdown: str,
        in_match_rear_text: str,
    ):
        self.packet_data = bytearray()
        if self.address == bytearray():
            return

        if self.is_timer:
            self.front_text, self.front_color, self.rear_text = self.generate_timer_texts(
                arena, countdown, in_match_rear_text
            )
        else:
            self.front_text, self.front_color, self.rear_text = self.generate_team_number_texts(
                arena, alliance_station, is_red, countdown, in_match_rear_text
            )

        try:
            self.send_packet()
        except Exception as err:
            logging.warning(f'Failed to send team sign packet: {err}')

    def set_id(self, id: int):
        if self.udp_conn is not None:
            self.udp_conn.close()

        self.address = bytearray([id])
        if id == 0:
            return

        ip_address = f'{TEAM_SIGN_ADDRESS_PREFIX}{id}'
        try:
            self.udp_conn.connect((ip_address, TEAM_SIGN_PORT))
        except Exception as err:
            logging.warning(f'Failed to connect to team sign at {ip_address}: {err}')
            return

        address_parts = ip_address.split('.')
        if len(address_parts) != 4:
            logging.warning(f'Failed to configure team sign: invalid IP address: {ip_address}')
            return

        address = int(address_parts[3])
        self.address = bytearray([address])
        self.packet_index = 0
        self.last_packet_time = datetime.now()


class TeamSigns:
    red_1: TeamSign = TeamSign()
    red_2: TeamSign = TeamSign()
    red_3: TeamSign = TeamSign()
    red_timer: TeamSign = TeamSign(is_timer=True)
    blue_1: TeamSign = TeamSign()
    blue_2: TeamSign = TeamSign()
    blue_3: TeamSign = TeamSign()
    blue_timer: TeamSign = TeamSign(is_timer=True)

    def __init__(self):
        pass

    @staticmethod
    def generate_in_match_rear_text(
        is_red: bool,
        countdown: str,
        realtime_score: 'RealtimeScore',
        opponent_realtime_score: 'RealtimeScore',
    ):
        score_summary = realtime_score.current_score.summarize(
            opponent_realtime_score.current_score
        )
        score_total = score_summary.score - score_summary.stage_points

        opponent_score_summary = opponent_realtime_score.current_score.summarize(
            realtime_score.current_score
        )
        opponent_score_total = opponent_score_summary.score - opponent_score_summary.stage_points

        if is_red:
            alliance_scores = f'R{score_total:03d}-B{opponent_score_total:03d}'
        else:
            alliance_scores = f'B{score_total:03d}-R{opponent_score_total:03d}'

        if realtime_score.amplified_time_remaining_sec > 0:
            alliance_scores = f'Amp:{realtime_score.amplified_time_remaining_sec:2d}'

        return f'{countdown[1:]} {score_summary.num_notes:02}/{score_summary.num_notes_goal:02} {alliance_scores:>9}'

    def update(self, arena):
        match_time_sec = int(arena.match_time_sec())

        match arena.match_state:
            case MatchState.PRE_MATCH:
                if arena.audience_display_mode == 'alliance_selection':
                    countdown_sec = arena.alliance_selection_time_remaining_sec
                else:
                    countdown_sec = game.timing.auto_duration_sec
            case MatchState.START_MATCH:
                pass
            case MatchState.WARMUP_PERIOD:
                countdown_sec = game.timing.auto_duration_sec
            case MatchState.AUTO_PERIOD:
                countdown_sec = (
                    game.timing.warmup_duration_sec + game.timing.auto_duration_sec - match_time_sec
                )
            case MatchState.TELEOP_PERIOD:
                countdown_sec = (
                    game.timing.warmup_duration_sec
                    + game.timing.auto_duration_sec
                    + game.timing.teleop_duration_sec
                    + game.timing.pause_duration_sec
                    - match_time_sec
                )
            case MatchState.TIMEOUT_ACTIVE:
                countdown_sec = game.timing.timeout_duration_sec - match_time_sec
            case _:
                countdown_sec = 0

        countdown = f'{countdown_sec // 60: 02d}:{countdown_sec % 60: 02d}'

        red_in_match_rear_text = self.generate_in_match_rear_text(
            True, countdown, arena.red_realtime_score, arena.blue_realtime_score
        )
        blue_in_match_rear_text = self.generate_in_match_rear_text(
            False, countdown, arena.blue_realtime_score, arena.red_realtime_score
        )

        self.red_1.update(
            arena, arena.alliance_stations['R1'], True, countdown, red_in_match_rear_text
        )
        self.red_2.update(
            arena, arena.alliance_stations['R2'], True, countdown, red_in_match_rear_text
        )
        self.red_3.update(
            arena, arena.alliance_stations['R3'], True, countdown, red_in_match_rear_text
        )
        self.red_timer.update(arena, None, True, countdown, red_in_match_rear_text)
        self.blue_1.update(
            arena, arena.alliance_stations['B1'], False, countdown, blue_in_match_rear_text
        )
        self.blue_2.update(
            arena, arena.alliance_stations['B2'], False, countdown, blue_in_match_rear_text
        )
        self.blue_3.update(
            arena, arena.alliance_stations['B3'], False, countdown, blue_in_match_rear_text
        )
        self.blue_timer.update(arena, None, False, countdown, blue_in_match_rear_text)

    def set_next_match_teams(self, match: 'MatchOut'):
        self.red_1.next_match_team_id = match.red1
        self.red_2.next_match_team_id = match.red2
        self.red_3.next_match_team_id = match.red3
        self.blue_1.next_match_team_id = match.blue1
        self.blue_2.next_match_team_id = match.blue2
        self.blue_3.next_match_team_id = match.blue3
