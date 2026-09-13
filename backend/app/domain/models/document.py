"""
DocumentModel — ORM Model.

Maps the MedicalDocument domain concept to the ``medical_documents`` table.

Phase 6: metadata-only persistence.
Phase 8: actual file storage + OCR + extraction will be added.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class DocumentModel(Base):
    """ORM model for medical document metadata."""

    __tablename__ = "medical_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kiosk_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processing_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # Relationship
    session = relationship("SessionModel", back_populates="documents")

    def __repr__(self) -> str:
        return f"<DocumentModel(id={self.id}, filename={self.filename})>"
