import asyncio
import multiprocessing
import uvicorn
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import web
from field.arena import Arena
from models.base import create_db_and_tables
from web.arena import APIArena
from web.websocket_manager import WebSocketManager
from ipc import IPCManager

def run_arena(command_queue, state_queue):
    """Arena process entry point"""
    async def _run():
        create_db_and_tables()
        # Create IPC manager in this process with shared queues
        ipc = IPCManager()
        ipc.command_queue = command_queue
        ipc.state_queue = state_queue
        
        arena = await Arena.new_arena(ipc)
        await arena.run()
    
    asyncio.run(_run())

def run_web(command_queue, state_queue):
    """Web process entry point"""
    # Create IPC manager in this process with shared queues
    ipc = IPCManager()
    ipc.command_queue = command_queue
    ipc.state_queue = state_queue
    
    app = fastapi.FastAPI()
    APIArena.set_ipc(ipc)  # Initialize IPC in web process
    
    # Create WebSocket manager and start state listener
    ws_manager = WebSocketManager(ipc)
    app.state.ipc = ipc
    app.state.ws_manager = ws_manager
    
    # Start WebSocket listener in background
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(ws_manager.listen_for_state_updates())
    
    @app.on_event("shutdown")
    async def shutdown_event():
        ws_manager.stop()
    
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(web.router)
    
    config = uvicorn.Config(app, '0.0.0.0', 8000, workers=1)
    server = uvicorn.Server(config)
    server.run()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # Create queues in main process - these can be pickled
    command_queue = multiprocessing.Queue()
    state_queue = multiprocessing.Queue()
    
    arena_process = multiprocessing.Process(target=run_arena, args=(command_queue, state_queue))
    web_process = multiprocessing.Process(target=run_web, args=(command_queue, state_queue))
    
    arena_process.start()
    web_process.start()
    
    try:
        arena_process.join()
        web_process.join()
    except KeyboardInterrupt:
        arena_process.terminate()
        web_process.terminate()
