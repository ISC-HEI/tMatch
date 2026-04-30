
from collections.abc import Sequence
from threading import Thread

import numpy as np
from models.project_rating import ProjectRating
from services.db import get_db, Db
from scipy.optimize import linear_sum_assignment

def assignment_algorithm(project_ratings: Sequence[ProjectRating], student_ids: list[int], project_ids: list[int], db: Db):
    student_index = { user_id: i for i, user_id in enumerate(student_ids) }
    project_index = { project_id: j for j, project_id in enumerate(project_ids) }
    project_by_id = { project_rating.project_id: project_rating.project for project_rating in project_ratings }

    n_students = len(student_ids)
    n_projects = len(project_ids)

    rating_matrix = np.zeros((n_students, n_projects))

    for project_rating in project_ratings:
        i = student_index[project_rating.student_id]
        j = project_index[project_rating.project_id]

        rating_matrix[i][j] = project_rating.value

    row_indexes, col_indexes = linear_sum_assignment(-rating_matrix)

    for i, j in zip(row_indexes, col_indexes):
        student_id = student_ids[i]
        project_id = project_ids[j]

        project = project_by_id[project_id]

        db.assign_project(project, student_id)




def start_assignment(program_id: int):
    db = get_db()

    project_ratings = db.get_ratings(program_id)

    student_ids = sorted(set(project_rating.student_id for project_rating in project_ratings))
    project_ids = sorted(set(project_rating.project_id for project_rating in project_ratings))

    n_students = len(student_ids)
    n_projects = len(project_ids)

    if len(project_ratings) != n_students * n_projects:
        return False

    thread = Thread(target = assignment_algorithm, args = (project_ratings, student_ids, project_ids, db))
    thread.start()

    return True
