import csv
import os
from datetime import datetime

import models
import network

from .driver_station_connection import DriverStationConnection

LOGS_DIR = 'static/logs'


class TeamMatchLog:
    def __init__(self, team_id: int, match: models.MatchOut, wifi_status: network.TeamWifiStatus):
        os.makedirs(os.path.join(models.BASE_DIR, LOGS_DIR), mode=0o755, exist_ok=True)

        filename = f'{os.path.join(models.BASE_DIR, LOGS_DIR)}/'
        filename += f"{datetime.now().strftime("%Y%m%d%H%M%S")}_{match.type.name.title()}_"
        filename += f'Match_{match.short_name}_{team_id}.csv'

        self.log_file = open(filename, 'w', newline='')
        self.log_writer = csv.writer(self.log_file)

        self.log_writer.writerow(
            [
                'match_time_sec',
                'packet_type',
                'team_id',
                'alliance_station',
                'ds_linked',
                'radio_linked',
                'rio_linked',
                'robot_linked',
                'auto',
                'enabled',
                'emergency_stop',
                'autonomous_stop',
                'battery_voltage',
                'missed_packet_count',
                'ds_robot_trip_time_ms',
                'rx_rate',
                'tx_rate',
                'signal_noise_ratio',
            ]
        )
        self.wifi_status = wifi_status

    def log_ds_packet(
        self, match_time_sec: float, packet_type: int, ds_conn: DriverStationConnection
    ):
        self.log_writer.writerow(
            [
                match_time_sec,
                packet_type,
                ds_conn.team_id,
                ds_conn.alliance_station,
                ds_conn.ds_linked,
                ds_conn.radio_linked,
                ds_conn.rio_linked,
                ds_conn.robot_linked,
                ds_conn.auto,
                ds_conn.enabled,
                ds_conn.e_stop,
                ds_conn.a_stop,
                ds_conn.battery_voltage,
                ds_conn.missed_packet_count,
                ds_conn.ds_robot_trip_time_ms,
                self.wifi_status.rx_rate,
                self.wifi_status.tx_rate,
                self.wifi_status.signal_noise_ratio,
            ]
        )
