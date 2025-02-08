from fastapi import APIRouter

from . import (
    bracket_svg,
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
    setup_lower_thirds,
    setup_schedule,
    setup_settings,
    setup_sponsor_slides,
    setup_teams,
)

router = APIRouter(prefix='/api')

router.include_router(bracket_svg.router)

router.include_router(setup_awards.router)
router.include_router(setup_displays.router)
router.include_router(setup_field_testing.router)
router.include_router(setup_lower_thirds.router)
router.include_router(setup_breaks.router)
router.include_router(setup_sponsor_slides.router)
router.include_router(setup_teams.router)
router.include_router(setup_schedule.router)
router.include_router(setup_settings.router)
router.include_router(setup_settings.db_router)

router.include_router(displays_alliance_station.router)
router.include_router(displays_announcer.router)
router.include_router(displays_audience.router)
router.include_router(displays_bracket.router)
router.include_router(displays_field_monitor.router)
router.include_router(displays_logo.router)
router.include_router(displays_placeholder.router)
router.include_router(displays_queueing.router)
router.include_router(displays_rankings.router)
router.include_router(displays_twitch.router)
router.include_router(displays_wall.router)
router.include_router(displays_webpage.router)

router.include_router(panels_referee.router)
router.include_router(panels_scoring.router)

router.include_router(match_logs.router)
router.include_router(match_play.router)
router.include_router(match_review.router)


@router.get('/')
async def api_root():
    return {'data': 'Hello API'}
