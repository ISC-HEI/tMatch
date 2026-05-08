
from sqlalchemy.orm import sessionmaker
from models.role import Role
from seeds.keywords import create_keywords
from seeds.programs import create_programs
from seeds.roles import create_roles

from seeds.engine import engine

Session = sessionmaker(bind=engine)
session = Session()

with session as s:
    if s.query(Role).count() > 0:
        print("Database already seeded. Skipping.")
        exit(0)

create_roles()
print("Created roles")

create_keywords()
print("Created keywords")

create_programs()
print("Created programs")
