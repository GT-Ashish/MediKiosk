"""
Document API Endpoints.

POST /api/v1/sessions/{session_id}/documents — Register document metadata
GET  /api/v1/sessions/{session_id}/documents — List session documents
GET  /api/v1/documents/{document_id}         — Get document details
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_document_service
from app.api.v1.api_schemas import (
    RegisterDocumentRequest,
    DocumentResponse,
    ErrorResponse,
)
from app.services.documents.impl import DocumentServiceImpl
from app.utils.errors import (
    SessionNotFoundError,
    ConsentRequiredError,
    MediKioskValidationError,
)

router = APIRouter()


def _doc_to_response(doc) -> DocumentResponse:
    """Convert a MedicalDocument to a DocumentResponse."""
    return DocumentResponse(
        document_id=doc.document_id,
        session_id=doc.session_id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        uploaded_at=doc.uploaded_at,
        processing_status=doc.processing_status.value,
        file_size_bytes=doc.file_size_bytes,
    )


@router.post(
    "/sessions/{session_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Register document metadata",
)
async def register_document(
    session_id: uuid.UUID,
    body: RegisterDocumentRequest,
    service: DocumentServiceImpl = Depends(get_document_service),
) -> DocumentResponse:
    """Register a newly uploaded document (metadata only in Phase 6)."""
    try:
        doc = await service.register_document(
            session_id=session_id,
            filename=body.filename,
            mime_type=body.mime_type,
            file_size_bytes=body.file_size_bytes,
        )
        return _doc_to_response(doc)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    except ConsentRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required before uploading documents.",
        )
    except MediKioskValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message,
        )


@router.get(
    "/sessions/{session_id}/documents",
    response_model=list[DocumentResponse],
    responses={404: {"model": ErrorResponse}},
    summary="List session documents",
)
async def list_session_documents(
    session_id: uuid.UUID,
    service: DocumentServiceImpl = Depends(get_document_service),
) -> list[DocumentResponse]:
    """Retrieve all document metadata for a session."""
    try:
        docs = await service.get_session_documents(session_id)
        return [_doc_to_response(d) for d in docs]
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get document details",
)
async def get_document(
    document_id: uuid.UUID,
    service: DocumentServiceImpl = Depends(get_document_service),
) -> DocumentResponse:
    """Retrieve a document's metadata by ID."""
    doc = await service.get_document(document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return _doc_to_response(doc)
