from fastapi import APIRouter

import models

from .arena import api_arena

router = APIRouter(prefix='/setup/sponsor_slides', tags=['sponsor_slides'])


@router.get('/')
async def get_sponsor_slides():
    sponser_slides = models.read_all_sponsor_slides()
    return {'event_settings': api_arena.event, 'sponsor_slides': sponser_slides}
