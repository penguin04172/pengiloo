import random
import string

from fastapi import APIRouter, HTTPException

import models

from .arena import api_arena

router = APIRouter(prefix='/setup/teams', tags=['teams'])

KEY_CHARS = string.ascii_letters + string.digits


@router.get('/')
async def get_teams() -> list[models.Team]:
    teams = models.read_all_teams()
    return teams


@router.post('/')
async def create_team(team_numbers: list[int]) -> dict:
    if not can_modify_team_list():
        raise HTTPException(
            status_code=400, detail='Cannot modify team list while matches are scheduled.'
        )

    for team_number in team_numbers:
        models.create_team(team_number)

    return {'status': 'success'}


@router.delete('/clear')
async def clear_teams() -> dict:
    if not can_modify_team_list():
        raise HTTPException(
            status_code=400, detail='Cannot modify team list while matches are scheduled.'
        )

    models.truncate_teams()

    return {'status': 'success'}


@router.get('/wpa')
async def generate_wpa_keys(all: bool = False) -> dict:
    teams = models.read_all_teams()
    for team in teams:
        if len(team.wpakey) == 0 or all:
            team.wpakey = ''.join(random.choices(KEY_CHARS, k=8))
            models.update_team(team)

    return {'status': 'success'}


@router.get('/{team_number}')
async def get_team(team_number: int) -> models.Team:
    team = models.read_team_by_id(team_number)
    if team is None:
        raise HTTPException(status_code=404, detail='Team not found')

    return team


@router.post('/{team_number}')
async def update_team(team_number: int, new_team: models.Team) -> dict:
    team = models.read_team_by_id(team_number)
    if team is None:
        raise HTTPException(status_code=404, detail='Team not found')

    team.name = new_team.name
    team.nickname = new_team.nickname
    team.city = new_team.city
    team.school_name = new_team.school_name
    team.state_prov = new_team.state_prov
    team.country = new_team.country
    team.rookie_year = new_team.rookie_year
    team.robot_name = new_team.robot_name
    team.accomplishments = new_team.accomplishments
    if api_arena.event.network_security_enabled:
        team.wpakey = new_team.wpakey
        if len(team.wpakey) < 8 or len(team.wpakey) > 63:
            raise HTTPException(
                status_code=400, detail='WPA key must be between 8 and 63 characters'
            )

    team.has_connected = new_team.has_connected

    models.update_team(team)

    return {'status': 'success'}


@router.delete('/{team_number}')
async def delete_team(team_number: int) -> dict:
    if not can_modify_team_list():
        raise HTTPException(
            status_code=400, detail='Cannot modify team list while matches are scheduled.'
        )

    team = models.read_team_by_id(team_number)
    if team is None:
        raise HTTPException(status_code=404, detail='Team not found')

    models.delete_team(team)

    return {'status': 'success'}


def can_modify_team_list():
    matches = models.read_matches_by_type(models.MatchType.QUALIFICATION, True)
    if len(matches) > 0:
        return False
    return True
