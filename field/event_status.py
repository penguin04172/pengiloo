from datetime import datetime

from pydantic import BaseModel

import models

from .specs import EARLY_LATE_THRESHOLD_MIN, MAX_MATCH_GAP_MIN, MatchState

MAX_EXPECTED_CYCLE_TIME_SEC = 900


class EventStatus(BaseModel):
    cycle_time: str
    early_late_message: str
    last_match_start_time: datetime
    last_match_scheduled_start_time: datetime


class EventStatusMixin:
    event_status: EventStatus

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_cycle_time(self, match_start_time: datetime):
        expected_cycle_time_sec = (
            self.current_match.scheduled_time - self.event_status.last_match_scheduled_start_time
        ).total_seconds()

        if (
            self.event_status.last_match_start_time == datetime.fromtimestamp(0)
            or expected_cycle_time_sec > MAX_EXPECTED_CYCLE_TIME_SEC
            or self.current_match.type == models.MATCH_TYPE.test
        ):
            self.event_status.cycle_time = ''
        else:
            cycle_time_sec = int(
                (match_start_time - self.event_status.last_match_start_time).total_seconds()
            )
            hours = cycle_time_sec // 3600
            minutes = (cycle_time_sec % 3600) // 60
            seconds = cycle_time_sec % 60
            if hours > 0:
                self.event_status.cycle_time = f'{hours}:{minutes:02}:{seconds:02}'
            else:
                self.event_status.cycle_time = f'{minutes}:{seconds:02}'

            delta_sec = cycle_time_sec - int(expected_cycle_time_sec)
            direction = 'faster' if delta_sec < 0 else 'slower'
            delta_sec = abs(delta_sec)
            self.event_status.cycle_time += (
                f' ({delta_sec // 60}m:{delta_sec % 60}s {direction} than scheduled)'
            )

        self.event_status.last_match_start_time = match_start_time
        self.event_status.last_match_scheduled_start_time = self.current_match.scheduled_time
        self.event_status_notifier.notify()

    def update_early_late_message(self):
        new_early_late_message = self.get_early_late_message()
        if new_early_late_message != self.event_status.early_late_message:
            self.event_status.early_late_message = new_early_late_message
            self.event_status_notifier.notify()

    def get_early_late_message(self):
        current_match = self.current_match
        if current_match.type == models.MATCH_TYPE.test:
            return ''
        if current_match.is_complete():
            return ''

        minutes_late = 0.0
        if self.match_state > MatchState.PRE_MATCH and self.match_state < MatchState.POST_MATCH:
            minutes_late = (
                current_match.started_at - current_match.scheduled_time
            ).total_seconds() / 60
        else:
            matches = models.read_matches_by_type(current_match.type, False)

            previous_match_index = -1
            next_match_index = len(matches)
            for i, match in enumerate(matches):
                if match.id == current_match.id:
                    previous_match_index = i - 1
                    next_match_index = i + 1
                    break

            if self.match_state in [
                MatchState.PRE_MATCH,
                MatchState.TIMEOUT_ACTIVE,
                MatchState.POST_TIMEOUT,
            ]:
                current_minutes_late = (
                    datetime.now() - current_match.scheduled_time
                ).total_seconds() / 60
                if (
                    previous_match_index >= 0
                    and (
                        current_match.scheduled_time - matches[previous_match_index].scheduled_time
                    ).total_seconds()
                    <= MAX_MATCH_GAP_MIN * 60
                ):
                    previous_match = matches[previous_match_index]
                    previous_minutes_late = (
                        previous_match.started_at - previous_match.scheduled_time
                    ).total_seconds() / 60
                    minutes_late = max(current_minutes_late, previous_minutes_late)
                else:
                    minutes_late = max(current_minutes_late, 0.0)

            elif self.match_state == MatchState.POST_MATCH:
                current_minutes_late = (
                    current_match.started_at - current_match.scheduled_time
                ).total_seconds() / 60
                if next_match_index < len(matches):
                    next_match = matches[next_match_index]
                    next_minutes_late = (
                        datetime.now() - next_match.scheduled_time
                    ).total_seconds() / 60
                    minutes_late = max(current_minutes_late, next_minutes_late)
                else:
                    minutes_late = current_minutes_late

        if minutes_late > EARLY_LATE_THRESHOLD_MIN:
            return f'Event is running {int(minutes_late)} minutes late'
        elif minutes_late < -EARLY_LATE_THRESHOLD_MIN:
            return f'Event is running {int(-minutes_late)} minutes early'

        return 'Event is running on schedule'
