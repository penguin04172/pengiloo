from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Session, select

from .base import engine


class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str
    user_name: Optional[str] = None
    created_at: datetime = Field(default=datetime(1970, 1, 1, 0, 0))


def create_user_session(session_data: UserSession) -> UserSession:
    with Session(engine) as session:
        existing = session.exec(select(UserSession).where(UserSession.token == session_data.token)).first()
        if existing:
            return existing

        session.add(session_data)
        session.commit()
        session.refresh(session_data)
        return session_data


def read_user_session_by_token(token: str) -> Optional[UserSession]:
    with Session(engine) as session:
        return session.exec(select(UserSession).where(UserSession.token == token)).first()


def delete_user_session(id: int):
    with Session(engine) as session:
        user_session = session.get(UserSession, id)
        if user_session:
            session.delete(user_session)
            session.commit()


def truncate_user_sessions():
    with Session(engine) as session:
        statement = select(UserSession)
        results = session.exec(statement)
        for us in results:
            session.delete(us)
        session.commit()
