from fastapi import APIRouter

import game
import models

router = APIRouter(prefix='/setup/field_testing', tags=['field_testing'])


@router.get('/field_testing')
async def get_field_testing():
    return {
        'event_settings': models.read_event_settings(),
        'match_sounds': game.sounds,
    }
