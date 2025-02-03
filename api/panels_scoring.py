import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import field
import game
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

                if command == 'leave':
                    if 3 >= payload['position'] >= 1:
                        score_changed = set_goal(
                            score.leave_statuses[payload['position'] - 1], payload['state']
                        )

                elif command == 'cage':
                    if 3 >= payload['position'] >= 1:
                        if score.cage_statuses[payload['position'] - 1] == max(game.CageStatus):
                            score.cage_statuses[payload['position'] - 1] = min(game.CageStatus)
                        else:
                            score.cage_statuses[payload['position'] - 1] += 1
                        score_changed = True

                elif command == 'endgame':
                    if 3 >= payload['position'] >= 1:
                        if score.endgame_statuses[payload['position'] - 1] == max(
                            game.EndgameStatus
                        ):
                            score.endgame_statuses[payload['position'] - 1] = min(
                                game.EndgameStatus
                            )
                        else:
                            score.endgame_statuses[payload['position'] - 1] += 1
                        score_changed = True

                elif command == 'trough_auto':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.auto_trough_coral)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.auto_trough_coral)

                elif command == 'trough_teleop':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.teleop_trough_coral)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.teleop_trough_coral)

                elif command == 'processor_auto':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.auto_processor_algae)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.auto_processor_algae)

                elif command == 'processor_teleop':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.teleop_processor_algae)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.teleop_processor_algae)

                elif command == 'net_auto':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.auto_net_algae)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.auto_net_algae)

                elif command == 'net_teleop':
                    if payload['action'] == 'plus':
                        score_changed = increment_goal(score.score_elements.teleop_net_algae)
                    elif payload['action'] == 'minus':
                        score_changed = decrement_goal(score.score_elements.teleop_net_algae)

                elif command == 'branches_auto':
                    if (
                        0 <= payload['position'] < game.BranchLocation.COUNT
                        and 0 <= payload['level'] < game.BranchLevel.COUNT
                    ):
                        score_changed = set_goal(
                            score.leave_statuses[payload['position'] - 1], payload['state']
                        )

                elif command == 'branches':
                    if (
                        0 <= payload['position'] < game.BranchLocation.COUNT
                        and 0 <= payload['level'] < game.BranchLevel.COUNT
                    ):
                        score_changed = set_goal(
                            score.leave_statuses[payload['position'] - 1], payload['state']
                        )

                elif command == 'branches_algaes':
                    if 0 <= payload['position'] < 6 and 0 <= payload['level'] < 2:
                        score_changed = set_goal(
                            score.leave_statuses[payload['position'] - 1], payload['state']
                        )

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


def increment_goal(goal: object):
    goal += 1
    return True


def decrement_goal(goal: object):
    if goal > 0:
        goal -= 1
        return True
    return False


def toggle_goal(goal: object):
    goal = not goal
    return True


def set_goal(goal: object, value: object):
    if goal != value:
        goal = value
        return True
    return False
