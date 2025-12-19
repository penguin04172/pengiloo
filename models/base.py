import os
import shutil
from datetime import datetime
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def backup_db(event_name: str, reason: str):
    os.makedirs(os.path.join('.', 'db/backups'), mode=0o755, exist_ok=True)
    # Assuming sqlite, the file is just the filename
    shutil.copy(
        sqlite_file_name,
        f'db/backups/{event_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d%H%M%S")}_{reason}.db',
    )
