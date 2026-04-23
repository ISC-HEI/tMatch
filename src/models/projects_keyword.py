
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.project import Project
    from models.keyword import Keyword

class ProjectsKeyword(Base):
    __tablename__: str = "projects_keywords"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"), primary_key=True)

    project: Mapped[Project] = relationship("Project", back_populates="projects_keywords", lazy="joined")
    keyword: Mapped[Keyword] = relationship("Keyword", back_populates="projects_keywords", lazy="joined")
