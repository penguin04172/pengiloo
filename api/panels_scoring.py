import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import field
import ws

from .arena import api_arena

router = APIRouter(prefix='/panels/scoring', tags=['panels'])


@router.websocket('/{alliance}/websocket')
async def websocket_endpoint(alliance: str, websocket: WebSocket):
    await websocket.accept()

    if alliance not in ['red', 'blue']:
        await websocket.close(1008, 'Invalid alliance')
        return

    if alliance == 'red':
        realtime_score = api_arena.red_realtime_score
    else:
        realtime_score = api_arena.blue_realtime_score

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(
            websocket,
            api_arena.match_load_notifier,
            api_arena.match_time_notifier,
            api_arena.realtime_score_notifier,
            api_arena.reload_displays_notifier,
        )
    )

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            command = data['type']

            score = realtime_score.current_score
            score_changed = False

            if command == 'commit_match':
                if api_arena.match_state != field.MatchState.POST_MATCH:
                    await websocket.send_json(
                        {'type': 'error', 'message': 'Match not in POST_MATCH state'}
                    )
                    continue
                else:
                    api_arena.scoring_panel_registry.set_score_commited(alliance, websocket)
                    await api_arena.scoring_status_notifier.notify()
            else:
                payload = data['data']

                if score_changed:
                    await api_arena.realtime_score_notifier.notify()

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass
        await websocket.close()
