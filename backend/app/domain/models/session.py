"""
SessionModel — ORM Model.

Maps the KioskSession domain concept to the ``kiosk_sessions`` database table.

This is a persistence model only — it is NOT used in the API or service layers.
Repositories handle mapping between SessionModel and the Pydantic KioskSession schema.
"""

import uuid

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base
from app.domain.models.base import TimestampMixin


class SessionModel(TimestampMixin, Base):
    """ORM model for kiosk sessions."""

    __tablename__ = "kiosk_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )
    consent_given: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    patient_identifier = relationship(
        "PatientIdentifierModel",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    consent = relationship(
        "ConsentModel",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    visits = relationship(
        "VisitModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    history_answers = relationship(
        "HistoryAnswerModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    documents = relationship(
        "DocumentModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SessionModel(id={self.id}, status={self.status})>"
