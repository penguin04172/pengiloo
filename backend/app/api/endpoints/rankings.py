from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.engine import get_session
from backend.app.services.tournament.ranking import calculate_rankings
from backend.app.models.ranking import Ranking

router = APIRouter()


@router.get("/", response_model=List[Ranking])
async def get_rankings(session: AsyncSession = Depends(get_session)):
    rankings = await calculate_rankings(session)
    return rankings
