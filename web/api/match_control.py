import asyncio
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import field
import game
import models
import tournament
import ws
from web.arena import get_arena

router = APIRouter(prefix='/match/control', tags=['match_play'])


class MatchControlListItem(BaseModel):
    id: int
    short_name: str
    time: str
    status: game.MatchStatus
    color_class: str = ''

    def __lt__(self, other):
        return (
            self.status == game.MatchStatus.MATCH_SCHEDULE
            and other.status != game.MatchStatus.MATCH_SCHEDULE
        )


class MatchLoadResponse(BaseModel):
    matches_by_type: dict[models.MatchType, list[MatchControlListItem]]
    current_match_type: models.MatchType


@router.get('/load')
async def load_match():
    pratice_matches = build_match_play_list(models.MatchType.PRACTICE)
    qualification_matches = build_match_play_list(models.MatchType.QUALIFICATION)
    playoff_matches = build_match_play_list(models.MatchType.PLAYOFF)

    matches_by_type = {
        models.MatchType.PRACTICE: pratice_matches,
        models.MatchType.QUALIFICATION: qualification_matches,
        models.MatchType.PLAYOFF: playoff_matches,
    }
    current_match_type = get_arena().current_match.type
    if current_match_type == models.MatchType.TEST:
        current_match_type = models.MatchType.PRACTICE

    return MatchLoadResponse(matches_by_type=matches_by_type, current_match_type=current_match_type)


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    notifiers_task = asyncio.create_task(
        ws.handle_notifiers(
            websocket,
            get_arena().match_timing_notifier,
            get_arena().alliance_station_display_mode_notifier,
            get_arena().arena_status_notifier,
            get_arena().audience_display_mode_notifier,
            get_arena().event_status_notifier,
            get_arena().match_load_notifier,
            get_arena().match_time_notifier,
            get_arena().realtime_score_notifier,
            get_arena().score_posted_notifier,
            get_arena().scoring_status_notifier,
        )
    )

    try:
        while True:
            data = await websocket.receive_json()
            if 'type' not in data:
                continue
            command = data['type']
            payload = data.get('data', {})

            if command == 'load_match':
                if 'match_id' not in payload:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match ID not provided'}}
                    )
                    continue
                try:
                    get_arena().reset_match()
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

                match_id = int(payload['match_id'])
                try:
                    if match_id == 0:
                        await get_arena().load_test_match()
                    else:
                        match = models.read_match_by_id(match_id)
                        if match is None:
                            await websocket.send_json(
                                {'type': 'error', 'data': {'message': 'Match not found'}}
                            )
                            continue
                        await get_arena().load_match(match)
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'show_result':
                if 'match_id' not in payload:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match ID not provided'}}
                    )
                    continue

                match_id = int(payload['match_id'])
                if match_id == 0:
                    get_arena().saved_match = models.Match(type=models.MatchType.TEST, type_order=0)
                    get_arena().saved_match_result = models.MatchResult(
                        match_id=0, match_type=models.MatchType.TEST
                    )
                    await get_arena().score_posted_notifier.notify()
                    continue

                match = models.read_match_by_id(match_id)
                if match is None:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match not found'}}
                    )
                    continue

                match_result = models.read_match_result_for_match(match_id)
                if match_result is None:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match result not found'}}
                    )
                    continue

                if match.should_update_ranking():
                    get_arena().saved_rankings = models.read_all_rankings()
                else:
                    get_arena().saved_rankings = game.Rankings()

                get_arena().saved_match = match
                get_arena().saved_match_result = match_result
                await get_arena().score_posted_notifier.notify()

            elif command == 'substitute_teams':
                if not all(
                    station in payload
                    for station in ['red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']
                ):
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Team IDs not provided'}}
                    )
                    continue

                red1 = int(payload.get('red1', 0))
                red2 = int(payload.get('red2', 0))
                red3 = int(payload.get('red3', 0))
                blue1 = int(payload.get('blue1', 0))
                blue2 = int(payload.get('blue2', 0))
                blue3 = int(payload.get('blue3', 0))

                try:
                    await get_arena().substitute_team(red1, red2, red3, blue1, blue2, blue3)
                except ValueError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'toggle_bypass':
                if 'station' not in payload:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Station not provided'}}
                    )
                    continue

                station = payload['station']
                if station not in get_arena().alliance_stations:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Invalid station'}}
                    )
                    continue

                get_arena().alliance_stations[station].bypass = (
                    not get_arena().alliance_stations[station].bypass
                )
                await ws.write_notifier(websocket, get_arena().arena_status_notifier)

            elif command == 'start_match':
                mute_match_sounds = payload.get('mute_match_sounds', False)
                get_arena().mute_match_sounds = mute_match_sounds
                try:
                    await get_arena().start_match()
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'abort_match':
                try:
                    await get_arena().abort_match()
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'signal_reset':
                if get_arena().match_state not in [
                    field.MatchState.POST_MATCH,
                    field.MatchState.PRE_MATCH,
                ]:
                    continue

                get_arena().field_reset = True
                get_arena().alliance_station_display_mode = 'fieldReset'
                await get_arena().alliance_station_display_mode_notifier.notify()

            elif command == 'commit_results':
                if get_arena().match_state != field.MatchState.POST_MATCH:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Match not in POST_MATCH state'}}
                    )
                    continue

                try:
                    await commit_current_match_score()
                    get_arena().reset_match()
                    await get_arena().load_next_match(True)
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'discard_results':
                try:
                    get_arena().reset_match()
                    await get_arena().load_next_match(False)
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'set_audience_display':
                if 'data' not in data:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Mode not provided'}}
                    )
                    continue

                mode = data['data']
                await get_arena().set_audience_display_mode(mode)

            elif command == 'set_alliance_station_display':
                if 'data' not in data:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Mode not provided'}}
                    )
                    continue

                mode = data['data']
                await get_arena().set_alliance_station_display_mode(mode)

            elif command == 'start_timeout':
                if 'duration_sec' not in payload:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Duration not provided'}}
                    )
                    continue

                duration_sec = int(payload['duration_sec'])
                try:
                    await get_arena().start_timeout('Timeout', duration_sec)
                except RuntimeError as e:
                    await websocket.send_json({'type': 'error', 'data': {'message': str(e)}})
                    continue

            elif command == 'set_test_match_name':
                if get_arena().current_match.type != models.MatchType.TEST:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Current match is not a test match'}}
                    )
                    continue
                if 'name' not in payload:
                    await websocket.send_json(
                        {'type': 'error', 'data': {'message': 'Name not provided'}}
                    )
                    continue

                get_arena().current_match.long_name = payload['name']
                await get_arena().match_load_notifier.notify()

            else:
                await websocket.send_json({'type': 'error', 'data': {'message': 'Invalid command'}})

    except WebSocketDisconnect:
        pass
    finally:
        notifiers_task.cancel()
        try:
            await notifiers_task
        except asyncio.CancelledError:
            pass


