from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import models

router = APIRouter(prefix='/setup/breaks', tags=['breaks'])


@router.get('')
async def get_breaks() -> list[models.ScheduledBreak]:
    breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
    return breaks


class BreakRequest(BaseModel):
    id: int
    description: str


@router.post('')
async def update_break(req: BreakRequest) -> list[models.ScheduledBreak]:
    break_ = models.read_scheduled_break_by_id(req.id)
    if break_ is None:
        raise HTTPException(status_code=404, detail='break not found')
    break_.description = req.description

    return models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
