
from sqlalchemy.orm import sessionmaker
from models.role import Role
from seed.keywords import create_keywords
from seed.programs import create_programs
from seed.roles import create_roles

from seed.engine import engine

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