async def commit_match_score(
    match: models.Match, match_result: models.MatchResult, is_match_review_edit: bool
):
    updated_rankings = game.Rankings()
    if match.type == models.MatchType.PLAYOFF:
        match_result.correct_playoff_score()

    match.score_commit_at = datetime.now()
    red_score_summary = match_result.red_score_summary()
    blue_score_summary = match_result.blue_score_summary()
    match.status = game.determine_match_status(
        red_score_summary, blue_score_summary, match.use_tiebreak_criteria
    )
    if match.type != models.MatchType.TEST:
        if match_result.play_number == 0:
            prev_match_result = models.read_match_result_for_match(match.id)
            if prev_match_result is not None:
                match_result.play_number = prev_match_result.play_number + 1
            else:
                match_result.play_number = 1

            models.create_match_result(match_result)
        else:
            models.update_match_result(match_result)

        models.update_match(match)

        if match.should_update_cards():
            tournament.calculate_team_cards(match.type)

        if match.should_update_ranking():
            rankings = tournament.calculate_rankings(is_match_review_edit)
            updated_rankings = rankings

        if match.should_update_playoff_matches():
            models.update_alliance_from_match(
                match.playoff_red_alliance, [match.red1, match.red2, match.red3]
            )
            models.update_alliance_from_match(
                match.playoff_blue_alliance, [match.blue1, match.blue2, match.blue3]
            )

            get_arena().update_playoff_tournament()

        if get_arena().playoff_tournament.is_complete():
            winner_alliance_id = get_arena().playoff_tournament.winning_alliance_id()
            finalist_alliance_id = get_arena().playoff_tournament.finalist_alliance_id()

            tournament.create_or_update_winner_and_finalist_awards(
                winner_alliance_id, finalist_alliance_id
            )

        if get_arena().event.tba_publishing_enabled and match.type != models.MatchType.PRACTICE:
            pass

        models.backup_db(get_arena().event.name, f'post_{match.type}_match_{match.short_name}')

    if not is_match_review_edit:
        get_arena().saved_match = match
        get_arena().saved_match_result = match_result
        get_arena().saved_rankings = updated_rankings
        await get_arena().score_posted_notifier.notify()


def get_current_match_result():
    return models.MatchResult(
        match_id=get_arena().current_match.id,
        match_type=get_arena().current_match.type,
        red_score=get_arena().red_realtime_score.current_score,
        blue_score=get_arena().blue_realtime_score.current_score,
        red_cards=get_arena().red_realtime_score.cards,
        blue_cards=get_arena().blue_realtime_score.cards,
    )


async def commit_current_match_score():
    return await commit_match_score(get_arena().current_match, get_current_match_result(), False)


def build_match_play_list(match_type: models.MatchType):
    matches = models.read_matches_by_type(match_type, False)
    match_play_list = []
    for match in matches:
        list_item = MatchControlListItem(
            id=match.id,
            short_name=match.short_name,
            time=match.scheduled_time.strftime('%I:%M %p'),
            status=match.status,
        )
        if match.status == game.MatchStatus.RED_WON_MATCH:
            list_item.color_class = 'red'
        elif match.status == game.MatchStatus.BLUE_WON_MATCH:
            list_item.color_class = 'blue'
        elif match.status == game.MatchStatus.TIE_MATCH:
            list_item.color_class = 'yellow'
        else:
            list_item.color_class = ''

        if get_arena().current_match is not None and get_arena().current_match.id == match.id:
            list_item.color_class = 'green'

        match_play_list.append(list_item)

    return sorted(match_play_list)
