from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import models
import tournament
from web.arena import get_arena

router = APIRouter(prefix='/setup/schedule', tags=['schedule'])

cached_matches = dict[models.MatchType, list[models.Match]]()
cached_team_first_match = dict[models.MatchType, dict[int, str]]()


@router.get('')
async def get_schedule(match_type: str) -> dict[str, Any]:
    try:
        match_type = models.MatchType[match_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail='Invalid match type') from None

    if match_type not in [
        models.MatchType.PRACTICE,
        models.MatchType.QUALIFICATION,
    ]:
        match_type = models.MatchType.PRACTICE
    teams = models.read_all_teams()
    schedule_blocks = models.read_schedule_blocks_by_match_type(match_type)
    return {
        'match_type': match_type,
        'schedule_blocks': schedule_blocks,
        'num_teams': len(teams),
        'matches': cached_matches.get(match_type, []),
        'team_first_matches': cached_team_first_match.get(match_type, {}),
    }


class ScheduleBlock(BaseModel):
    num_matches: int
    match_spacing_sec: int
    start_time: datetime


class GenerateScheduleRequest(BaseModel):
    num_schedule_blocks: int
    schedule_blocks: list[ScheduleBlock]


@router.post('/generate')
async def generate_schedule(
    match_type: str, schedule_request: GenerateScheduleRequest
) -> dict[str, Any]:
    try:
        match_type = models.MatchType[match_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail='Invalid match type') from None

    if match_type not in [
        models.MatchType.PRACTICE,
        models.MatchType.QUALIFICATION,
    ]:
        raise HTTPException(status_code=400, detail='Invalid match type')

    schedule_blocks = list[models.ScheduleBlock]()
    for block in schedule_request.schedule_blocks:
        schedule_block = models.ScheduleBlock(
            match_type=match_type,
            start_time=block.start_time,
            num_matches=block.num_matches,
            match_spacing_sec=block.match_spacing_sec,
        )
        schedule_blocks.append(schedule_block)

    models.delete_schedule_block_by_match_type(match_type)
    for schedule_block in schedule_blocks:
        schedule_block = models.create_schedule_block(schedule_block)
        if schedule_block is None:
            raise HTTPException(status_code=500, detail='Failed to create schedule block')

    teams = models.read_all_teams()
    if len(teams) == 0:
        raise HTTPException(status_code=400, detail='No teams in database')
    if len(teams) < 6:
        raise HTTPException(status_code=400, detail='Not enough teams in database')

    try:
        matches = await tournament.build_random_schedule(teams, schedule_blocks, match_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    cached_matches[match_type] = matches

    team_first_matches = dict[int, str]()
    for match in matches:
        for team in [match.red1, match.red2, match.red3, match.blue1, match.blue2, match.blue3]:
            if team not in team_first_matches:
                team_first_matches[team] = match.short_name
    cached_team_first_match[match_type] = team_first_matches

    return {
        'match_type': match_type,
        'schedule_blocks': schedule_blocks,
        'num_teams': len(teams),
        'matches': cached_matches.get(match_type, []),
        'team_first_matches': cached_team_first_match.get(match_type, {}),
    }


@router.post('/save')
async def save_schedule(match_type: str) -> dict:
    try:
        match_type = models.MatchType[match_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail='Invalid match type') from None

    existing_matches = models.read_matches_by_type(match_type)
    if len(existing_matches) > 0:
        raise HTTPException(status_code=400, detail='Matches already exist for this match type')

    for match in cached_matches.get(match_type, []):
        models.create_match(match)

    return {'status': 'success'}
