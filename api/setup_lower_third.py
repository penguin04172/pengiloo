from fastapi import APIRouter

import models

router = APIRouter(prefix='/setup/lower_thirds', tags=['lower_thirds'])


@router.get('/')
async def get_lower_thirds() -> list[models.LowerThird]:
    lower_thirds = models.read_all_lower_thirds()
    return lower_thirds
