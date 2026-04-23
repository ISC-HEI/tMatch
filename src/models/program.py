# pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.program_membership import ProgramMembership

class Program(Base):
    __tablename__: str = "programs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    program_memberships: Mapped[list[ProgramMembership]] = relationship("ProgramMembership", back_populates="program", lazy="selectin")
