import os
import shutil
from datetime import datetime

from pony.orm import Database, db_session

db = Database()


@db_session
def backup_db(event_name: str, reason: str):
    os.makedirs(os.path.join('.', '/db/backups'), mode=0o755, exist_ok=True)
    shutil.copy(
        db.provider_name,
        f'/db/backups/{event_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d%H%M%S")}_{reason}.db',
    )
