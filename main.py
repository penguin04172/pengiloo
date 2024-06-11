import fastapi
from models.database import db

from api import team
from web import index

app = fastapi.FastAPI()
app.include_router(team.router)
app.include_router(index.router)

db.bind(provider='sqlite', filename='db.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)
