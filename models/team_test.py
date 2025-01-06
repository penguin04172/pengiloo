import unittest

from .database import db
from .team import (
	Team,
	create_team,
	delete_team,
	read_all_teams,
	read_team_by_id,
	truncate_teams,
	update_team,
)


class TeamTest(unittest.TestCase):
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

	def test_team_crud(self):
		team = Team(
			**{
				'id': 7641,
				'name': "National Tainan Girls' Senior High School",
				'nickname': 'Normal Force',
				'city': 'Tainan',
				'state_prov': 'TN',
				'country': 'Chinese Taipei',
				'rookie_year': 2019,
				'robot_name': 'little princess',
			}
		)

		create_team(team)
		team_get = read_team_by_id(7641)
		self.assertEqual(team_get.name, team.name)

		team.name = 'Updated Name'
		team_get = update_team(team)
		team_get2 = read_team_by_id(7641)
		self.assertEqual(team_get.name, team.name)
		self.assertEqual(team_get2.name, team.name)

		delete_team(7641)
		team_get = read_team_by_id(7641)
		self.assertIsNone(team_get)

	def test_team_truncate(self):
		team = Team(
			**{
				'id': 7641,
				'name': "National Tainan Girls' Senior High School",
				'nickname': 'Normal Force',
				'city': 'Tainan',
				'state_prov': 'TN',
				'country': 'Chinese Taipei',
				'rookie_year': 2019,
				'robot_name': 'little princess',
			}
		)

		team_get = create_team(team)
		self.assertEqual(team.name, team_get.name)
		truncate_teams()
		team_get = read_team_by_id(7641)
		self.assertIsNone(team_get)

	def test_get_all_teams(self):
		teams = read_all_teams()
		self.assertEqual(teams, [])

		team_num = 20
		for i in range(team_num):
			create_team(Team(id=i + 1, rookie_year=2024))
		teams = read_all_teams()
		self.assertEqual(team_num, len(teams))

		for i in range(team_num):
			self.assertEqual(i + 1, teams[i].id)
