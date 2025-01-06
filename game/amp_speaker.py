from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import timedelta
from .game_specific import game_specific, TIME_CONSTANT
from . import match_timing


class AmpSpeaker(BaseModel):
	banked_amp_notes: int = 0
	coop_activated: bool = False
	auto_amp_notes: int = 0
	teleop_amp_notes: int = 0
	auto_speaker_notes: int = 0
	teleop_unamplified_speaker_notes: int = 0
	teleop_amplified_speaker_notes: int = 0
	last_amplified_time: timedelta = Field(timedelta(), exclude=True)
	last_amplified_speaker_notes: int = Field(0, exclude=0)

	def update_state(
		self,
		amp_note_count: int,
		speaker_note_count: int,
		amplify_button: bool,
		coop_button: bool,
		match_start_time: timedelta,
		current_time: timedelta,
	):
		new_amp_notes = amp_note_count - self.amp_notes_scored()
		new_speaker_notes = speaker_note_count - self.speaker_notes_scored()

		# Handle Auto
		auto_validity_cutoff = match_start_time + timedelta(
			seconds=match_timing.get_duration_to_auto_end()
			+ TIME_CONSTANT.speaker_auto_grace_period_sec
		)
		if current_time < auto_validity_cutoff:
			self.auto_amp_notes += new_amp_notes
			self.banked_amp_notes = min(
				self.banked_amp_notes + new_amp_notes, game_specific.BANKED_AMP_NOTE_LIMIT
			)
			self.auto_speaker_notes += new_speaker_notes

			return

		# Handle Amp
		teleop_amp_validaty_cutoff = match_start_time + timedelta(
			seconds=match_timing.get_duration_to_teleop_end()
		)
		if current_time < teleop_amp_validaty_cutoff:
			# Amp Note
			self.teleop_amp_notes += new_amp_notes
			if not self.is_amplified(current_time, False):
				self.banked_amp_notes = min(
					self.banked_amp_notes + new_amp_notes, game_specific.BANKED_AMP_NOTE_LIMIT
				)

			# Coop button
			if (
				coop_button
				and not self.coop_activated
				and self.banked_amp_notes >= 1
				and self.is_coop_window_open(match_start_time, current_time)
			):
				self.coop_activated = True
				self.banked_amp_notes -= 1

			# Amplify button
			if (
				amplify_button
				and not self.is_amplified(current_time, False)
				and self.banked_amp_notes >= 2
			):
				self.last_amplified_time = current_time
				self.last_amplified_speaker_notes = 0
				self.banked_amp_notes -= 2

		# Handle Speaker
		teleop_speaker_validity_cutoff = match_start_time + timedelta(
			seconds=match_timing.get_duration_to_teleop_end()
			+ TIME_CONSTANT.speaker_teleop_grace_period_sec
		)
		if current_time < teleop_speaker_validity_cutoff:
			while new_speaker_notes > 0 and self.is_amplified(current_time, True):
				self.teleop_amplified_speaker_notes += 1
				self.last_amplified_speaker_notes += 1
				new_speaker_notes -= 1
			self.teleop_unamplified_speaker_notes += new_speaker_notes

	def amplified_time_remaining(self, current_time: timedelta) -> float:
		time_left = timedelta(seconds=game_specific.amplification_duration_sec) - (
			current_time - self.last_amplified_time
		)
		return time_left.total_seconds() if self.is_amplified(current_time, False) else 0

	def is_coop_window_open(self, match_start_time: timedelta, current_time: timedelta) -> bool:
		coop_validity_cutoff = (
			match_start_time
			+ timedelta(seconds=match_timing.get_duration_to_teleop_start())
			+ timedelta(seconds=TIME_CONSTANT.coop_teleop_window_sec)
		)
		return (
			game_specific.melody_bonus_threshold_with_coop > 0
			and current_time < coop_validity_cutoff
		)

	def total_notes_scored(self) -> int:
		return self.amp_notes_scored() + self.speaker_notes_scored()

	def auto_note_points(self) -> int:
		return 2 * self.auto_amp_notes + 5 * self.auto_speaker_notes

	def amp_points(self) -> int:
		return 2 * self.auto_amp_notes + self.teleop_amp_notes

	def speaker_points(self) -> int:
		return (
			5 * self.auto_speaker_notes
			+ 2 * self.teleop_unamplified_speaker_notes
			+ 5 * self.teleop_amplified_speaker_notes
		)

	def amp_notes_scored(self) -> int:
		return self.auto_amp_notes + self.teleop_amp_notes

	def speaker_notes_scored(self) -> int:
		return (
			self.auto_speaker_notes
			+ self.teleop_unamplified_speaker_notes
			+ self.teleop_amplified_speaker_notes
		)

	def is_amplified(self, current_time: timedelta, include_grace_period: bool) -> bool:
		amplified_validity_cutoff = self.last_amplified_time + timedelta(
			seconds=game_specific.amplification_duration_sec
		)
		if include_grace_period:
			amplified_validity_cutoff = amplified_validity_cutoff + timedelta(
				seconds=TIME_CONSTANT.speaker_amplified_grace_period_sec
			)

		meets_time_criterion = (
			current_time > self.last_amplified_time
			and current_time < amplified_validity_cutoff
			and current_time > timedelta(seconds=match_timing.get_duration_to_auto_end())
		)
		meets_note_criterion = (
			game_specific.amplification_note_limit == 0
			or self.last_amplified_speaker_notes < game_specific.amplification_note_limit
		)
		return meets_time_criterion and meets_note_criterion
