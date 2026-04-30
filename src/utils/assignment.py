
from collections.abc import Sequence
from threading import Thread

import numpy as np
from models.project_rating import ProjectRating
from models.user import User
from services.db import get_db, Db
from scipy.optimize import linear_sum_assignment

from services.mail import Mailer

def assignment_algorithm(program_id: int, project_ratings: Sequence[ProjectRating], db: Db, mailer: Mailer):
    student_ids = sorted(set(project_rating.student_id for project_rating in project_ratings))
    project_ids = sorted(set(project_rating.project_id for project_rating in project_ratings))

    n_students = len(student_ids)
    n_projects = len(project_ids)

    student_index = { user_id: i for i, user_id in enumerate(student_ids) }
    project_index = { project_id: j for j, project_id in enumerate(project_ids) }

    rating_matrix = np.zeros((n_students, n_projects))

    for project_rating in project_ratings:
        i = student_index[project_rating.student_id]
        j = project_index[project_rating.project_id]

        rating_matrix[i][j] = project_rating.value

    row_indexes, col_indexes = linear_sum_assignment(-rating_matrix)

    for i, j in zip(row_indexes, col_indexes):
        student_id = student_ids[i]
        project_id = project_ids[j]

        print(f"{project_id} assigned to {student_id}")

        db.assign_project(project_id, student_id)

    mailer.project_assignment(program_id)

def remind_students(students: Sequence[User], n_projects: int, mailer: Mailer):
    students_to_remind = []

    for student in students:
        if len(student.project_ratings) != n_projects:
            students_to_remind.append(student)

        mailer.students_reminder(students_to_remind, urgent=True)


def start_assignment(program_id: int):
    db = get_db()
    mailer = Mailer()

    project_ratings = db.get_ratings(program_id)
    students = db.get_students(program_id)
    students = [student for student in students if student.ldap_uid == "leny"]
    projects = db.get_projects(program_id)

    n_students = len(students)
    n_projects = len(projects)

    if len(project_ratings) != n_students * n_projects:
        thread = Thread(target = remind_students, args = (students, n_projects, mailer))
        thread.start()

        return False

    thread = Thread(target = assignment_algorithm, args = (program_id, project_ratings, db, mailer))
    thread.start()

    return True
