from fastapi import APIRouter, HTTPException
from backend.app.core import ipc
from pydantic import BaseModel

router = APIRouter()


class ArenaCommand(BaseModel):
    action: str


@router.post("/start")
async def start_match():
    q = ipc.get_command_queue()
    if not q:
        raise HTTPException(status_code=500, detail="IPC Command Queue not initialized")
    q.put({"action": "START"})
    return {"status": "Command sent"}


@router.post("/abort")
async def abort_match():
    q = ipc.get_command_queue()
    if not q:
        raise HTTPException(status_code=500, detail="IPC Command Queue not initialized")
    q.put({"action": "ABORT"})
    return {"status": "Command sent"}


@router.post("/reset")
async def reset_match():
    q = ipc.get_command_queue()
    if not q:
        raise HTTPException(status_code=500, detail="IPC Command Queue not initialized")
    q.put({"action": "RESET"})
    return {"status": "Command sent"}
