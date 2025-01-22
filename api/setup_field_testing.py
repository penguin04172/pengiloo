from fastapi import APIRouter

import game

router = APIRouter(prefix='/setup/field_testing', tags=['field_testing'])


@router.get('/field_testing')
async def get_field_testing() -> list[game.MatchSounds]:
    return game.sounds
