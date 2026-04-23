from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import streamlit as st
from streamlit.connections import SQLConnection

from models.auth_token import AuthToken
from models.base import Base
from models.program import Program
from models.program_membership import ProgramMembership
from models.project import Project
from models.role import Role
from models.session import Session
from models.user import User
from models.project_rating import ProjectRating


class Db:
    _conn: SQLConnection

    def __init__(self) -> None:
        self._conn = st.connection("tmatch_db", type="sql")

    def create_project(self, created_by: int, teacher_id: int, title: str, description: str, specifications: str) -> Project | None:
        with self._conn.session as s:
            project = Project(
                created_by=created_by,
                teacher_id=teacher_id,
                title=title,
                description=description,
                specifications=specifications,
            )

            try:
                s.add(project)
                s.commit()

            except IntegrityError:
                return None

            s.refresh(project)

            return project

    def create_session(self, user_id: int, program_id: int) -> Session:
        with self._conn.session as s:
            session = Session(
                user_id=user_id,
                program_id=program_id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )

            s.add(session)
            s.commit()
            s.refresh(session)

            return session

    def create_auth_token(self, user_id: int, program_id: int) -> AuthToken:
        with self._conn.session as s:
            auth_token = AuthToken(
                user_id=user_id,
                program_id=program_id,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
            )

            s.add(auth_token)
            s.commit()
            s.refresh(auth_token)

            return auth_token

    def apply_rating(self, project_id: int, user_id: int, rating: int) -> ProjectRating:
        with self._conn.session as s:
            existing = s.execute(
                select(ProjectRating)
                .where(ProjectRating.student_id == user_id)
                .where(ProjectRating.project_id == project_id)
            ).scalar_one_or_none()

            if existing:
                existing.value = rating

                s.commit()
                s.refresh(existing)

                return existing

            else:
                project_rating = ProjectRating(
                    project_id=project_id, student_id=user_id, value=rating
                )

                s.add(project_rating)
                s.commit()
                s.refresh(project_rating)

                return project_rating

    def get_rating(self, project_id: int, user_id: int) ->  ProjectRating|None:
        with self._conn.session as s:
            return s.execute(select(ProjectRating)
                             .where(ProjectRating.student_id == user_id)
                             .where(ProjectRating.project_id == project_id)
                             ).scalar_one_or_none()

    def get_projects(self) -> Sequence[Project]:
        with self._conn.session as s:
            return s.execute(select(Project)).unique().scalars().all()

    def get_teachers(self) -> Sequence[User]:
        with self._conn.session as s:
            return (
                s.execute(
                    select(User)
                    .join(ProgramMembership, ProgramMembership.user_id == User.id)
                    .join(Role, Role.id == ProgramMembership.role_id)
                    .where(Role.name == "teacher")
                    .distinct()
                )
                .scalars()
                .all()
            )

    def get_programs(self) -> Sequence[Program]:
        with self._conn.session as s:
            return s.execute(select(Program)).scalars().all()

    def get_user(self, uid: str) -> User:
        with self._conn.session as s:
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

    def get_session(self, sid: str) -> Session | None:
        with self._conn.session as s:
            return s.execute(
                select(Session).where(Session.id == sid)
            ).scalar_one_or_none()

    def get_auth_token(self, token_id: str) -> AuthToken | None:
        with self._conn.session as s:
            return s.execute(
                select(AuthToken).where(AuthToken.id == token_id)
            ).scalar_one_or_none()

    def get_program(self, program_id: int) -> Program | None:
        with self._conn.session as s:
            return s.execute(
                select(Program).where(Program.id == program_id)
            ).scalar_one_or_none()

    def remove(self, model: Base) -> None:
        with self._conn.session as s:
            s.delete(model)
            s.commit()


@st.cache_resource
def get_db() -> Db:
    return Db()
