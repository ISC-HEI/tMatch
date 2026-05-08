
from sqlalchemy.orm import sessionmaker

from models.program import Program
from seeds.engine import engine

Session = sessionmaker(bind=engine)

def create_programs():
    programs = [
        "ISC",
        "SYND",
        "LSE",
        "ETE"
    ]

    with Session() as s:
        for i in range(len(programs)):
            new_program = Program(name=programs[i])
            s.add(new_program)

        s.commit()
