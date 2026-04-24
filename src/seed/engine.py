
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost/tmatch_db")
