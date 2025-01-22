import asyncio
import csv
import math
import os
import random
from datetime import timedelta

import models

MATCHMAKER_DIR = 'matchmaker'
SCHEDULES_DIR = 'schedules'
TEAMS_PER_MATCH = 6


async def build_random_schedule(
    teams: list[models.Team],
    schedule_blocks: list[models.ScheduleBlock],
    match_type: models.MatchType,
):
    num_teams = len(teams)
    num_matches = count_matches(schedule_blocks)
    matches_per_team = num_matches * TEAMS_PER_MATCH // num_teams

    num_matches = math.ceil(num_teams * matches_per_team / TEAMS_PER_MATCH)
    process = await asyncio.create_subprocess_exec(
        os.path.join(models.BASE_DIR, MATCHMAKER_DIR, 'MatchMaker.exe'),
        f'-t {num_teams}',
        f'-r {matches_per_team}',
        '-m L -b -q -s',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stderr:
        raise Exception(stderr.decode())

    schedule_list = stdout.decode().splitlines()
    if len(schedule_list) != num_matches:
        raise ValueError(f'Invalid number {len(schedule_list)} of matches {num_matches} generated')

    anon_schedule = [list(map(int, schedule[2:].split(' '))) for schedule in schedule_list]
    matches = []
    team_shuffle = random.sample(range(num_teams), num_teams)

    for i, anon_match in enumerate(anon_schedule):
        match = models.Match(type=match_type, type_order=i + 1)
        if match_type == models.MatchType.PRACTICE:
            match.short_name = f'P{i + 1}'
            match.long_name = f'Practice {i + 1}'
            match.tba_match_key.comp_level = 'p'
        elif match_type == models.MatchType.QUALIFICATION:
            match.short_name = f'Q{i + 1}'
            match.long_name = f'Qualification {i + 1}'
            match.tba_match_key.comp_level = 'qm'
        else:
            raise ValueError(f'Invalid match type {match_type}')

        match.red1 = teams[team_shuffle[anon_match[0] - 1]].id
        match.red1_is_surrogate = anon_match[1] == 1
        match.red2 = teams[team_shuffle[anon_match[2] - 1]].id
        match.red2_is_surrogate = anon_match[3] == 1
        match.red3 = teams[team_shuffle[anon_match[4] - 1]].id
        match.red3_is_surrogate = anon_match[5] == 1
        match.blue1 = teams[team_shuffle[anon_match[6] - 1]].id
        match.blue1_is_surrogate = anon_match[7] == 1
        match.blue2 = teams[team_shuffle[anon_match[8] - 1]].id
        match.blue2_is_surrogate = anon_match[9] == 1
        match.blue3 = teams[team_shuffle[anon_match[10] - 1]].id
        match.blue3_is_surrogate = anon_match[11] == 1
        match.tba_match_key.match_number = i + 1

        matches.append(match)

    os.makedirs(os.path.join(models.BASE_DIR, SCHEDULES_DIR), exist_ok=True)
    match_index = 0
    for block in schedule_blocks:
        with open(
            os.path.join(models.BASE_DIR, SCHEDULES_DIR, f'schedule_{block.match_type.name}.csv'),
            'w',
        ) as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(
                ['Match', 'Time', 'Red 1', 'Red 2', 'Red 3', 'Blue 1', 'Blue 2', 'Blue 3']
            )
            for i in range(block.num_matches):
                if match_index < num_matches:
                    matches[match_index].scheduled_time = block.start_time + timedelta(
                        seconds=i * block.match_spacing_sec
                    )

                    csv_writer.writerow(
                        [
                            matches[match_index].short_name,
                            matches[match_index].scheduled_time,
                            matches[match_index].red1,
                            matches[match_index].red2,
                            matches[match_index].red3,
                            matches[match_index].blue1,
                            matches[match_index].blue2,
                            matches[match_index].blue3,
                        ]
                    )

                    match_index += 1

    return matches


def count_matches(schedule_blocks: list[models.ScheduleBlock]):
    num_matches = 0
    for block in schedule_blocks:
        num_matches += block.num_matches
    return num_matches
