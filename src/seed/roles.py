from sqlalchemy.orm import sessionmaker

from models.role import Role
from seed.engine import engine

Session = sessionmaker(bind=engine)

def create_roles():
    with Session() as s:
        student = Role(name="student")
        teacher = Role(name="teacher")
        secretary = Role(name="secretary")
        program_director = Role(name="program director")

        s.add(student)
        s.add(teacher)
        s.add(secretary)
        s.add(program_director)

        s.commit()
