from fastapi import APIRouter

from . import (
    displays_alliance_station,
    displays_announcer,
    displays_audience,
    displays_bracket,
    displays_field_monitor,
    displays_logo,
    displays_placeholder,
    displays_queueing,
    displays_rankings,
    displays_twitch,
    displays_wall,
    displays_webpage,
    match_logs,
    match_play,
    match_review,
    panels_referee,
    panels_scoring,
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

api_router = APIRouter(prefix='/api')

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

api_router.include_router(displays_alliance_station.router)
api_router.include_router(displays_announcer.router)
api_router.include_router(displays_audience.router)
api_router.include_router(displays_bracket.router)
api_router.include_router(displays_field_monitor.router)
api_router.include_router(displays_logo.router)
api_router.include_router(displays_placeholder.router)
api_router.include_router(displays_queueing.router)
api_router.include_router(displays_rankings.router)
api_router.include_router(displays_twitch.router)
api_router.include_router(displays_wall.router)
api_router.include_router(displays_webpage.router)

api_router.include_router(panels_referee.router)
api_router.include_router(panels_scoring.router)

api_router.include_router(match_logs.router)
api_router.include_router(match_play.router)
api_router.include_router(match_review.router)


@api_router.get('/')
async def api_root():
    return {'message': 'Hello API'}
