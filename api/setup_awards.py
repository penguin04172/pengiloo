from fastapi import HTTPException

import models

from .router import setup_router


@setup_router.get('/awards')
async def get_awards():
    awards = models.read_all_awards()
    teams = models.read_all_teams()
    return {'awards': awards, 'teams': teams}


@setup_router.post('/awards')
async def create_or_update_award(award: models.Award):
    if award.id is None:
        return models.create_award(award)

    award = models.read_award_by_id(award.id)
    if award is None:
        raise HTTPException(status_code=404, detail='award not found')
    return models.update_award(award)


@setup_router.delete('/awards/{id}')
async def delete_award(id: int):
    models.delete_award(id)
    return {'status': 'ok'}
