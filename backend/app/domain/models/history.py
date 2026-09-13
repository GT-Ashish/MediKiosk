"""
HistoryAnswerModel — ORM Model.

Maps the HistoryAnswer domain concept to the ``history_answers`` table.

Each row is a single Q&A exchange from the kiosk conversation.
The collection of answers for a session/visit is assembled into a
ClinicalHistory by the service layer.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class HistoryAnswerModel(Base):
    """ORM model for clinical history Q&A answers."""

    __tablename__ = "history_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kiosk_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visit_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("visits.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    answer_source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session = relationship("SessionModel", back_populates="history_answers")
    visit = relationship("VisitModel", back_populates="history_answers")

    def __repr__(self) -> str:
        return f"<HistoryAnswerModel(id={self.id}, q={self.question_id})>"
