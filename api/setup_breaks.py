from fastapi import HTTPException

import models

from .router import setup_router


@setup_router.get('/breaks')
async def get_breaks():
    breaks = models.read_scheduled_breaks_by_match_type(models.MatchType.PLAYOFF)
    return breaks


@setup_router.post('/breaks')
async def update_break(id: int, description: str):
    break_ = models.read_scheduled_break_by_id(id)
    if break_ is None:
        raise HTTPException(status_code=404, detail='break not found')
    break_.description = description
    return models.update_scheduled_break(break_)
