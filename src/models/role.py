
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.program_membership import ProgramMembership

class Role(Base):
    __tablename__: str = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    program_memberships: Mapped[list[ProgramMembership]] = relationship("ProgramMembership", back_populates="role", lazy="selectin")
