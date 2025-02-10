from fastapi import APIRouter, HTTPException

import models

router = APIRouter(prefix='/setup/breaks', tags=['breaks'])


@router.get('')
async def get_breaks() -> list[models.ScheduledBreak]:
    breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
    return breaks


@router.post('')
async def update_break(id: int, description: str) -> models.ScheduledBreak:
    break_ = models.read_scheduled_break_by_id(id)
    if break_ is None:
        raise HTTPException(status_code=404, detail='break not found')
    break_.description = description
    return models.update_scheduled_break(break_)
