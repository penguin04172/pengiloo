from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.engine import get_session
from backend.app.models.schedule import ScheduleBlock

router = APIRouter()


@router.get("/", response_model=List[ScheduleBlock])
async def read_schedule_blocks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ScheduleBlock))
    return result.scalars().all()


@router.post("/", response_model=ScheduleBlock)
async def create_schedule_block(
    block: ScheduleBlock, session: AsyncSession = Depends(get_session)
):
    session.add(block)
    await session.commit()
    await session.refresh(block)
    return block


@router.delete("/{block_id}")
async def delete_schedule_block(
    block_id: int, session: AsyncSession = Depends(get_session)
):
    block = await session.get(ScheduleBlock, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    await session.delete(block)
    await session.commit()
    return {"ok": True}
