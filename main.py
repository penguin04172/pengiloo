import asyncio

import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import web
from field.arena import Arena
from models.base import db
from web.arena import APIArena

app = fastapi.FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


async def main():
    db.bind(provider='sqlite', filename='pengiloo.db', create_db=True)
    # db.bind(provider='sqlite', filename=':memory:', create_db=True)
    db.generate_mapping(create_tables=True)

    arena = await Arena.new_arena()
    APIArena.set_instance(arena)
    arena_task = asyncio.create_task(arena.run())

    app.include_router(web.router)

    config = uvicorn.Config(app, '0.0.0.0', 8000, workers=4)
    server = uvicorn.Server(config)

    await server.serve()

    arena.running = False
    await arena_task


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
