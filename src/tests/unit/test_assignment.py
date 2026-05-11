from unittest.mock import patch, MagicMock
import pytest
import numpy as np
from utils.assignment import (
    assignment_algorithm,
    assign_projects,
    start_assignment,
)


@pytest.fixture(autouse=True)
def mock_logger():
    with patch("utils.assignment.logger") as mock:
        yield mock


class TestAssignmentAlgorithm:
    """Tests for the assignment_algorithm function."""

    def test_returns_correct_shape_multiple_students_and_projects(self):
        """Returns correct row and column indices for multiple students and projects."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=5),
            MagicMock(student_id=1, project_id=2, value=3),
            MagicMock(student_id=2, project_id=1, value=4),
            MagicMock(student_id=2, project_id=2, value=2),
        ]
        student_ids = [1, 2]
        project_ids = [1, 2]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == len(student_ids)
        assert len(col_idx) == len(project_ids)
        assert set(row_idx) == {0, 1}
        assert set(col_idx) == {0, 1}

    def test_single_student_single_project(self):
        """Handles edge case of single student and single project."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=5),
        ]
        student_ids = [1]
        project_ids = [1]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == 1
        assert len(col_idx) == 1
        assert row_idx[0] == 0
        assert col_idx[0] == 0

    def test_more_projects_than_students(self):
        """Handles case with more projects than students."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=5),
            MagicMock(student_id=1, project_id=2, value=3),
            MagicMock(student_id=1, project_id=3, value=1),
        ]
        student_ids = [1]
        project_ids = [1, 2, 3]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == 1
        assert len(col_idx) == 1

    def test_all_same_ratings_handles_ties(self):
        """Handles ties where all ratings are the same without division error."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=3),
            MagicMock(student_id=1, project_id=2, value=3),
            MagicMock(student_id=2, project_id=1, value=3),
            MagicMock(student_id=2, project_id=2, value=3),
        ]
        student_ids = [1, 2]
        project_ids = [1, 2]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == 2
        assert len(col_idx) == 2
        assert set(row_idx) == {0, 1}
        assert set(col_idx) == {0, 1}

    def test_all_different_ratings(self):
        """Handles full range of rating values."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=1),
            MagicMock(student_id=1, project_id=2, value=2),
            MagicMock(student_id=1, project_id=3, value=3),
        ]
        student_ids = [1]
        project_ids = [1, 2, 3]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == 1
        assert len(col_idx) == 1

    def test_max_rating_only(self):
        """Handles case where student gives max rating to all projects."""
        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=5),
            MagicMock(student_id=1, project_id=2, value=5),
        ]
        student_ids = [1]
        project_ids = [1, 2]

        row_idx, col_idx = assignment_algorithm(project_ratings, student_ids, project_ids)

        assert len(row_idx) == 1


class TestAssignProjects:
    """Tests for the assign_projects function."""

    @patch("utils.assignment.assignment_algorithm")
    @patch("utils.assignment.Mailer")
    def test_sorts_ids_before_assignment(self, mock_mailer_cls, mock_algo):
        """Uses sorted student and project IDs for assignment."""
        mock_db = MagicMock()
        mock_mailer = MagicMock()
        mock_mailer_cls.return_value = mock_mailer

        mock_algo.return_value = (np.array([0, 1]), np.array([0, 1]))

        project_ratings = [
            MagicMock(student_id=3, project_id=2, value=5),
            MagicMock(student_id=1, project_id=1, value=3),
        ]

        assign_projects(1, project_ratings, mock_db, mock_mailer)

        mock_algo.assert_called_once()
        args = mock_algo.call_args[0]
        assert args[1] == [1, 3]
        assert args[2] == [1, 2]

    @patch("utils.assignment.assignment_algorithm")
    @patch("utils.assignment.Mailer")
    def test_calls_mailer_after_assignment(self, mock_mailer_cls, mock_algo):
        """Sends email notification after assignment completes."""
        mock_db = MagicMock()
        mock_mailer = MagicMock()
        mock_mailer_cls.return_value = mock_mailer

        mock_algo.return_value = (np.array([0]), np.array([0]))

        project_ratings = [
            MagicMock(student_id=1, project_id=1, value=5),
        ]

        assign_projects(1, project_ratings, mock_db, mock_mailer)

        mock_mailer.project_assignment.assert_called_once_with(1)

    @patch("utils.assignment.assignment_algorithm")
    @patch("utils.assignment.Mailer")
    def test_empty_ratings_no_assignments(self, mock_mailer_cls, mock_algo):
        """Does not call db.assign_project when no ratings exist."""
        mock_db = MagicMock()
        mock_mailer = MagicMock()
        mock_mailer_cls.return_value = mock_mailer

        mock_algo.return_value = (np.array([]), np.array([]))

        assign_projects(1, [], mock_db, mock_mailer)

        mock_db.assign_project.assert_not_called()


class TestStartAssignment:
    """Tests for the start_assignment function."""

    @patch("utils.assignment.get_db")
    @patch("utils.assignment.remind_students")
    @patch("utils.assignment.Mailer")
    def test_returns_false_when_ratings_incomplete(self, mock_mailer_cls, mock_remind, mock_get_db):
        """Returns False when not all students have rated all projects."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_db.get_ratings.return_value = []
        mock_db.get_students.return_value = [MagicMock()]
        mock_db.get_projects.return_value = [MagicMock(), MagicMock()]

        result = start_assignment(1)

        assert result is False
        mock_remind.assert_called_once()

    @patch("utils.assignment.get_db")
    @patch("utils.assignment.assign_projects")
    @patch("utils.assignment.Mailer")
    def test_returns_true_when_ratings_complete(self, mock_mailer_cls, mock_assign, mock_get_db):
        """Returns True when all students have rated all projects."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_student = MagicMock()
        mock_student.ldap_uid = "testuser"

        mock_db.get_ratings.return_value = [
            MagicMock(student_id=1, project_id=1, value=5),
            MagicMock(student_id=1, project_id=2, value=3),
        ]
        mock_db.get_students.return_value = [mock_student]
        mock_db.get_projects.return_value = [MagicMock(), MagicMock()]

        result = start_assignment(1)

        assert result is True
        mock_assign.assert_called_once()

    @patch("utils.assignment.get_db")
    @patch("utils.assignment.assign_projects")
    @patch("utils.assignment.Mailer")
    def test_starts_background_thread_when_ratings_complete(self, mock_mailer_cls, mock_assign, mock_get_db):
        """Starts background thread for assignment on completion."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_student = MagicMock()
        mock_student.ldap_uid = "testuser"

        mock_db.get_ratings.return_value = [
            MagicMock(student_id=1, project_id=1, value=5),
        ]
        mock_db.get_students.return_value = [mock_student]
        mock_db.get_projects.return_value = [MagicMock()]

        result = start_assignment(1)

        assert result is True
