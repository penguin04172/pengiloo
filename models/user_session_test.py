import unittest
from .database import db
from .user_session import *
from datetime import datetime


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

	def test_user_session_crud(self):
		user_session = UserSession(
			**{'id': 0, 'token': 'token1', 'user_name': 'Pengu', 'created_at': datetime.now()}
		)

		user_session1 = create_user_session(user_session)
		user_session2 = read_user_session_by_token(user_session.token)
		self.assertEqual(user_session.token, user_session2.token)
		self.assertEqual(user_session.user_name, user_session2.user_name)
		self.assertEqual(user_session.created_at, user_session2.created_at)

		delete_user_session(user_session.id)
		user_session2 = read_user_session_by_token(user_session.token)
		self.assertIsNone(user_session2)

	def test_user_session_truncate(self):
		user_session = UserSession(
			**{'id': 0, 'token': 'token1', 'user_name': 'Pengu', 'created_at': datetime.now()}
		)

		user_session_get = create_user_session(user_session)
		self.assertEqual(user_session.token, user_session_get.token)
		truncate_user_sessions()
		user_session_get = read_user_session_by_token('token1')
		self.assertIsNone(user_session_get)
