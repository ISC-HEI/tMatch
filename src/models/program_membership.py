#pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User
    from models.program import Program
    from models.role import Role

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ProgramMembership(Base):
    __tablename__ = "program_memberships"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    user: Mapped[User] = relationship("User", lazy="joined")
    program: Mapped[Program] = relationship("Program", lazy="joined")
    role: Mapped[Role] = relationship("Role", lazy="joined")
