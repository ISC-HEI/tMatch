
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.session import Session
    from models.program_membership import ProgramMembership
    from models.project import Project
    from models.project_rating import ProjectRating
    from models.auth_token import AuthToken
    from models.role import Role

class User(Base):
    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ldap_uid: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    sessions: Mapped[list[Session]] = relationship("Session", back_populates="user")
    auth_tokens: Mapped[list[AuthToken]] = relationship("AuthToken", back_populates="user")

    program_memberships: Mapped[list[ProgramMembership]] = relationship("ProgramMembership", back_populates="user", lazy="selectin")
    created_projects: Mapped[list[Project]] = relationship("Project", foreign_keys="Project.created_by", back_populates="creator", lazy="selectin")
    supervised_projects: Mapped[list[Project]] = relationship("Project", foreign_keys="Project.teacher_id", back_populates="teacher", lazy="selectin")
    project_ratings: Mapped[list[ProjectRating]] = relationship("ProjectRating", back_populates="student", lazy="selectin")
    project: Mapped[Project|None] = relationship("Project", foreign_keys="Project.student_id", back_populates="student", lazy="joined")

    def get_roles(self, program_id: int) -> list[Role]:
        roles = []

        for membership in self.program_memberships:
            if membership.program_id == program_id:
                roles.append(membership.role)

        return roles
