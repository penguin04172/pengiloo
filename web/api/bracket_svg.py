from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import models
import web

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

    arena = web.get_arena()

    matchups = {}

    if arena.playoff_tournament is not None:
        for matchup in arena.playoff_tournament.MatchGroups():
            alliance_matchup = AllianceMatchup(
                id=matchup.Id(),
                red_alliance_source=matchup.red_alliance_source_display_name(),
                blue_alliance_source=matchup.blue_alliance_source_display_name(),
                is_complete=matchup.is_complete(),
            )
            if matchup.red_alliance_id > 0:
                if len(alliances) > 0:
                    alliance_matchup.red_alliance = alliances[matchup.red_alliance_id - 1]
                else:
                    alliance_matchup.red_alliance = models.Alliance(id=matchup.red_alliance_id)

            if matchup.blue_alliance_id > 0:
                if len(alliances) > 0:
                    alliance_matchup.blue_alliance = alliances[matchup.blue_alliance_id - 1]
                else:
                    alliance_matchup.blue_alliance = models.Alliance(id=matchup.blue_alliance_id)

            if active_match is not None:
                alliance_matchup.is_active = matchup.Id() == active_match.playoff_match_group_id

            alliance_matchup.series_leader, alliance_matchup.series_status = matchup.status_text()
            matchups[matchup.Id()] = alliance_matchup

    bracket_type = 'double'
    num_alliances = arena.event.num_playoff_alliance
    if arena.event.playoff_type == models.PlayoffType.SINGLE_ELIMINATION:
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
    if active_match == 'current':
        match = web.get_arena().current_match
    elif active_match == 'saved':
        match = web.get_arena().saved_match

    svg = await generate_bracket_svg(match)

    return StreamingResponse(content=svg.encode(), media_type='image/svg+xml')
