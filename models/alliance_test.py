import unittest
from .database import db
from .alliance import *
from .match import Match, MATCH_TYPE


class TestAlliance(unittest.TestCase):
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

	def build_test_alliances(self):
		create_alliance(Alliance(id=2, team_ids=[7641, 6998, 8121], line_up=[6998, 7641, 8121]))
		create_alliance(Alliance(id=1, team_ids=[1, 2, 3, 4, 5], line_up=[2, 1, 3]))

	def test_read_nonexist_alliance(self):
		alliance = read_alliance_by_id(7641)
		self.assertIsNone(alliance)

	def test_alliance_crud(self):
		alliance_ex = Alliance(id=3, team_ids=[7641, 6998, 8121, 8790], line_up=[8121, 7641, 6998])
		alliance = create_alliance(alliance_ex)
		alliance_2 = read_alliance_by_id(3)
		self.assertEqual(alliance, alliance_ex)
		self.assertEqual(alliance_2, alliance_ex)

		alliance_ex.team_ids.append(8121)
		alliance = update_alliance(alliance_ex)
		alliance_2 = read_alliance_by_id(3)
		self.assertEqual(alliance, alliance_ex)
		self.assertEqual(alliance_2, alliance_ex)

		delete_alliance(alliance_ex.id)
		alliance_2 = read_alliance_by_id(3)
		self.assertIsNone(alliance_2)

	def test_update_alliance_from_match(self):
		alliance_ex = Alliance(id=3, team_ids=[7641, 6998, 8121, 8790], line_up=[8121, 7641, 6998])
		create_alliance(alliance_ex)
		alliance_1 = update_alliance_from_match(3, [8790, 6083, 8121])
		alliance_2 = read_alliance_by_id(3)
		self.assertEqual([7641, 6998, 8121, 8790, 6083], alliance_2.team_ids)
		self.assertEqual([8790, 6083, 8121], alliance_2.line_up)

	def test_trunate_alliance_teams(self):
		alliance_ex = Alliance(id=1, team_ids=[7641, 6998, 8121, 8790], line_up=[8121, 7641, 6998])
		truncate_alliance()
		alliance_2 = read_alliance_by_id(1)
		self.assertIsNone(alliance_2)

	def test_read_all_alliances(self):
		alliances = read_all_alliances()
		self.assertEqual([], alliances)
		self.build_test_alliances()
		alliances = read_all_alliances()
		self.assertEqual(2, len(alliances))
		self.assertEqual(1, alliances[0].id)
		self.assertEqual([1, 2, 3, 4, 5], alliances[0].team_ids)
		self.assertEqual(2, alliances[1].id)
		self.assertEqual([7641, 6998, 8121], alliances[1].team_ids)

	def test_off_field_team_ids(self):
		self.build_test_alliances()

		match = Match(
			type=MATCH_TYPE.playoff,
			type_order=1,
			playoff_red_alliance=1,
			playoff_blue_alliance=2,
			red1=2,
			red2=3,
			red3=4,
			blue1=7641,
			blue2=6998,
			blue3=8121,
		)

		red_off_field_teams, blue_off_field_teams = read_off_field_team_ids(match)
		self.assertEqual([1, 5], red_off_field_teams)
		self.assertEqual([], blue_off_field_teams)

		match.red1 = 1
		match.red2 = 5
		red_off_field_teams, blue_off_field_teams = read_off_field_team_ids(match)
		self.assertEqual([2, 3], red_off_field_teams)
		self.assertEqual([], blue_off_field_teams)

		match.playoff_blue_alliance = 0
		match.playoff_red_alliance = 0
		red_off_field_teams, blue_off_field_teams = read_off_field_team_ids(match)
		self.assertEqual([], red_off_field_teams)
		self.assertEqual([], blue_off_field_teams)

		match = Match(
			type=MATCH_TYPE.playoff,
			type_order=1,
			playoff_red_alliance=2,
			playoff_blue_alliance=1,
			red1=7641,
			red2=6998,
			red3=8121,
			blue1=1,
			blue2=2,
			blue3=3,
		)
		red_off_field_teams, blue_off_field_teams = read_off_field_team_ids(match)
		self.assertEqual([], red_off_field_teams)
		self.assertEqual([4, 5], blue_off_field_teams)
