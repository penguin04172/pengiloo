from fastapi import APIRouter

from field.arena import Arena

arena: Arena = None

api_router = APIRouter(prefix='/api', tags=['api'])
setup_router = APIRouter(prefix='/setup', tags=['setup'])

api_router.include_router(setup_router)
