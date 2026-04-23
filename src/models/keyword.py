# pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.projects_keyword import ProjectsKeyword

class Keyword(Base):
    __tablename__: str = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    projects_keywords: Mapped[list[ProjectsKeyword]] = relationship("ProjectsKeyword", back_populates="keyword", lazy="selectin")
