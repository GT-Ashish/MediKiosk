"""
VisitModel — ORM Model.

Maps the Visit domain concept to the ``visits`` table.

A Visit represents a single clinical encounter within a kiosk session.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class VisitModel(Base):
    """ORM model for clinical visits."""

    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kiosk_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chief_complaint: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session = relationship("SessionModel", back_populates="visits")
    history_answers = relationship(
        "HistoryAnswerModel",
        back_populates="visit",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<VisitModel(id={self.id}, complaint={self.chief_complaint[:30]}...)>"
