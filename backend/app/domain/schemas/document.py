"""
Document Pipeline Schemas — Domain Layer.

Defines the data contracts for the document upload and processing pipeline.

Document Pipeline Architecture (future implementation):
    ┌────────────────┐
    │ Image / PDF    │   Uploaded by patient at the kiosk
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │ OCR Engine     │   Replaceable provider (Tesseract / Google Vision / Azure)
    │                │   Interface: infrastructure/integrations/ocr.py (future)
    └───────┬────────┘
            │  raw_text
    ┌───────▼────────┐
    │ Entity Extract │   Medical NER: extracts MEDICATION, DIAGNOSIS, DATE, etc.
    │ (LLM-assisted) │   Output: list[MedicalEntity]
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │ DocumentExtra  │   Structured extraction result stored against document_id
    │ -ction         │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │ Timeline +     │   Cross-document synthesis — deferred to Phase 7+
    │ Summary        │
    └────────────────┘

None of the pipeline stages above are implemented in this phase.
This file defines the DATA CONTRACTS only so that:
    - The API layer knows what shapes to expect/return
    - The service layer has typed return types
    - OCR provider can be swapped without changing API contracts
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """
    Processing status of an uploaded document.

    PENDING    — Document registered, awaiting processing
    PROCESSING — OCR/extraction in progress
    COMPLETED  — Processing finished, DocumentExtraction available
    FAILED     — Processing encountered an unrecoverable error
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MedicalDocument(BaseModel):
    """
    A medical document uploaded by the patient during a kiosk session.

    Represents the raw upload record. The actual file content is handled
    by the infrastructure layer (file storage — deferred to Phase 7+).
    Only metadata is stored in this schema.
    """

    document_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this document.",
    )
    session_id: uuid.UUID = Field(
        description="The session this document belongs to.",
    )
    filename: str = Field(
        description="Original filename as uploaded by the patient.",
    )
    mime_type: str = Field(
        description="MIME type of the uploaded file (e.g., 'image/jpeg', 'application/pdf').",
    )
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the document was uploaded.",
    )
    processing_status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        description="Current processing status of this document.",
    )
    file_size_bytes: int | None = Field(
        default=None,
        description="Size of the uploaded file in bytes.",
    )


class MedicalEntity(BaseModel):
    """
    A single clinical entity extracted from a document.

    Produced by the medical NER step of the document pipeline.
    Entity types follow a simplified NER taxonomy suitable for
    the SIH 2026 prototype (not yet SNOMED/ICD-11 aligned).
    """

    entity_type: str = Field(
        description=(
            "Type of clinical entity. Examples: "
            "'MEDICATION', 'DIAGNOSIS', 'PROCEDURE', 'DATE', "
            "'LAB_VALUE', 'ALLERGY', 'VITAL_SIGN'."
        ),
    )
    text: str = Field(
        description="The raw extracted text span from the document.",
    )
    normalized_value: str | None = Field(
        default=None,
        description=(
            "Normalized or standardised form of the entity. "
            "For example, 'Paracetamol 500mg' might normalize to 'Paracetamol'. "
            "FHIR/SNOMED normalization is deferred to Phase 8+."
        ),
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Extraction confidence score (0.0–1.0).",
    )
    page_number: int | None = Field(
        default=None,
        description="Page number in the source document (1-indexed). None for single-page images.",
    )


class DocumentExtraction(BaseModel):
    """
    The result of processing a MedicalDocument through the OCR + NER pipeline.

    Created by the document processing service when a document has been
    fully processed. Referenced by document_id.

    AI/Privacy note:
        raw_text may contain sensitive patient information.
        It must not be logged, must not be returned to the frontend verbatim,
        and must only be used for the structured extraction step.
    """

    document_id: uuid.UUID = Field(
        description="The document this extraction belongs to.",
    )
    raw_text: str | None = Field(
        default=None,
        description=(
            "Raw text extracted by OCR. "
            "Contains sensitive patient data — never log this field."
        ),
    )
    extracted_entities: list[MedicalEntity] = Field(
        default_factory=list,
        description="Structured medical entities extracted from the raw text.",
    )
    processing_notes: str | None = Field(
        default=None,
        description="Non-sensitive notes about the processing (e.g., 'low image quality', 'handwritten text detected').",
    )
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when processing completed.",
    )
