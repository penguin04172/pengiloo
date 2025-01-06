import fastapi

from api import event, match, team
from models.database import db
from web import index

app = fastapi.FastAPI()

app.include_router(team.router)
app.include_router(event.router)
app.include_router(match.router)

app.include_router(index.router)

# db.bind(provider='sqlite', filename='db.sqlite3', create_db=True)
db.bind(provider='sqlite', filename=':memory:', create_db=True)
db.generate_mapping(create_tables=True)
