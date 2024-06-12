from fastapi import APIRouter, HTTPException, status
from models.event import *

router = APIRouter(
    prefix="/api/event",
    tags=["event_settings"]
)

@router.get("/")
async def get_settings():
    return read_event_settings()

@router.put("/")
async def update_settings(event_settings: Event):
    return update_event_settings(event_settings)
