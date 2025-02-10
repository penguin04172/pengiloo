from fastapi import APIRouter

import models

router = APIRouter(prefix='/setup/sponsor_slides', tags=['sponsor_slides'])


@router.get('')
async def get_sponsor_slides() -> list[models.SponsorSlide]:
    sponser_slides = models.read_all_sponsor_slides()
    return sponser_slides
