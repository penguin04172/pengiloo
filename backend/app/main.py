from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from backend.app.db.engine import init_db
import asyncio
import queue
from loguru import logger
import os

# Import models to register them with SQLModel metadata

from backend.app.api.endpoints import (
    ws,
    teams,
    matches,
    events,
    arena,
    rankings,
    schedule,
    alliances,
)
from backend.app.core import ipc
from backend.app.core.notifier import manager

# Setup Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


async def ipc_listener():
    """Background task to listen for IPC events and broadcast them."""
    logger.info("IPC Listener started")
    q = ipc.get_event_queue()
    if not q:
        logger.warning(
            "IPC Queue not initialized! WebServer might be running standalone."
        )
        return

    while True:
        try:
            # Non-blocking get
            try:
                message = q.get_nowait()
                await manager.broadcast(message)
            except queue.Empty:
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in IPC listener: {e}")
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Web Server Starting...")
    await init_db()

    # Start IPC listener task
    task = asyncio.create_task(ipc_listener())

    yield
    # Shutdown logic
    print("Web Server Shutting Down...")
    task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(title="FRC FMS", lifespan=lifespan)

    # Mount Static Files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "static")),
        name="static",
    )

    # API Routers
    app.include_router(ws.router)
    app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
    app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
    app.include_router(events.router, prefix="/api/events", tags=["Events"])
    app.include_router(arena.router, prefix="/api/arena", tags=["Arena Control"])
    app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
    app.include_router(rankings.router, prefix="/api/rankings", tags=["Rankings"])
    app.include_router(alliances.router, prefix="/api/alliances", tags=["Alliances"])

    # Frontend Routes
    @app.get("/")
    async def dashboard(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})

    @app.get("/teams")
    async def teams_page(request: Request):
        return templates.TemplateResponse("teams.html", {"request": request})

    @app.get("/matches")
    async def matches_page(request: Request):
        return templates.TemplateResponse("matches.html", {"request": request})

    @app.get("/rankings")
    async def rankings_page(request: Request):
        return templates.TemplateResponse("rankings.html", {"request": request})

    @app.get("/alliances")
    async def alliances_page(request: Request):
        return templates.TemplateResponse(
            "alliance_selection.html", {"request": request}
        )

    return app
