from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import models

router = APIRouter(prefix='/setup/sponsor_slides', tags=['sponsor_slides'])


@router.get('')
async def get_sponsor_slides() -> list[models.SponsorSlide]:
    sponser_slides = models.read_all_sponsor_slides()
    return sponser_slides


class SponsorSlideRequest(BaseModel):
    data: models.SponsorSlide
    action: str


@router.post('')
async def post_sponsor_slides(
    sponsor_slide_request: SponsorSlideRequest,
) -> list[models.SponsorSlide]:
    sponsor_slide = models.read_sponsor_slide_by_id(sponsor_slide_request.data.id)

    if sponsor_slide_request.action == 'save':
        if sponsor_slide is None:
            sponsor_slide_request.data.display_order = (
                models.read_next_sponsor_slide_display_order()
            )
            models.create_sponsor_slide(sponsor_slide_request.data)
        else:
            models.update_sponsor_slide(sponsor_slide_request.data)

    elif sponsor_slide_request.action == 'reorder_up':
        try:
            reorder_sponsor_slide(sponsor_slide_request.data.id, True)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    elif sponsor_slide_request.action == 'reorder_down':
        try:
            reorder_sponsor_slide(sponsor_slide_request.data.id, False)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    else:
        raise HTTPException(status_code=400, detail='Invalid action')

    sponsor_slides = models.read_all_sponsor_slides()
    return sponsor_slides


@router.delete('/{id}')
async def delete_sponsor_slides(id: int) -> list[models.SponsorSlide]:
    models.delete_sponsor_slide(id)

    return models.read_all_sponsor_slides()


def reorder_sponsor_slide(id: int, move_up: bool):
    sponsor_slide = models.read_sponsor_slide_by_id(id)
    if sponsor_slide is None:
        raise KeyError(f'Sponsor slide with id {id} not found')

    sponsor_slide_list = models.read_all_sponsor_slides()

    index = sponsor_slide_list.index(sponsor_slide)

    index += -1 if move_up else 1
    if index < 0 or index >= len(sponsor_slide_list):
        return

    sponsor_slide.display_order, sponsor_slide_list[index].display_order = (
        sponsor_slide_list[index].display_order,
        sponsor_slide.display_order,
    )
    models.update_sponsor_slide(sponsor_slide)
    models.update_sponsor_slide(sponsor_slide_list[index])
