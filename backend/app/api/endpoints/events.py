from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.engine import get_session
from backend.app.models.event import Event

router = APIRouter()


@router.get("/", response_model=List[Event])
async def read_events(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Event))
    events = result.scalars().all()
    return events


@router.post("/", response_model=Event)
async def create_event(event: Event, session: AsyncSession = Depends(get_session)):
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.get("/{event_id}", response_model=Event)
async def read_event(event_id: int, session: AsyncSession = Depends(get_session)):
    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=Event)
async def update_event(
    event_id: int, event_update: Event, session: AsyncSession = Depends(get_session)
):
    db_event = await session.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = event_update.model_dump(exclude_unset=True)
    event_data.pop("id", None)

    for key, value in event_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    await session.commit()
    await session.refresh(db_event)
    return db_event


@router.delete("/{event_id}")
async def delete_event(event_id: int, session: AsyncSession = Depends(get_session)):
    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await session.delete(event)
    await session.commit()
    return {"ok": True}
