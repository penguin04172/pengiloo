import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import models
import tournament
import ws
from web import arena_commands, arena_state

router = APIRouter('/alliance_selection', tags=['alliance_selection'])

alliance_selection_time_limit_sec = 45


class AllianceSelectionResponse(BaseModel):
    alliances: list[models.Alliance]
    ranked_teams: list[models.AllianceSelectionRankedTeam]
    next_row: int
    next_col: int
    time_limit_sec: int


def determine_next_cell() -> tuple[int, int]:
    alliances_data = arena_state.get_alliance_selection_alliances()
    event = models.read_event_settings()
    
    for i, alliance_dict in enumerate(alliances_data):
        team_ids = alliance_dict.get('team_ids', [])
        if len(team_ids) > 0 and team_ids[0] == 0:
            return i, 0
        if len(team_ids) > 1 and team_ids[1] == 0:
            return i, 1

    if event and event.selection_round_2_order == 'F':
        for i, alliance_dict in enumerate(alliances_data):
            team_ids = alliance_dict.get('team_ids', [])
            if len(team_ids) > 2 and team_ids[2] == 0:
                return i, 2
    else:
        for i, alliance_dict in reversed(list(enumerate(alliances_data))):
            team_ids = alliance_dict.get('team_ids', [])
            if len(team_ids) > 2 and team_ids[2] == 0:
                return i, 2

    if event and event.selection_round_3_order == 'F':
        for i, alliance_dict in enumerate(alliances_data):
            team_ids = alliance_dict.get('team_ids', [])
            if len(team_ids) > 3 and team_ids[3] == 0:
                return i, 3
    else:
        for i, alliance_dict in reversed(list(enumerate(alliances_data))):
            team_ids = alliance_dict.get('team_ids', [])
            if len(team_ids) > 3 and team_ids[3] == 0:
                return i, 3

    return -1, -1


def can_modify_alliance_selection():
    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
    if len(matches) > 0:
        return False
    return True


def can_reset_alliance_selection():
    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, True)
    for match in matches:
        if match.is_complete():
            return False
    return True


@router.get('')
async def get_alliance_selection() -> AllianceSelectionResponse:
    next_row, next_col = determine_next_cell()
    
    # Convert dict data back to models
    alliances_data = arena_state.get_alliance_selection_alliances()
    alliances = [models.Alliance(**a) for a in alliances_data]
    
    ranked_teams_data = arena_state.get_alliance_selection_ranked_teams()
    ranked_teams = [models.AllianceSelectionRankedTeam(**t) for t in ranked_teams_data]
    
    return AllianceSelectionResponse(
        alliances=alliances,
        ranked_teams=ranked_teams,
        next_row=next_row,
        next_col=next_col,
        time_limit_sec=alliance_selection_time_limit_sec,
    )


@router.post('')
async def post_alliance_selection(request: Request) -> dict:
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    body = await request.json()
    
    # Get current alliance selection state
    alliances_data = arena_state.get_alliance_selection_alliances()
    alliances = [models.Alliance(**a) for a in alliances_data]
    
    ranked_teams_data = arena_state.get_alliance_selection_ranked_teams()
    ranked_teams = [models.AllianceSelectionRankedTeam(**t) for t in ranked_teams_data]
    
    # Update alliances based on form data
    for i, alliance in enumerate(alliances):
        for j in range(len(alliance.team_ids)):
            team_id = body.get(f'selection{i}_{j}', 0)
            if team_id == 0:
                alliance.team_ids[j] = 0
            else:
                found = False
                for k, team in enumerate(ranked_teams):
                    if team.team_id == team_id:
                        if team.picked:
                            raise HTTPException(
                                status_code=400,
                                detail=f'Team {team_id} has already been picked',
                            )

                        found = True
                        alliance.team_ids[j] = team_id
                        ranked_teams[k].picked = True
                        break

                if not found:
                    raise HTTPException(
                        status_code=404, detail=f'Team {team_id} not found in ranked teams'
                    )

    # Send updated data back to Arena
    arena_commands.update_alliance_selection(
        [a.model_dump() for a in alliances],
        [t.model_dump() for t in ranked_teams]
    )
    
    return {'status': 'success'}


@router.post('/start')
async def start_alliance_selection() -> dict:
    alliances_data = arena_state.get_alliance_selection_alliances()
    if len(alliances_data) > 0:
        raise HTTPException(status_code=400, detail='Alliance selection has already started')

    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    event = models.read_event_settings()
    if not event:
        raise HTTPException(status_code=500, detail='Event settings not found')
    
    teams_per_alliance = 3
    if event.selection_round_3_order != '':
        teams_per_alliance = 4

    alliances = []
    for i in range(event.num_playoff_alliance):
        alliances.append(
            models.Alliance(id=i + 1, team_ids=[0] * teams_per_alliance)
        )

    rankings = models.read_all_rankings()
    ranked_teams = [
        models.AllianceSelectionRankedTeam(team_id=ranking.team_id, rank=ranking.rank, picked=False)
        for ranking in rankings
    ]

    arena_commands.update_alliance_selection(
        [a.model_dump() for a in alliances],
        [t.model_dump() for t in ranked_teams]
    )
    
    return {'status': 'success'}


@router.post('/reset')
async def reset_alliance_selection() -> dict:
    if not can_reset_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    models.truncate_alliance()
    arena_commands.reset_alliance_selection()
    
    return {'status': 'success'}


@router.post('/finalize')
async def finalize_alliance_selection(start_time: datetime) -> dict:
    if not can_modify_alliance_selection():
        raise HTTPException(
            status_code=400, detail='Cannot modify alliance selection during playoffs'
        )

    # Get current alliances from state
    alliances_data = arena_state.get_alliance_selection_alliances()
    alliances = [models.Alliance(**a) for a in alliances_data]
    
    # Validate all positions are filled
    for alliance in alliances:
        for team_id in alliance.team_ids:
            if team_id <= 0:
                raise HTTPException(status_code=400, detail='Alliance selection not complete')

    # Set lineup order and save to database
    for alliance in alliances:
        alliance.line_up[0] = alliance.team_ids[1]
        alliance.line_up[1] = alliance.team_ids[0]
        alliance.line_up[2] = alliance.team_ids[2]
        models.create_alliance(alliance)

    # Create playoff matches - this needs to be done via IPC command
    # For now, we'll use a new command to handle playoff creation
    arena_commands.create_playoff_matches(start_time.isoformat())
    
    tournament.calculate_team_cards(models.MatchType.PLAYOFF)
    
    event = models.read_event_settings()
    if event:
        models.backup_db(event.name, 'alliance_selection')

    # Load first playoff match
    matches = models.read_matches_by_type(models.MatchType.PLAYOFF, False)
    if len(matches) > 0:
        arena_commands.load_match(matches[0].id)

    return {'status': 'success'}


@router.post('/timer/config')
async def set_timer_config(time_limit_sec: int) -> dict:
    """Set alliance selection timer limit."""
    global alliance_selection_time_limit_sec
    alliance_selection_time_limit_sec = time_limit_sec
    return {'status': 'success', 'time_limit_sec': time_limit_sec}


@router.post('/timer/start')
async def start_timer() -> dict:
    """Start alliance selection timer."""
    arena_commands.start_alliance_selection_timer(alliance_selection_time_limit_sec)
    return {'status': 'success'}


@router.post('/timer/stop')
async def stop_timer() -> dict:
    """Stop alliance selection timer."""
    arena_commands.stop_alliance_selection_timer()
    return {'status': 'success'}
