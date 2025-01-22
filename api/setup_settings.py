from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import models

from .arena import api_arena

router = APIRouter(prefix='/setup/settings', tags=['settings'])
db_router = APIRouter(prefix='/setup/db', tags=['db'])


@router.get('/')
async def get_settings() -> models.Event:
    return api_arena.event


@router.post('/')
async def update_settings(new_settings: models.Event) -> dict:
    event_settings = models.read_event_settings()
    previous_event_name = event_settings.name
    event_settings.name = new_settings.name
    if len(event_settings.name) < 1 and event_settings.name != previous_event_name:
        event_settings.name = previous_event_name
    previous_admin_password = event_settings.admin_password

    playoff_type = models.PlayoffType.DOUBLE_ELIMINATION
    num_alliance = 8
    if new_settings.playoff_type == models.PlayoffType.SINGLE_ELIMINATION:
        playoff_type = models.PlayoffType.SINGLE_ELIMINATION
        num_alliance = new_settings.num_playoff_alliance
        if num_alliance < 2 or num_alliance > 16:
            raise HTTPException(status_code=400, detail='Invalid number of alliances')

    if (
        event_settings.playoff_type != playoff_type
        or event_settings.num_playoff_alliance != num_alliance
    ):
        alliances = models.read_all_alliances()
        if len(alliances) > 0:
            raise HTTPException(
                status_code=400, detail='Cannot change playoff type with existing alliances'
            )

    event_settings.playoff_type = playoff_type
    event_settings.num_playoff_alliance = num_alliance
    event_settings.selection_round_2_order = new_settings.selection_round_2_order
    event_settings.selection_round_3_order = new_settings.selection_round_3_order
    event_settings.tba_download_enabled = new_settings.tba_download_enabled
    event_settings.tba_publishing_enabled = new_settings.tba_publishing_enabled
    event_settings.tba_event_code = new_settings.tba_event_code
    event_settings.tba_secret_id = new_settings.tba_secret_id
    event_settings.tba_secret = new_settings.tba_secret
    event_settings.nexus_enabled = new_settings.nexus_enabled
    event_settings.network_security_enabled = new_settings.network_security_enabled
    event_settings.ap_address = new_settings.ap_address
    event_settings.ap_password = new_settings.ap_password
    event_settings.ap_channel = new_settings.ap_channel
    event_settings.switch_address = new_settings.switch_address
    event_settings.switch_password = new_settings.switch_password
    event_settings.plc_address = new_settings.plc_address
    event_settings.admin_password = new_settings.admin_password
    event_settings.team_sign_red_1_id = new_settings.team_sign_red_1_id
    event_settings.team_sign_red_2_id = new_settings.team_sign_red_2_id
    event_settings.team_sign_red_3_id = new_settings.team_sign_red_3_id
    event_settings.team_sign_red_timer_id = new_settings.team_sign_red_timer_id
    event_settings.team_sign_blue_1_id = new_settings.team_sign_blue_1_id
    event_settings.team_sign_blue_2_id = new_settings.team_sign_blue_2_id
    event_settings.team_sign_blue_3_id = new_settings.team_sign_blue_3_id
    event_settings.team_sign_blue_timer_id = new_settings.team_sign_blue_timer_id
    event_settings.warmup_duration_sec = new_settings.warmup_duration_sec
    event_settings.auto_duration_sec = new_settings.auto_duration_sec
    event_settings.pause_duration_sec = new_settings.pause_duration_sec
    event_settings.teleop_duration_sec = new_settings.teleop_duration_sec
    event_settings.warning_remaining_duration_sec = new_settings.warning_remaining_duration_sec
    event_settings.melody_bonus_threshold_without_coop = (
        new_settings.melody_bonus_threshold_without_coop
    )
    event_settings.melody_bonus_threshold_with_coop = new_settings.melody_bonus_threshold_with_coop
    event_settings.amplification_note_limit = new_settings.amplification_note_limit
    event_settings.amplification_duration_sec = new_settings.amplification_duration_sec

    models.update_event_settings(event_settings)
    await api_arena.load_settings()

    if event_settings.admin_password != previous_admin_password:
        models.truncate_user_sessions()

    return {'status': 'success'}


@router.get('/publish_alliances')
async def publish_alliances() -> dict:
    if api_arena.event.tba_publishing_enabled:
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=400, detail='TBA publishing is not enabled')


@router.get('/publish_awards')
async def publish_awards() -> dict:
    if api_arena.event.tba_publishing_enabled:
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=400, detail='TBA publishing is not enabled')


@router.get('/publish_matches')
async def publish_matches() -> dict:
    if api_arena.event.tba_publishing_enabled:
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=400, detail='TBA publishing is not enabled')


@router.get('/publish_rankings')
async def publish_rankings() -> dict:
    if api_arena.event.tba_publishing_enabled:
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=400, detail='TBA publishing is not enabled')


@router.get('/publish_teams')
async def publish_teams() -> dict:
    if api_arena.event.tba_publishing_enabled:
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=400, detail='TBA publishing is not enabled')


@db_router.get('/save')
async def save_db() -> FileResponse:
    filename = (
        f'{api_arena.event.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d%H%M%S")}.db'
    )
    return FileResponse('./pengiloo.db', filename=filename)


@db_router.post('/restore')
async def restore_db() -> dict:
    raise HTTPException(status_code=500, detail='Not Supported')
    # return {'status': 'success'}


@db_router.post('/clear/{type}')
async def clear_db(type: str) -> dict:
    try:
        match_type = models.MatchType[type.upper()]
    except KeyError as e:
        raise HTTPException(status_code=400, detail='Invalid match type') from e
    if match_type == models.MatchType.TEST:
        raise HTTPException(status_code=400, detail='Cannot clear test matches')

    models.backup_db(models.read_event_settings().name, 'clear')
    if match_type == models.MatchType.PRACTICE:
        delete_match_date_for_type(models.MatchType.PRACTICE)
    elif match_type == models.MatchType.QUALIFICATION:
        delete_match_date_for_type(models.MatchType.QUALIFICATION)
        models.truncate_ranking()
    elif match_type == models.MatchType.PLAYOFF:
        delete_match_date_for_type(models.MatchType.PLAYOFF)
        models.truncate_alliance()

    return {'status': 'success'}


def delete_match_date_for_type(match_type: models.MatchType):
    matches = models.read_matches_by_type(match_type, True)
    for match in matches:
        match_result = models.read_match_result_for_match(match.id)
        while match_result is not None:
            models.delete_match_result(match_result.id)
            match_result = models.read_match_result_for_match(match.id)
        models.delete_match(match.id)
    models.delete_schedule_block_by_match_type(match_type)
