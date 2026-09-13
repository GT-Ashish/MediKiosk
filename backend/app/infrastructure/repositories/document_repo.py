"""
SQLAlchemy Document Repository.

Handles persistence of MedicalDocument domain objects (metadata only in Phase 6).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.document import DocumentModel
from app.domain.schemas.document import MedicalDocument, DocumentStatus


class SQLAlchemyDocumentRepository:
    """Repository for MedicalDocument persistence using SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        session_id: uuid.UUID,
        filename: str,
        mime_type: str,
        file_size_bytes: int | None = None,
    ) -> MedicalDocument:
        """Create a new document metadata record."""
        model = DocumentModel(
            session_id=session_id,
            filename=filename,
            mime_type=mime_type,
            processing_status=DocumentStatus.PENDING.value,
            file_size_bytes=file_size_bytes,
        )
        self._db.add(model)
        await self._db.flush()
        return self._to_domain(model)

    async def get(self, document_id: uuid.UUID) -> MedicalDocument | None:
        """Retrieve a document by ID."""
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_session(self, session_id: uuid.UUID) -> list[MedicalDocument]:
        """Retrieve all documents for a session."""
        stmt = (
            select(DocumentModel)
            .where(DocumentModel.session_id == session_id)
            .order_by(DocumentModel.uploaded_at)
        )
        result = await self._db.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def update_status(
        self, document_id: uuid.UUID, status: DocumentStatus
    ) -> MedicalDocument | None:
        """Update the processing status of a document."""
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.processing_status = status.value
        await self._db.flush()
        return self._to_domain(model)

    async def count_by_session(self, session_id: uuid.UUID) -> int:
        """Count documents for a session (for limit enforcement)."""
        stmt = select(DocumentModel).where(DocumentModel.session_id == session_id)
        result = await self._db.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    def _to_domain(model: DocumentModel) -> MedicalDocument:
        """Map a DocumentModel to a MedicalDocument domain schema."""
        return MedicalDocument(
            document_id=model.id,
            session_id=model.session_id,
            filename=model.filename,
            mime_type=model.mime_type,
            uploaded_at=model.uploaded_at,
            processing_status=DocumentStatus(model.processing_status),
            file_size_bytes=model.file_size_bytes,
        )
