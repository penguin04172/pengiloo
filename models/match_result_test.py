import unittest

from game.amp_speaker import AmpSpeaker
from game.foul import Foul
from game.score import ENDGAME_STATUS, Score

from .database import db
from .match_result import (
	MATCH_TYPE,
	MatchResult,
	create_match_result,
	delete_match_result,
	read_match_result_for_match,
	truncate_match_results,
	update_match_result,
)


class MatchResultTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		db.bind(provider='sqlite', filename=':memory:', create_db=True)
		db.generate_mapping(create_tables=True)

	@classmethod
	def tearDownClass(cls) -> None:
		db.disconnect()

	def setUp(self) -> None:
		db.create_tables(True)

	def tearDown(self) -> None:
		db.drop_all_tables(with_all_data=True)

	def score_1(self) -> Score:
		return Score(
			fouls=[
				Foul(is_technical=True, team_id=7641, rule_id=13),
				Foul(is_technical=False, team_id=6998, rule_id=14),
				Foul(is_technical=False, team_id=6998, rule_id=14),
				Foul(is_technical=True, team_id=7641, rule_id=15),
				Foul(is_technical=True, team_id=7641, rule_id=15),
				Foul(is_technical=True, team_id=7641, rule_id=15),
				Foul(is_technical=True, team_id=7641, rule_id=15),
			],
			leave_statuses=[True, True, False],
			amp_speaker=AmpSpeaker(
				coop_activated=True,
				auto_amp_notes=1,
				teleop_amp_notes=4,
				auto_speaker_notes=6,
				teleop_unamplified_speaker_notes=1,
				teleop_amplified_speaker_notes=5,
			),
			endgame_statuses=[ENDGAME_STATUS.park, ENDGAME_STATUS.none, ENDGAME_STATUS.stage_left],
			microphone_statuses=[False, True, True],
			trap_statuses=[True, True, False],
			playoff_dq=False,
		)

	def score_2(self) -> Score:
		return Score(
			leave_statuses=[False, True, False],
			amp_speaker=AmpSpeaker(
				coop_activated=False,
				auto_amp_notes=0,
				teleop_amp_notes=51,
				auto_speaker_notes=8,
				teleop_unamplified_speaker_notes=3,
				teleop_amplified_speaker_notes=23,
			),
			endgame_statuses=[
				ENDGAME_STATUS.stage_left,
				ENDGAME_STATUS.stage_center,
				ENDGAME_STATUS.stage_center,
			],
			microphone_statuses=[False, True, True],
			trap_statuses=[False, False, False],
			fouls=[],
			playoff_dq=False,
		)

	def build_test_match_result(self, match_id: int, play_number: int):
		match_result = MatchResult(
			match_id=match_id, play_number=play_number, match_type=MATCH_TYPE.qualification
		)
		match_result.red_score = self.score_1()
		match_result.blue_score = self.score_2()
		match_result.red_cards = {'6998': 'yellow'}
		match_result.blue_cards = {}
		return match_result

	def test_read_nonexist_match_result(self):
		result = read_match_result_for_match(7641)
		self.assertIsNone(result)

	def test_match_result_crud(self):
		match_result = create_match_result(self.build_test_match_result(7641, 5))
		match_result_2 = read_match_result_for_match(7641)
		self.assertEqual(match_result, match_result_2)

		match_result.blue_score.endgame_statuses = [
			ENDGAME_STATUS.park,
			ENDGAME_STATUS.none,
			ENDGAME_STATUS.stage_right,
		]
		update_match_result(match_result)
		match_result_2 = read_match_result_for_match(7641)
		self.assertEqual(match_result, match_result_2)

		delete_match_result(match_result.id)
		match_result_2 = read_match_result_for_match(7641)
		self.assertIsNone(match_result_2)

	def test_truncate_match_results(self):
		create_match_result(self.build_test_match_result(7641, 1))
		truncate_match_results()
		match_result_2 = read_match_result_for_match(7641)
		self.assertIsNone(match_result_2)

	def test_read_match_result_for_match(self):
		create_match_result(self.build_test_match_result(7641, 2))
		match_result_2 = create_match_result(self.build_test_match_result(7641, 5))
		create_match_result(self.build_test_match_result(7641, 4))

		match_result_4 = read_match_result_for_match(7641)
		self.assertEqual(match_result_2, match_result_4)
