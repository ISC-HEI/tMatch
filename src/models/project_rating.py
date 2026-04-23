#pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.project import Project

class ProjectRating(Base):
    __tablename__: str = "project_ratings"

    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    value: Mapped[int] = mapped_column(nullable=False)

    student: Mapped[User] = relationship("User", back_populates="project_ratings", lazy="joined")
    project: Mapped[Project] = relationship("Project", back_populates="project_ratings", lazy="joined")
