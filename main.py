import asyncio
import signal

import fastapi
import uvicorn

import api.arena
from api.router import api_router
from field.arena import Arena
from models.base import db
from web import index

app = fastapi.FastAPI()


def shutdown():
    loop = asyncio.get_event_loop()
    loop.stop()


async def main():
    # db.bind(provider='sqlite', filename='event.db', create_db=True)
    db.bind(provider='sqlite', filename=':memory:', create_db=True)
    db.generate_mapping(create_tables=True)

    arena = await Arena.new_arena()
    api.arena.api_arena = arena
    arena_task = asyncio.create_task(arena.run())

    app.include_router(api_router)
    app.include_router(index.router)

    config = uvicorn.Config(app, '0.0.0.0', 8000)
    server = uvicorn.Server(config)

    await server.serve()

    arena.running = False
    await arena_task


if __name__ == '__main__':
    # 設定 Ctrl+C 監聽
    signal.signal(signal.SIGINT, lambda s, f: shutdown())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
