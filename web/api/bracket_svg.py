from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import models
import web
from web import arena_state

router = APIRouter(prefix='/bracket')


class AllianceMatchup:
    def __init__(
        self,
        id: str = '',
        red_alliance_source: str = '',
        blue_alliance_source: str = '',
        red_alliance: models.Alliance = None,
        blue_alliance: models.Alliance = None,
        is_active: bool = False,
        series_leader: str = '',
        series_status: str = '',
        is_complete: bool = False,
    ):
        self.id = id
        self.red_alliance_source = red_alliance_source
        self.blue_alliance_source = blue_alliance_source
        self.red_alliance = red_alliance
        self.blue_alliance = blue_alliance
        self.is_active = is_active
        self.series_leader = series_leader
        self.series_status = series_status
        self.is_complete = is_complete


async def generate_bracket_svg(active_match: models.Match = None) -> str:
    alliances = models.read_all_alliances()

    # Get playoff tournament data from cached state
    state = arena_state.get_full_state()
    playoff_tournament_data = state.get('playoff_tournament')

    matchups = {}

    if playoff_tournament_data is not None:
        # Note: playoff_tournament is a complex object that needs special handling
        # For now, we'll use placeholder logic
        # TODO: Properly serialize playoff_tournament in Arena state broadcasting
        pass

    # Get event settings from database
    event = models.read_event_settings()
    bracket_type = 'double'
    num_alliances = event.num_playoff_alliances if event else 8
    if event and event.playoff_type == models.PlayoffType.SINGLE_ELIMINATION:
        if num_alliances > 8:
            bracket_type = '16'
        elif num_alliances > 4:
            bracket_type = '8'
        elif num_alliances > 2:
            bracket_type = '4'
        else:
            bracket_type = '2'

    template = web.templates.get_template('img/bracket.svg')
    return template.render(
        matchups=matchups,
        bracket_type=bracket_type,
    )


@router.get('/bracket')
async def bracket_svg(active_match: str = ''):
    match = None
    if active_match == 'current':
        match_id = arena_state.get_match_id()
        match = models.read_match_by_id(match_id) if match_id else None
    elif active_match == 'saved':
        # saved_match is not in state, use None
        match = None

    svg = await generate_bracket_svg(match)

    return StreamingResponse(content=svg.encode(), media_type='image/svg+xml')