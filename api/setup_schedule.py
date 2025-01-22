from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel

import models
import tournament

from .router import setup_router

cached_matches = dict[models.MatchType, list[models.MatchOut]]()
cached_team_first_match = dict[models.MatchType, dict[int, str]]()


@setup_router.get('/schedule')
async def get_schedule(match_type: models.MatchType):
    if match_type not in [
        models.MatchType.PRACTICE,
        models.MatchType.QUALIFICATION,
    ]:
        match_type = models.MatchType.PRACTICE
    teams = models.read_all_teams()
    schedule_blocks = models.read_schedule_blocks_by_match_type(match_type)
    return {
        'event_settings': models.read_event_settings(),
        'match_type': match_type,
        'schedule_blocks': schedule_blocks,
        'num_teams': len(teams),
        'matches': cached_matches.get(match_type, []),
        'team_first_matches': cached_team_first_match.get(match_type, {}),
    }


class GenerateScheduleRequest(BaseModel):
    match_type: models.MatchType
    num_schedule_blocks: int
    num_matches: int
    match_spacing_sec: int
    start_time: datetime


@setup_router.post('/schedule/generate')
async def generate_schedule(schedule_request: GenerateScheduleRequest):
    if schedule_request.match_type not in [
        models.MatchType.PRACTICE,
        models.MatchType.QUALIFICATION,
    ]:
        raise HTTPException(status_code=400, detail='Invalid match type')

    schedule_blocks = list[models.ScheduleBlock]()
    for _ in range(schedule_request.num_schedule_blocks):
        schedule_block = models.ScheduleBlock(
            match_type=schedule_request.match_type,
            start_time=schedule_request.start_time,
            num_matches=schedule_request.num_matches,
            match_spacing_sec=schedule_request.match_spacing_sec,
        )
        schedule_blocks.append(schedule_block)

    models.delete_schedule_block_by_match_type(schedule_request.match_type)
    for schedule_block in schedule_blocks:
        schedule_block = models.create_schedule_block(schedule_block)
        if schedule_block is None:
            raise HTTPException(status_code=400, detail='Failed to create schedule block')

    teams = models.read_all_teams()
    if len(teams) == 0:
        raise HTTPException(status_code=400, detail='No teams in database')
    if len(teams) < 6:
        raise HTTPException(status_code=400, detail='Not enough teams in database')

    try:
        matches = await tournament.build_random_schedule(
            schedule_request.match_type, teams, schedule_blocks
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    cached_matches[schedule_request.match_type] = matches

    team_first_matches = dict[int, str]()
    for match in matches:
        for team in [match.red1, match.red2, match.red3, match.blue1, match.blue2, match.blue3]:
            if team not in team_first_matches:
                team_first_matches[team] = match.short_name
    cached_team_first_match[schedule_request.match_type] = team_first_matches

    return matches


@setup_router.post('/schedule/save')
async def save_schedule(match_type: models.MatchType):
    existing_matches = models.read_matches_by_type(match_type)
    if len(existing_matches) > 0:
        raise HTTPException(status_code=400, detail='Matches already exist for this match type')

    for match in cached_matches.get(match_type, []):
        models.create_match(match)

    models.backup_db(models.read_event_settings().name, 'schedule')

    return {'status': 'success'}
