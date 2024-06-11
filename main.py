import fastapi
from models.database import db

app = fastapi.FastAPI()
db.bind(provider='sqlite', filename='db.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)