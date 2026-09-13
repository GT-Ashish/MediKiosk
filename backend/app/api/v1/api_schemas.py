"""
API Request/Response Schemas.

These are API-layer models — separate from the domain schemas.
They define what the API accepts and returns, without exposing
internal domain details unnecessarily.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.schemas.patient import IdentifierType
from app.domain.schemas.history import AnswerSource


# ── Error Response ────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    detail: str | None = None


# ── Session ───────────────────────────────────────────────────────────────────

class PatientIdentifierRequest(BaseModel):
    """Patient identifier in API requests."""
    identifier_type: IdentifierType
    identifier_hash: str | None = None
    display_name: str | None = None


class CreateSessionRequest(BaseModel):
    """Request body for POST /api/v1/sessions."""
    language: str = Field(default="en", description="BCP-47 language code.")
    patient_identifier: PatientIdentifierRequest | None = None


class SessionResponse(BaseModel):
    """Response for session endpoints."""
    session_id: uuid.UUID
    created_at: datetime
    language: str
    status: str
    consent_given: bool
    patient_identifier: PatientIdentifierRequest | None = None


# ── Consent ───────────────────────────────────────────────────────────────────

class ConsentRequest(BaseModel):
    """Request body for POST /api/v1/sessions/{session_id}/consent."""
    data_use_acknowledged: bool = Field(
        description="Patient acknowledges data use policy."
    )
    ai_processing_acknowledged: bool = Field(
        description="Patient acknowledges AI processing."
    )


# ── Visit ─────────────────────────────────────────────────────────────────────

class CreateVisitRequest(BaseModel):
    """Request body for POST /api/v1/sessions/{session_id}/visits."""
    chief_complaint: str = Field(
        description="The patient's primary reason for visiting."
    )
    department: str | None = Field(
        default=None,
        description="Optional target department."
    )


class VisitResponse(BaseModel):
    """Response for visit endpoints."""
    visit_id: uuid.UUID
    session_id: uuid.UUID
    chief_complaint: str
    department: str | None = None


# ── History ───────────────────────────────────────────────────────────────────

class RecordAnswerRequest(BaseModel):
    """Request body for POST /api/v1/visits/{visit_id}/answers."""
    session_id: uuid.UUID = Field(
        description="The session this answer belongs to."
    )
    question_id: str = Field(
        description="Identifier for the clinical question."
    )
    question_text: str = Field(
        description="The question text presented to the patient."
    )
    answer_text: str = Field(
        description="The patient's answer."
    )
    answer_source: AnswerSource = Field(
        description="How the answer was captured."
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0–1.0)."
    )


class HistoryAnswerResponse(BaseModel):
    """Response for a single recorded answer."""
    question_id: str
    question_text: str
    answer_text: str
    answer_source: str
    confidence: float | None = None
    answered_at: datetime


# ── Document ──────────────────────────────────────────────────────────────────

class RegisterDocumentRequest(BaseModel):
    """Request body for POST /api/v1/sessions/{session_id}/documents."""
    filename: str = Field(description="Original filename.")
    mime_type: str = Field(description="MIME type (e.g., 'image/jpeg').")
    file_size_bytes: int | None = Field(
        default=None,
        description="File size in bytes."
    )


class DocumentResponse(BaseModel):
    """Response for document endpoints."""
    document_id: uuid.UUID
    session_id: uuid.UUID
    filename: str
    mime_type: str
    uploaded_at: datetime
    processing_status: str
    file_size_bytes: int | None = None
