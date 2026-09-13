"""
PatientIdentifierModel — ORM Model.

Maps the PatientIdentifier domain concept to the ``patient_identifiers`` table.

Privacy note:
    - identifier_hash stores ONLY SHA-256 hashes — never raw Aadhaar/ABHA/mobile.
    - display_name is populated only from consented, non-sensitive sources.
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class PatientIdentifierModel(Base):
    """ORM model for patient identifiers (privacy-preserving references)."""

    __tablename__ = "patient_identifiers"

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
    identifier_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    identifier_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationship
    session = relationship("SessionModel", back_populates="patient_identifier")

    def __repr__(self) -> str:
        return f"<PatientIdentifierModel(id={self.id}, type={self.identifier_type})>"
