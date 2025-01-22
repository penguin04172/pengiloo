from fastapi import APIRouter

from . import (
    setup_awards,
    setup_breaks,
    setup_displays,
    setup_field_testing,
    setup_lower_third,
    setup_schedule,
    setup_settings,
    setup_sponsor_slides,
    setup_teams,
)

api_router = APIRouter(prefix='/api', tags=['api'])

api_router.include_router(setup_awards.router)
api_router.include_router(setup_displays.router)
api_router.include_router(setup_field_testing.router)
api_router.include_router(setup_lower_third.router)
api_router.include_router(setup_breaks.router)
api_router.include_router(setup_sponsor_slides.router)
api_router.include_router(setup_teams.router)
api_router.include_router(setup_schedule.router)
api_router.include_router(setup_settings.router)
api_router.include_router(setup_settings.db_router)


@api_router.get('/')
async def api_root():
    return {'message': 'Hello API'}
