import csv
import glob
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import game
import models
from web.arena import get_arena

router = APIRouter(prefix='/match_logs', tags=['match_logs'])


class MatchLogsListItem(BaseModel):
    id: int
    short_name: str
    time: str
    red_teams: list[str]
    blue_teams: list[str]
    color_class: str = ''
    is_completed: bool = False


class MatchLogRow(BaseModel):
    match_time_sec: float
    packet_type: int
    team_id: int
    alliance_station: str
    ds_linked: bool
    radio_linked: bool
    rio_linked: bool
    robot_linked: bool
    auto: bool
    enabled: bool
    emergency_stop: bool
    autonomous_stop: bool
    battery_voltage: float
    missed_packets_count: int
    ds_robot_trip_time_ms: int
    tx_rate: float = 0.0
    rx_rate: float = 0.0
    signal_noise_ratio: float = 0.0


class MatchLog(BaseModel):
    filename: int
    start_time: str
    rows: list[MatchLogRow]


class MatchLogs(BaseModel):
    team_id: int
    alliance_station: str
    logs: list[MatchLog] = []


class MatchLogsResponse(BaseModel):
    matches_by_type: dict[models.MatchType, list[MatchLogsListItem]]
    current_match_type: models.MatchType


@router.get('')
async def get_match_logs() -> MatchLogsResponse:
    pratice_matches = build_match_logs_list(models.MatchType.PRACTICE)
    qualification_matches = build_match_logs_list(models.MatchType.QUALIFICATION)
    playoff_matches = build_match_logs_list(models.MatchType.PLAYOFF)

    matches_by_type = {
        models.MatchType.PRACTICE: pratice_matches,
        models.MatchType.QUALIFICATION: qualification_matches,
        models.MatchType.PLAYOFF: playoff_matches,
    }
    current_match_type = get_arena().current_match.type
    if current_match_type == models.MatchType.TEST:
        current_match_type = models.MatchType.PRACTICE

    return MatchLogsResponse(matches_by_type=matches_by_type, current_match_type=current_match_type)


class MatchLogViewResponse(BaseModel):
    match: models.Match
    logs: MatchLogs
    first_match: str


@router.get('/{match_id}/{station_id}/log')
async def get_match_log_view(match_id: int, station_id: str) -> MatchLogViewResponse:
    try:
        match, match_logs = get_match_log_from_request(match_id, station_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    first_match = '0'
    if match_logs is not None and len(match_logs.logs) > 0:
        first_match = match_logs.logs[0].start_time

    return MatchLogViewResponse(match=match, logs=match_logs, first_match=first_match)


def get_match_log_from_request(match_id: int, station_id: str):
    match = models.read_match_by_id(match_id)
    logs = MatchLogs(team_id=0, alliance_station=station_id)

    if match is None:
        raise ValueError(f'Match {match_id} not found')

    if station_id == 'R1':
        logs.team_id = match.red1
    elif station_id == 'R2':
        logs.team_id = match.red2
    elif station_id == 'R3':
        logs.team_id = match.red3
    elif station_id == 'B1':
        logs.team_id = match.blue1
    elif station_id == 'B2':
        logs.team_id = match.blue2
    elif station_id == 'B3':
        logs.team_id = match.blue3

    if logs.team_id == 0:
        return None, None

    pattern = os.path.join(
        '.', 'static', 'logs', f'*_*_Match_{match.short_name}_{logs.team_id}.csv'
    )
    files = glob.glob(pattern)

    if len(files) == 0:
        return match, logs

    header_map = {}
    for filename in files:
        with open(filename) as f:
            reader = csv.reader(f)

            header = next(reader)
            for i, column in enumerate(header):
                header_map[column] = i

            current_log = MatchLog(filename=filename, start_time=filename[12:26], rows=[])
            for row in reader:
                current_row = MatchLogRow(
                    match_time_sec=float(row[header_map['match_time_sec']]),
                    packet_type=int(row[header_map['packet_type']]),
                    team_id=int(row[header_map['team_id']]),
                    alliance_station=row[header_map['alliance_station']],
                    ds_linked=row[header_map['ds_linked']] == 'True',
                    radio_linked=row[header_map['radio_linked']] == 'True',
                    rio_linked=row[header_map['rio_linked']] == 'True',
                    robot_linked=row[header_map['robot_linked']] == 'True',
                    auto=row[header_map['auto']] == 'True',
                    enabled=row[header_map['enabled']] == 'True',
                    emergency_stop=row[header_map['emergency_stop']] == 'True',
                    autonomous_stop=row[header_map['autonomous_stop']] == 'True',
                    battery_voltage=float(row[header_map['battery_voltage']]),
                    missed_packets_count=int(row[header_map['missed_packets_count']]),
                    ds_robot_trip_time_ms=int(row[header_map['ds_robot_trip_time_ms']]),
                )
                if len(header_map) > 13:
                    current_row.tx_rate = float(row[header_map['tx_rate']])
                    current_row.rx_rate = float(row[header_map['rx_rate']])
                    current_row.signal_noise_ratio = float(row[header_map['signal_noise_ratio']])
                else:
                    current_row.tx_rate = -1
                    current_row.rx_rate = -1
                    current_row.signal_noise_ratio = -1

                current_log.rows.append(current_row)

            logs.logs.append(current_log)
    return match, logs


def build_match_logs_list(match_type: models.MatchType):
    matches = models.read_matches_by_type(match_type, False)
    match_logs_list = []

    for match in matches:
        match_logs_list.append(
            MatchLogsListItem(
                id=match.id,
                short_name=match.short_name,
                time=match.scheduled_time.strftime('%b %m/%d %I:%M %p'),
                red_teams=[match.red1, match.red2, match.red3],
                blue_teams=[match.blue1, match.blue2, match.blue3],
            )
        )
        if match.status == game.MatchStatus.RED_WON_MATCH:
            match_logs_list[-1].color_class = 'red'
            match_logs_list[-1].is_completed = True
        elif match.status == game.MatchStatus.BLUE_WON_MATCH:
            match_logs_list[-1].color_class = 'blue'
            match_logs_list[-1].is_completed = True
        elif match.status == game.MatchStatus.TIE_MATCH:
            match_logs_list[-1].color_class = 'yellow'
            match_logs_list[-1].is_completed = True
        else:
            match_logs_list[-1].color_class = ''
            match_logs_list[-1].is_completed = False

    return match_logs_list
