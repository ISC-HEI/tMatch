from sqlalchemy.orm import sessionmaker

from models.role import Role
from seed.engine import engine

Session = sessionmaker(bind=engine)
session = Session()

def create_roles():
    student = Role(name="student")
    teacher = Role(name="teacher")
    secretary = Role(name="secretary")
    program_director = Role(name="program director")

    session.add(student)
    session.add(teacher)
    session.add(secretary)
    session.add(program_director)

    session.commit()
