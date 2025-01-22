import fastapi

from models.base import db
from web import index

app = fastapi.FastAPI()

app.include_router(index.router)

# db.bind(provider='sqlite', filename='pengiloo.db', create_db=True)
db.bind(provider='sqlite', filename=':memory:', create_db=True)
db.generate_mapping(create_tables=True)
