"""
ConsentModel — ORM Model.

Maps the Consent domain concept to the ``consents`` table.

One consent record per session — consent is mandatory before any clinical
data collection.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ConsentModel(Base):
    """ORM model for patient consent records."""

    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kiosk_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    consented_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    consent_version: Mapped[str] = mapped_column(
        String(10),
        default="1.0",
        nullable=False,
    )
    data_use_acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    ai_processing_acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # Relationship
    session = relationship("SessionModel", back_populates="consent")

    def __repr__(self) -> str:
        return f"<ConsentModel(id={self.id}, session_id={self.session_id})>"
