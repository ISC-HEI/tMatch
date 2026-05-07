
from collections.abc import Sequence
from threading import Thread

import numpy as np
from models.project_rating import ProjectRating
from models.user import User
from services.db import get_db, Db
from scipy.optimize import linear_sum_assignment

from services.mail import Mailer

def assignment_algorithm(project_ratings: Sequence[ProjectRating], student_ids: list[int], project_ids: list[int]) -> tuple[list[int], list[int]] :
    """Assignment algorithm.

    Creates the matrix, run the hungarian algorithm on a normalized version and returns the assignment matrix.

    Args:
        project_ratings: All project ratings in the program.
        student_ids: All student IDs in the program.
        project_ids: All project IDs in the program.

    Returns:
        The assigment matrix.
    """

    n_students = len(student_ids)
    n_projects = len(project_ids)

    student_index = { user_id: i for i, user_id in enumerate(student_ids) }
    project_index = { project_id: j for j, project_id in enumerate(project_ids) }

    rating_matrix = np.zeros((n_students, n_projects))

    for project_rating in project_ratings:
        i = student_index[project_rating.student_id]
        j = project_index[project_rating.project_id]

        rating_matrix[i][j] = project_rating.value

    mins = rating_matrix.min(axis=1, keepdims=True)
    maxs = rating_matrix.max(axis=1, keepdims=True)
    ranges = maxs - mins

    with np.errstate(invalid="ignore", divide="ignore"):
        normalized_matrix = np.where(
            ranges == 0,
            0.0,
            (rating_matrix - mins) / ranges
        )

    return linear_sum_assignment(-normalized_matrix)

def assign_projects(program_id: int, project_ratings: Sequence[ProjectRating], db: Db, mailer: Mailer):
    """Run the project assignment algorithm.

    This runs as a background task. It assigns projects to students based on their ratings
    using the Hungarian Algorithm to maximize student satisfaction.

    Args:
        program_id: ID of the program to run assignment for.
        project_ratings: All project ratings in the program.
        db: Database instance.
        mailer: Mailer instance.
    """

    student_ids = sorted(set(project_rating.student_id for project_rating in project_ratings))
    project_ids = sorted(set(project_rating.project_id for project_rating in project_ratings))

    row_indexes, col_indexes = assignment_algorithm(project_ratings, student_ids, project_ids)

    for i, j in zip(row_indexes, col_indexes):
        student_id = student_ids[i]
        project_id = project_ids[j]

        db.assign_project(project_id, student_id)

    mailer.project_assignment(program_id)

def remind_students(students: Sequence[User], n_projects: int, mailer: Mailer):
    """Remind students who haven't rated all projects to submit their ratings.

    This runs as a background task.

    Args:
        students: List of all students in the program.
        n_projects: Total number of projects in the program.
        mailer: Mailer instance.
    """

    students_to_remind = []

    for student in students:
        if len(student.project_ratings) != n_projects:
            students_to_remind.append(student)

        mailer.students_reminder(students_to_remind, urgent=True)


def start_assignment(program_id: int):
    """Start the project assignment process for a program.

    If all students have rated all projects, runs the assignment algorithm.
    Otherwise, sends reminders to students who haven't completed their ratings.

    Args:
        program_id: ID of the program.

    Returns:
        True if assignment was started, False if reminders were sent.
    """

    db = get_db()
    mailer = Mailer()

    project_ratings = db.get_ratings(program_id)
    students = db.get_students(program_id)
    projects = db.get_projects(program_id)

    n_students = len(students)
    n_projects = len(projects)

    if len(project_ratings) != n_students * n_projects:
        thread = Thread(target = remind_students, args = (students, n_projects, mailer))
        thread.start()

        return False

    thread = Thread(target = assign_projects, args = (program_id, project_ratings, db, mailer))
    thread.start()

    return True
