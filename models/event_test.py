import unittest
from .database import db
from .event import *


class EventTest(unittest.TestCase):
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

	def test_event_read_write(self):
		event = Event(
			id=1,
			name='Untitled Event',
			playoff_type=PLAYOFF_TYPE.double_elimination,
			num_playoff_alliance=8,
			selection_round_2_order='L',
			selection_round_3_order='',
			tba_download_enabled=True,
			ap_channel=36,
			warmup_duration_sec=0,
			auto_duration_sec=15,
			pause_duration_sec=3,
			teleop_duration_sec=135,
			warning_remaining_duration_sec=20,
			melody_bonus_threshold_without_coop=18,
			melody_bonus_threshold_with_coop=15,
			amplification_note_limit=4,
			amplification_duration_sec=10,
		)
		event_settings = read_event_settings()
		self.assertEqual(event.name, event_settings.name)
		self.assertEqual(event.playoff_type, event_settings.playoff_type)
		self.assertEqual(event.num_playoff_alliance, event_settings.num_playoff_alliance)
		self.assertEqual(event.selection_round_2_order, event_settings.selection_round_2_order)
		self.assertEqual(event.selection_round_3_order, event_settings.selection_round_3_order)
		self.assertEqual(event.tba_download_enabled, event_settings.tba_download_enabled)
		self.assertEqual(event.ap_channel, event_settings.ap_channel)
		self.assertEqual(event.warmup_duration_sec, event_settings.warmup_duration_sec)
		self.assertEqual(event.auto_duration_sec, event_settings.auto_duration_sec)
		self.assertEqual(event.pause_duration_sec, event_settings.pause_duration_sec)
		self.assertEqual(event.teleop_duration_sec, event_settings.teleop_duration_sec)
		self.assertEqual(
			event.warning_remaining_duration_sec, event_settings.warning_remaining_duration_sec
		)
		self.assertEqual(
			event.melody_bonus_threshold_without_coop,
			event_settings.melody_bonus_threshold_without_coop,
		)
		self.assertEqual(
			event.melody_bonus_threshold_with_coop, event_settings.melody_bonus_threshold_with_coop
		)
		self.assertEqual(event.amplification_note_limit, event_settings.amplification_note_limit)
		self.assertEqual(
			event.amplification_duration_sec, event_settings.amplification_duration_sec
		)

		event_settings.name = 'Snowball War'
		event_settings.num_playoff_alliance = 6
		event_settings.selection_round_2_order = 'F'
		event_settings.selection_round_3_order = 'L'

		new_event_settings = update_event_settings(event_settings)
		self.assertEqual(event_settings, new_event_settings)

		renew_event_settings = read_event_settings()
		self.assertEqual(event_settings, renew_event_settings)
