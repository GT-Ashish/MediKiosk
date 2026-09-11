"""
DocumentService — Service Protocol.

Defines the interface for medical document registration and retrieval.

The DocumentService is responsible for:
    - Registering uploaded documents (metadata only — file storage is separate)
    - Retrieving document records for a session
    - Triggering document processing (OCR + extraction — deferred to Phase 7+)

Document pipeline separation:
    The DocumentService handles the METADATA layer of documents.
    The actual OCR + NER processing is done by a separate DocumentProcessor
    (to be defined in infrastructure/integrations/ in Phase 7+).

    This separation means:
        - The DocumentService interface is stable regardless of OCR provider
        - OCR providers can be swapped without touching the API layer
        - Processing is asynchronous and status-tracked via DocumentStatus

File storage note:
    Actual file bytes are not managed by this service.
    File storage (local disk / object storage) is deferred to Phase 7+.
    For Phase 6, documents are metadata-only records.

Implementation note (Phase 6):
    Concrete implementation will be InMemoryDocumentService.
"""

import uuid
from typing import Protocol

from app.domain.schemas.document import MedicalDocument, DocumentExtraction, DocumentStatus


class DocumentService(Protocol):
    """
    Interface for medical document registration and retrieval.
    """

    async def register_document(
        self,
        session_id: uuid.UUID,
        filename: str,
        mime_type: str,
        file_size_bytes: int | None = None,
    ) -> MedicalDocument:
        """
        Register a newly uploaded document.

        Creates a MedicalDocument record with status=PENDING.
        File storage and processing are handled separately.

        Args:
            session_id: The session this document belongs to.
            filename: Original filename from the upload.
            mime_type: MIME type (e.g., 'image/jpeg', 'application/pdf').
            file_size_bytes: Optional file size.

        Returns:
            The registered MedicalDocument (status=PENDING).
        Raises:
            SessionNotFoundError: If the session does not exist.
            ConsentRequiredError: If consent has not been given.
            UnsupportedOperationError: If the session has too many documents.
        """
        ...

    async def get_document(self, document_id: uuid.UUID) -> MedicalDocument | None:
        """
        Retrieve a document record by ID.

        Args:
            document_id: The document to retrieve.

        Returns:
            The MedicalDocument if found, None otherwise.
        """
        ...

    async def get_session_documents(
        self,
        session_id: uuid.UUID,
    ) -> list[MedicalDocument]:
        """
        Retrieve all documents for a session.

        Args:
            session_id: The session to retrieve documents for.

        Returns:
            List of MedicalDocument records (may be empty).
        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        ...

    async def get_document_extraction(
        self,
        document_id: uuid.UUID,
    ) -> DocumentExtraction | None:
        """
        Retrieve the extraction result for a processed document.

        Args:
            document_id: The document to retrieve extraction for.

        Returns:
            DocumentExtraction if processing completed, None if not yet processed.
        """
        ...

    async def update_document_status(
        self,
        document_id: uuid.UUID,
        status: DocumentStatus,
    ) -> MedicalDocument:
        """
        Update the processing status of a document.

        Called by the document processing pipeline (Phase 7+).

        Args:
            document_id: The document to update.
            status: The new DocumentStatus.

        Returns:
            The updated MedicalDocument.
        Raises:
            ValueError: If document_id does not exist.
        """
        ...
