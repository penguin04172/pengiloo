import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import field
import game
import ws
from web.arena import get_arena

router = APIRouter(prefix='/panels/scoring', tags=['panels'])


@router.websocket('/{alliance}/websocket')
async def websocket_endpoint(alliance: str, websocket: WebSocket):
    await websocket.accept()

    if alliance not in ['red', 'blue']:
        await websocket.close(1008, 'Invalid alliance')
        return

    realtime_score = (
        get_arena().red_realtime_score if alliance == 'red' else get_arena().blue_realtime_score
    )
    opponent_realtime_score = (
        get_arena().blue_realtime_score if alliance == 'red' else get_arena().red_realtime_score
    )

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(
            websocket,
            get_arena().match_load_notifier,
            get_arena().match_time_notifier,
            get_arena().realtime_score_notifier,
            get_arena().reload_displays_notifier,
        )
    )

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            command = data['type']

            score = realtime_score.current_score
            opponent_score = opponent_realtime_score.current_score
            score_changed = False

            if command == 'commit_match':
                if get_arena().match_state != field.MatchState.POST_MATCH:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match not in POST_MATCH state'}}
                    )
                    continue
                else:
                    get_arena().scoring_panel_registry.set_score_commited(alliance, websocket)
                    await get_arena().scoring_status_notifier.notify()
            else:
                payload = data['data']

                if command == 'leave':
                    if 2 >= payload['position'] >= 0:
                        score_changed, score.leave_statuses[payload['position']] = set_goal(
                            score.leave_statuses[payload['position']], payload['state']
                        )

                elif command == 'cage':
                    if 2 >= payload['position'] >= 0:
                        if score.cage_statuses[payload['position']] == max(game.CageStatus):
                            score.cage_statuses[payload['position']] = min(game.CageStatus)
                        else:
                            score.cage_statuses[payload['position']] += 1
                        score_changed = True

                elif command == 'endgame':
                    if 2 >= payload['position'] >= 0:
                        if score.endgame_statuses[payload['position']] == max(game.EndgameStatus):
                            score.endgame_statuses[payload['position']] = min(game.EndgameStatus)
                        else:
                            score.endgame_statuses[payload['position']] += 1
                        score_changed = True

                elif command == 'trough_auto':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.auto_trough_coral = increment_goal(
                            score.score_elements.auto_trough_coral
                        )
                        _, score.score_elements.total_trough_coral = increment_goal(
                            score.score_elements.total_trough_coral
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.auto_trough_coral = decrement_goal(
                            score.score_elements.auto_trough_coral
                        )
                        _, score.score_elements.total_trough_coral = decrement_goal(
                            score.score_elements.total_trough_coral
                        )

                elif command == 'trough_total':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.total_trough_coral = increment_goal(
                            score.score_elements.total_trough_coral
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.total_trough_coral = decrement_goal(
                            score.score_elements.total_trough_coral
                        )

                elif command == 'processor_auto':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.auto_processor_algae = increment_goal(
                            score.score_elements.auto_processor_algae
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.auto_processor_algae = decrement_goal(
                            score.score_elements.auto_processor_algae
                        )

                elif command == 'processor_teleop':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.teleop_processor_algae = increment_goal(
                            score.score_elements.teleop_processor_algae
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.teleop_processor_algae = decrement_goal(
                            score.score_elements.teleop_processor_algae
                        )

                elif command == 'net_auto':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.auto_net_algae = increment_goal(
                            score.score_elements.auto_net_algae
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.auto_net_algae = decrement_goal(
                            score.score_elements.auto_net_algae
                        )

                elif command == 'net_teleop':
                    if payload['action'] == 'plus':
                        score_changed, score.score_elements.teleop_net_algae = increment_goal(
                            score.score_elements.teleop_net_algae
                        )
                    elif payload['action'] == 'minus':
                        score_changed, score.score_elements.teleop_net_algae = decrement_goal(
                            score.score_elements.teleop_net_algae
                        )

                elif command == 'branches_auto':
                    if (
                        0 <= payload['position'] < game.BranchLocation.COUNT
                        and 0 <= payload['level'] < game.BranchLevel.COUNT
                    ):
                        (
                            score_changed,
                            score.score_elements.branches_auto[payload['position']][
                                payload['level']
                            ],
                        ) = set_goal(
                            score.score_elements.branches_auto[payload['position']][
                                payload['level']
                            ],
                            payload['state'],
                        )
                        (
                            _,
                            score.score_elements.branches[payload['position']][payload['level']],
                        ) = set_goal(
                            score.score_elements.branches[payload['position']][payload['level']],
                            payload['state'],
                        )

                elif command == 'branches':
                    if (
                        0 <= payload['position'] < game.BranchLocation.COUNT
                        and 0 <= payload['level'] < game.BranchLevel.COUNT
                    ):
                        (
                            score_changed,
                            score.score_elements.branches[payload['position']][payload['level']],
                        ) = set_goal(
                            score.score_elements.branches[payload['position']][payload['level']],
                            payload['state'],
                        )

                elif command == 'branches_algaes':
                    if 0 <= payload['position'] < 6 and 0 <= payload['level'] < 2:
                        (
                            score_changed,
                            score.score_elements.branch_algaes[payload['position']][
                                payload['level']
                            ],
                        ) = set_goal(
                            score.score_elements.branch_algaes[payload['position']][
                                payload['level']
                            ],
                            payload['state'],
                        )

                if score_changed:
                    await asyncio.to_thread(score.summarize, opponent_score)
                    await get_arena().realtime_score_notifier.notify()

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass


def increment_goal(goal: object):
    goal += 1
    return True, goal


def decrement_goal(goal: object):
    if goal > 0:
        goal -= 1
        return True, goal
    return False, goal


def toggle_goal(goal: object):
    goal = not goal
    return True, goal


def set_goal(goal: object, value: Any):
    if goal != value:
        return True, value
    return False, goal
