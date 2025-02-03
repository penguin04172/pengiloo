import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import field
import game
import models
import ws

from .arena import get_arena

router = APIRouter(prefix='/panels/referee', tags=['panels'])


class FoulListResponse(BaseModel):
    match: models.Match
    red_fouls: list[game.Foul]
    blue_fouls: list[game.Foul]
    rules: dict[int, game.Rule]


@router.get('/foul_list')
async def get_foul_list() -> FoulListResponse:
    return FoulListResponse(
        match=get_arena().current_match,
        red_fouls=get_arena().red_realtime_score.current_score.fouls,
        blue_fouls=get_arena().blue_realtime_score.current_score.fouls,
        rules=game.get_all_rules(),
    )


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(
            websocket,
            get_arena().match_load_notifier,
            get_arena().match_time_notifier,
            get_arena().realtime_score_notifier,
            get_arena().reload_displays_notifier,
            get_arena().scoring_status_notifier,
        )
    )
    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            message_type = data['type']

            if message_type == 'add_foul':
                alliance = data['data'].get('alliance')
                is_major = data['data'].get('is_major')

                foul = game.Foul(
                    is_major=is_major,
                )
                if alliance == 'red':
                    get_arena().red_realtime_score.current_score.fouls.append(foul)
                elif alliance == 'blue':
                    get_arena().blue_realtime_score.current_score.fouls.append(foul)

                await get_arena().realtime_score_notifier.notify()
            elif message_type in [
                'toggle_foul_type',
                'update_foul_team',
                'update_foul_rule',
                'delete_foul',
            ]:
                alliance = data['data'].get('alliance')
                index = data['data'].get('index')
                team_id = data['data'].get('team_id')
                rule_id = data['data'].get('rule_id')

                if alliance == 'red':
                    fouls = get_arena().red_realtime_score.current_score.fouls
                else:
                    fouls = get_arena().blue_realtime_score.current_score.fouls

                if index is not None and 0 <= index < len(fouls):
                    if message_type == 'toggle_foul_type':
                        fouls[index].is_technical = not fouls[index].is_technical
                        fouls[index].rule_id = 0
                    elif message_type == 'delete_foul':
                        fouls.pop(index)
                    elif message_type == 'update_foul_rule':
                        fouls[index].rule_id = rule_id
                    elif message_type == 'update_foul_team':
                        if fouls[index].team_id == team_id:
                            fouls[index].team_id = 0
                        else:
                            fouls[index].team_id = team_id

                    await get_arena().realtime_score_notifier.notify()

                elif message_type == 'card':
                    alliance = data['data'].get('alliance')
                    team_id = data['data'].get('team_id')
                    card = data['data'].get('card')

                    if alliance == 'red':
                        cards = get_arena().red_realtime_score.cards
                    else:
                        cards = get_arena().blue_realtime_score.cards

                    if get_arena().current_match.type == models.MatchType.PLAYOFF:
                        if alliance == 'red':
                            cards[str(get_arena().current_match.red1)] = card
                            cards[str(get_arena().current_match.red2)] = card
                            cards[str(get_arena().current_match.red3)] = card
                        else:
                            cards[str(get_arena().current_match.blue1)] = card
                            cards[str(get_arena().current_match.blue2)] = card
                            cards[str(get_arena().current_match.blue3)] = card
                    else:
                        cards[str(team_id)] = card

                    await get_arena().alliance_station_display_mode_notifier.notify()

                elif message_type == 'signal_reset':
                    if get_arena().match_state != field.MatchState.POST_MATCH:
                        continue

                    get_arena().field_reset = True
                    get_arena().alliance_station_display_mode = 'field_reset'
                    await get_arena().scoring_status_notifier.notify()

                elif message_type == 'commit_match':
                    if get_arena().match_state != field.MatchState.POST_MATCH:
                        continue

                    get_arena().red_realtime_score.fouls_commited = True
                    get_arena().blue_realtime_score.fouls_commited = True
                    get_arena().field_reset = True
                    get_arena().alliance_station_display_mode = 'field_reset'
                    await get_arena().alliance_station_display_mode_notifier.notify()
                    await get_arena().scoring_status_notifier.notify()

                else:
                    await websocket.send_json(
                        {'type': 'error', 'message': f'Invalid message type{message_type}'}
                    )

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass
