from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import streamlit as st

from config import DATABASE_URL
from models.auth_token import AuthToken
from models.base import Base
from models.program import Program
from models.program_membership import ProgramMembership
from models.project import Project
from models.role import Role
from models.session import Session
from models.user import User
from models.project_rating import ProjectRating
from sqlalchemy import delete
from models.keyword import Keyword
from models.projects_keyword import ProjectsKeyword

@st.cache_resource
def get_session_factory():
    engine = create_engine(DATABASE_URL)
    return sessionmaker(bind=engine)

class Db:
    """Database service class for CRUD operations."""

    def __init__(self) -> None:
        self._session_factory = get_session_factory()

    def create_project(self, created_by: int, teacher_id: int, title: str, description: str, specifications: str, program_id: int) -> Project | None:
        """Create a new project in the database.

        Args:
            created_by: ID of the user who created the project.
            teacher_id: ID of the user supervising the project.
            title: Title of the project.
            description: Description of the project.
            specifications: Technical specifications of the project.
            program_id: ID of the program the project belongs to.

        Returns:
            The created Project object, or None if a database integrity error occurs.
        """

        with self._session_factory() as s:
            project = Project(
                created_by=created_by,
                teacher_id=teacher_id,
                title=title,
                description=description,
                specifications=specifications,
                program_id=program_id
            )

            try:
                s.add(project)
                s.commit()

            except IntegrityError:
                return None

            s.refresh(project)

            return project

    def create_session(self, user_id: int) -> Session:
        """Create a new session for a user.

        Args:
            user_id: ID of the user to create the session for.

        Returns:
            The created Session object.
        """

        with self._session_factory() as s:
            session = Session(
                user_id=user_id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )

            s.add(session)
            s.commit()
            s.refresh(session)

            return session

    def create_auth_token(self, user_id: int) -> AuthToken:
        """Create a new authentication token for a user.

        Args:
            user_id: ID of the user to create the token for.

        Returns:
            The created AuthToken object.
        """

        with self._session_factory() as s:
            auth_token = AuthToken(
                user_id=user_id,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
            )

            s.add(auth_token)
            s.commit()
            s.refresh(auth_token)

            return auth_token

    def apply_rating(self, project_id: int, student_id: int, rating: int) -> ProjectRating:
        """Apply or update a rating for a project by a student.

        If a rating already exists for this student/project pair, it updates the value.
        Otherwise, it creates a new rating.

        Args:
            project_id: ID of the project being rated.
            student_id: ID of the student applying the rating.
            rating: Rating value (0 to N, where N is the number of projects in the program).

        Returns:
            The created or updated ProjectRating object.
        """

        with self._session_factory() as s:
            existing = s.execute(
                select(ProjectRating)
                .where(ProjectRating.student_id == student_id)
                .where(ProjectRating.project_id == project_id)
            ).scalar_one_or_none()

            if existing:
                existing.value = rating

                s.commit()
                s.refresh(existing)

                return existing

            else:
                project_rating = ProjectRating(
                    project_id=project_id, student_id=student_id, value=rating
                )

                s.add(project_rating)
                s.commit()
                s.refresh(project_rating)

                return project_rating

    def assign_project(self, project_id: int, student_id: int) -> None:
        """Assign a project to a student.

        Args:
            project_id: ID of the project to assign.
            student_id: ID of the student to assign the project to.
        """

        with self._session_factory() as s:
            project = s.execute(
                select(Project).where(Project.id == project_id)
            ).scalar_one()

            project.student_id = student_id
            s.commit()

            return None
        

    def get_rating(self, project_id: int, student_id: int) -> ProjectRating|None:
        """Get a specific rating for a project by a student.

        Args:
            project_id: ID of the project.
            student_id: ID of the student who rated the project.

        Returns:
            The ProjectRating object, or None if not found.
        """

        with self._session_factory() as s:
            return s.execute(select(ProjectRating)
                .where(ProjectRating.student_id == student_id)
                .where(ProjectRating.project_id == project_id)
            ).scalar_one_or_none()

    def get_ratings(self, program_id: int) -> Sequence[ProjectRating]:
        """Get all ratings for projects in a program.

        Args:
            program_id: ID of the program.

        Returns:
            Sequence of all ProjectRating objects for the program.
        """

        with self._session_factory() as s:
            return (
                s.execute(
                    select(ProjectRating)
                    .join(Project, Project.id == ProjectRating.project_id)
                    .where(Project.program_id == program_id)
                )
                .scalars()
                .all()
            )

    def get_projects(self, program_id: int) -> Sequence[Project]:
        """Get all projects in a program.

        Args:
            program_id: ID of the program.

        Returns:
            Sequence of all Project objects for the program.
        """

        with self._session_factory() as s:
            return (
                s.execute(
                    select(Project)
                    .where(Project.program_id == program_id)
                )
                .scalars()
                .all()
            )


    def get_teachers(self, program_id: int) -> Sequence[User]:
        """Get all teachers in a program.

        Args:
            program_id: ID of the program.

        Returns:
            Sequence of all User objects with teacher role in the program.
        """

        with self._session_factory() as s:
            return (
                s.execute(
                    select(User)
                    .join(ProgramMembership, ProgramMembership.user_id == User.id)
                    .join(Role, Role.id == ProgramMembership.role_id)
                    .join(Program, Program.id == ProgramMembership.program_id)
                    .where(Role.name == "teacher")
                    .where(Program.id == program_id)
                    .distinct()
                )
                .scalars()
                .all()
            )

    def get_students(self, program_id: int) -> Sequence[User]:
        """Get all students in a program.

        Args:
            program_id: ID of the program.

        Returns:
            Sequence of all User objects with student role in the program.
        """

        with self._session_factory() as s:
            return (
                s.execute(
                    select(User)
                    .join(ProgramMembership, ProgramMembership.user_id == User.id)
                    .join(Role, Role.id == ProgramMembership.role_id)
                    .join(Program, Program.id == ProgramMembership.program_id)
                    .where(Role.name == "student")
                    .where(Program.id == program_id)
                    .distinct()
                )
                .scalars()
                .all()
            )

    def get_keywords(self) -> Sequence[Keyword]:
        """Get all keywords.

        Returns:
            Sequence of all Keyword objects.
        """

        with self._session_factory() as s:
            return s.execute(select(Keyword)).scalars().all()

    def update_project_keywords(self, project_id: int, keyword_ids: list[int]) -> None:
        """Replace all keywords for a project with new ones.

        Args:
            project_id: ID of the project.
            keyword_ids: List of keyword IDs to associate with the project.
        """

        with self._session_factory() as s:
            s.execute(
                delete(ProjectsKeyword)
                .where(ProjectsKeyword.project_id == project_id)
            )
            for kid in keyword_ids:
                s.add(ProjectsKeyword(project_id=project_id, keyword_id=kid))
            s.commit()

    def get_users(self) -> Sequence[User]:
        """Get all users with their roles.

        Returns:
            Sequence of all User objects.
        """

        with self._session_factory() as s:
            return (
                s.execute(
                    select(User)
                    .join(ProgramMembership, ProgramMembership.user_id == User.id)
                    .join(Role, Role.id == ProgramMembership.role_id)
                    .distinct()
                    )
                .scalars()
                .all()
            )

    def get_programs(self) -> Sequence[Program]:
        """Get all programs.

        Returns:
            Sequence of all Program objects.
        """

        with self._session_factory() as s:
            return s.execute(select(Program)).scalars().all()

    def get_roles(self) -> Sequence[Role]:
        """Get all roles.

        Returns:
            Sequence of all Role objects.
        """

        with self._session_factory() as s:
            return s.execute(select(Role)).scalars().all()

    def update_user_role(self, user_id: int, program_id: int, role_name: str) -> None:
        """Update a user's role in a program.

        Args:
            user_id: ID of the user.
            program_id: ID of the program.
            role_name: Name of the role to assign.
        """

        with self._session_factory() as s:
            role = s.execute(
                select(Role).where(Role.name == role_name)
            ).scalar_one_or_none()

            if role is None:
                return

            membership = s.execute(
                select(ProgramMembership)
                .where(ProgramMembership.user_id == user_id)
                .where(ProgramMembership.program_id == program_id)
            ).scalar_one_or_none()

            if membership:
                membership.role_id = role.id
                s.commit()

    def get_user(self, uid: str) -> User:
        """Get a user by LDAP UID, creating if not found.

        Args:
            uid: The LDAP UID of the user.

        Returns:
            The User object (existing or newly created).
        """

        with self._session_factory() as s:
            user = s.execute(
                select(User).where(User.ldap_uid == uid)
            ).scalar_one_or_none()

            if user is not None:
                return user

            user = User(ldap_uid=uid)
            s.add(user)
            s.commit()
            s.refresh(user)

            return user

    def get_project(self, project_id: int) -> Project|None:
        """Get a project by ID.

        Args:
            project_id: ID of the project.

        Returns:
            The Project object, or None if not found.
        """

        with self._session_factory() as s:
            return s.execute(
                select(Project).where(Project.id == project_id)
            ).scalar_one_or_none()

    def get_session(self, sid: str) -> Session | None:
        """Get a session by ID.

        Args:
            sid: The session ID (UUID string).

        Returns:
            The Session object, or None if not found.
        """

        with self._session_factory() as s:
            return s.execute(
                select(Session).where(Session.id == sid)
            ).scalar_one_or_none()

    def get_auth_token(self, token_id: str) -> AuthToken | None:
        """Get an auth token by ID.

        Args:
            token_id: The token ID (UUID string).

        Returns:
            The AuthToken object, or None if not found.
        """

        with self._session_factory() as s:
            return s.execute(
                select(AuthToken).where(AuthToken.id == token_id)
            ).scalar_one_or_none()

    def get_program(self, program_id: int) -> Program | None:
        """Get a program by ID.

        Args:
            program_id: ID of the program.

        Returns:
            The Program object, or None if not found.
        """

        with self._session_factory() as s:
            return s.execute(
                select(Program).where(Program.id == program_id)
            ).scalar_one_or_none()

    def update_project(self, project_id: int, title: str, description: str, teacher_id: int) -> Project | None:
        """Update a project's details.

        Args:
            project_id: ID of the project to update.
            title: New title for the project.
            description: New description for the project.
            teacher_id: ID of the new teacher supervising the project.

        Returns:
            The updated Project object, or None if not found or on integrity error.
        """

        with self._session_factory() as s:
            project = s.execute(
                select(Project).where(Project.id == project_id)
            ).scalar_one_or_none()
            if project is None:
                return None
            project.title = title
            project.description = description
            project.teacher_id = teacher_id
            try:
                s.commit()
                s.refresh(project)
                return project
            except IntegrityError:
                s.rollback()
                return None

    def remove(self, model: Base) -> None:
        """Delete a model instance from the database.

        Args:
            model: The model instance to delete.

        Note:
            Cascade behavior depends on the model configuration.
        """

        with self._session_factory() as s:
            s.delete(model)
            s.commit()


@st.cache_resource
def get_db() -> Db:
    """Get the singleton database instance.

    Returns:
        The Db instance.
    """

    return Db()
