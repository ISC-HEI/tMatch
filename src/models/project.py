#pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.project_rating import ProjectRating
    from models.projects_keyword import ProjectsKeyword

class Project(Base):
    __tablename__: str = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    specifications: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    creator: Mapped[User] = relationship("User", foreign_keys=[created_by], back_populates="created_projects", lazy="joined")
    teacher: Mapped[User] = relationship("User", foreign_keys=[teacher_id], back_populates="supervised_projects", lazy="joined")
    project_ratings: Mapped[list[ProjectRating]] = relationship("ProjectRating", back_populates="project", lazy="selectin")
    projects_keywords: Mapped[list[ProjectsKeyword]] = relationship("ProjectsKeyword", back_populates="project", lazy="selectin")
    student: Mapped[User] = relationship("User", foreign_keys=[student_id], back_populates="project", lazy="joined")

    def get_rating_from(self, student_id: int) -> ProjectRating|None:
        for rating in self.project_ratings:
            if rating.student_id == student_id:
                return rating
