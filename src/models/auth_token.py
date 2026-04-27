#pyright: reportImportCycles = false

from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
import uuid

if TYPE_CHECKING:
    from models.user import User

class AuthToken(Base):
    __tablename__: str = "auth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="auth_tokens", lazy="joined")
