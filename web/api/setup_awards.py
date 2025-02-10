from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import models

router = APIRouter(prefix='/setup/awards', tags=['awards'])


class AwardResponse(BaseModel):
    awards: list[models.Award]
    teams: list[models.Team]


@router.get('')
async def get_awards() -> AwardResponse:
    awards = models.read_all_awards()
    teams = models.read_all_teams()
    return AwardResponse(awards=awards, teams=teams)


@router.post('')
async def create_or_update_award(award: models.Award) -> models.Award:
    if award.id is None:
        return models.create_award(award)

    award = models.read_award_by_id(award.id)
    if award is None:
        raise HTTPException(status_code=404, detail='award not found')
    return models.update_award(award)


@router.delete('/{id}')
async def delete_award(id: int) -> dict:
    models.delete_award(id)
    return {'status': 'ok'}
