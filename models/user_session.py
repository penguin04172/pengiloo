from pony.orm import *
from pydantic import BaseModel
from .database import db
from datetime import datetime


class UserSession(BaseModel):
	id: int | None = None
	token: str
	user_name: str | None = None
	created_at: datetime | None = None


class UserSessionDB(db.Entity):
	id = PrimaryKey(int)
	token = Required(str)
	user_name = Optional(str)
	created_at = Optional(datetime, default=datetime(1970, 1, 1, 0, 0), volatile=True)


@db_session
def create_user_session(session: UserSession):
	user_session = UserSessionDB.get(token=session.token)
	if user_session is not None:
		return UserSession(**user_session.to_dict())

	user_session = UserSessionDB(**session.model_dump(exclude_none=True))
	return UserSession(**user_session.to_dict())


@db_session
def read_user_session_by_token(token: str):
	user_session = UserSessionDB.get(token=token)
	if user_session is None:
		return None
	return UserSession(**user_session.to_dict())


@db_session
def delete_user_session(id: int):
	UserSessionDB[id].delete()


def truncate_user_sessions():
	db.drop_table(table_name=UserSessionDB._table_, with_all_data=True)
	db.create_tables()
