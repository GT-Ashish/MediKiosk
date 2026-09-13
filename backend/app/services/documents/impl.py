"""
DocumentService — Concrete Implementation.

Implements the DocumentService Protocol using repository pattern.
Phase 6: metadata-only. File storage and OCR deferred to Phase 8.
"""

import uuid

from app.config import get_settings
from app.domain.schemas.document import MedicalDocument, DocumentExtraction, DocumentStatus
from app.infrastructure.repositories.session_repo import SQLAlchemySessionRepository
from app.infrastructure.repositories.document_repo import SQLAlchemyDocumentRepository
from app.utils.errors import (
    SessionNotFoundError,
    ConsentRequiredError,
    MediKioskValidationError,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DocumentServiceImpl:
    """
    Concrete implementation of the DocumentService Protocol.

    Manages document metadata persistence. Actual file storage and OCR
    processing are deferred to Phase 8.
    """

    def __init__(
        self,
        session_repo: SQLAlchemySessionRepository,
        document_repo: SQLAlchemyDocumentRepository,
    ) -> None:
        self._session_repo = session_repo
        self._document_repo = document_repo

    async def register_document(
        self,
        session_id: uuid.UUID,
        filename: str,
        mime_type: str,
        file_size_bytes: int | None = None,
    ) -> MedicalDocument:
        """Register a newly uploaded document (metadata only)."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if not session.consent_given:
            raise ConsentRequiredError(session_id)

        # Check document limit
        count = await self._document_repo.count_by_session(session_id)
        if count >= settings.max_documents_per_session:
            raise MediKioskValidationError(
                f"Maximum documents per session ({settings.max_documents_per_session}) exceeded.",
                field="documents",
            )

        document = await self._document_repo.create(
            session_id=session_id,
            filename=filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
        )
        logger.info("Document registered: %s for session %s", document.document_id, session_id)
        return document

    async def get_document(self, document_id: uuid.UUID) -> MedicalDocument | None:
        """Retrieve a document record by ID."""
        return await self._document_repo.get(document_id)

    async def get_session_documents(
        self,
        session_id: uuid.UUID,
    ) -> list[MedicalDocument]:
        """Retrieve all documents for a session."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return await self._document_repo.get_by_session(session_id)

    async def get_document_extraction(
        self,
        document_id: uuid.UUID,
    ) -> DocumentExtraction | None:
        """
        Retrieve extraction result for a document.

        Returns None — OCR/extraction is deferred to Phase 8.
        """
        return None

    async def update_document_status(
        self,
        document_id: uuid.UUID,
        status: DocumentStatus,
    ) -> MedicalDocument:
        """Update the processing status of a document."""
        updated = await self._document_repo.update_status(document_id, status)
        if updated is None:
            raise MediKioskValidationError(
                f"Document not found: {document_id}",
                field="document_id",
            )
        return updated
