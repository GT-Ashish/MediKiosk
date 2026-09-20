"""
Document Evidence Domain Models — Clinical Engine.

Represents clinical facts extracted from historical patient documents
and their verification lifecycle during an adaptive history-taking session.

Architecture principle:
    Store broadly, use narrowly.

    A patient's longitudinal record may contain evidence from many
    historical documents.  The current clinical session consumes only
    the subset relevant to the current complaint.  Irrelevant evidence
    is never deleted — it simply isn't selected.

Evidence lifecycle:
    Document (Phase 6)
        ↓  (future extraction layer)
    DocumentEvidence
        ↓  (future relevance selector)
    HistoricalContextCandidate
        ↓  (future verification flow)
    VerificationTarget → patient confirmation → SlotState KNOWN

Hard constraints:
    - Evidence does NOT automatically promote a slot to KNOWN.
    - Evidence does NOT imply diagnosis.
    - Evidence does NOT modify SlotStatus.
    - Medication evidence does NOT infer conditions
      (e.g. metformin ≠ diabetes).
    - Red-flag evaluation does NOT read from evidence directly.

Provenance:
    Every evidence item retains a reference to its source document
    (document_id), the date on the source document (source_date),
    when the extraction was performed (extracted_at), and optionally
    the relevant excerpt from the source text (source_excerpt).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ── Verification status ─────────────────────────────────────────────────────


class EvidenceVerificationStatus(str, Enum):
    """
    Verification state of a document-derived clinical fact.

    UNVERIFIED:
        Information came from a historical source but has not been
        confirmed for current use by the patient.

    PATIENT_CONFIRMED:
        Patient has confirmed that the information is currently
        applicable.

    PATIENT_REJECTED:
        Patient has explicitly stated that the historical information
        is not currently applicable or correct.

    SUPERSEDED:
        A newer verified/current fact has replaced this evidence for
        current-context purposes.  The old evidence is preserved for
        audit/history.
    """

    UNVERIFIED = "unverified"
    PATIENT_CONFIRMED = "patient_confirmed"
    PATIENT_REJECTED = "patient_rejected"
    SUPERSEDED = "superseded"


# ── Duration classification ─────────────────────────────────────────────────


class EvidenceDurationClass(str, Enum):
    """
    Classification of a treatment's temporal course as stated in
    the source document.

    Values are only accepted when explicitly supplied by a future
    extraction layer.  They are NEVER inferred from a medication name.

    SHORT_COURSE:
        The source document indicates a limited/temporary duration
        (e.g. "for 5 days").

    MAINTENANCE:
        The source document indicates an ongoing/long-term treatment
        (e.g. "daily", "long-term").

    UNKNOWN:
        Duration information is not stated or cannot be determined
        from the source document.
    """

    SHORT_COURSE = "short_course"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


# ── Document evidence ───────────────────────────────────────────────────────


class DocumentEvidence(BaseModel):
    """
    A single clinical fact extracted from a historical patient document.

    Represents one piece of structured evidence with full provenance
    back to the source document.  Multiple evidence items may reference
    the same document, and a patient may have evidence from many
    documents over time.

    This model does NOT:
        - Reference or require a SlotState
        - Automatically create or modify any slot
        - Imply or infer a diagnosis
        - Contain OCR or extraction logic
    """

    evidence_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this evidence item.",
    )

    # ── Provenance ───────────────────────────────────────────────────────

    document_id: uuid.UUID = Field(
        ...,
        description=(
            "Reference to the source MedicalDocument (Phase 6). "
            "Preserves the full provenance chain."
        ),
    )
    source_date: datetime | None = Field(
        default=None,
        description=(
            "Date on the source document (e.g. prescription date). "
            "None when the document does not carry an explicit date."
        ),
    )
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this evidence was extracted.",
    )
    source_excerpt: str | None = Field(
        default=None,
        description=(
            "Relevant text excerpt from the source document. "
            "Aids human audit of the extraction. May contain "
            "sensitive data — handle per privacy policy."
        ),
    )

    # ── Clinical content ─────────────────────────────────────────────────

    fact_type: str = Field(
        ...,
        min_length=1,
        description=(
            "Type of clinical fact. Examples: 'medication', 'diagnosis', "
            "'allergy', 'lab_value', 'procedure', 'vital_sign'."
        ),
    )
    value: dict[str, Any] = Field(
        ...,
        description=(
            "Structured value of the extracted fact. Shape depends on "
            "fact_type. For example, a medication might be: "
            '{"name": "Metformin", "dose": "500 mg", "frequency": "BD"}.'
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score (0.0–1.0).",
    )
    duration_class: EvidenceDurationClass | None = Field(
        default=None,
        description=(
            "Temporal classification of a treatment if stated in the "
            "source document. Only accepted when explicitly supplied "
            "by the extraction layer — never inferred from names."
        ),
    )

    # ── Verification ─────────────────────────────────────────────────────

    verification_status: EvidenceVerificationStatus = Field(
        default=EvidenceVerificationStatus.UNVERIFIED,
        description="Current verification state of this evidence.",
    )
    patient_verified_at: datetime | None = Field(
        default=None,
        description=(
            "UTC timestamp when the patient confirmed or rejected "
            "this evidence.  None while UNVERIFIED."
        ),
    )

    # ── Validators ───────────────────────────────────────────────────────

    @model_validator(mode="after")
    def _fact_type_not_blank(self) -> DocumentEvidence:
        """Reject whitespace-only fact_type."""
        if not self.fact_type.strip():
            raise ValueError("fact_type must not be blank.")
        return self


# ── Historical context candidate ────────────────────────────────────────────


class HistoricalContextCandidate(BaseModel):
    """
    An evidence item selected as potentially relevant to the current
    clinical session.

    This is NOT the final clinical state.  It represents:
        "this historical evidence MAY be relevant to this interview."

    The current slot must NOT automatically become KNOWN because
    a context candidate exists.  Patient confirmation is always
    required before evidence can influence slot state.
    """

    candidate_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this candidate selection.",
    )
    evidence_id: uuid.UUID = Field(
        ...,
        description="Reference to the DocumentEvidence item.",
    )
    relevance_reason: str = Field(
        ...,
        min_length=1,
        description=(
            "Why this evidence was selected as potentially relevant. "
            "Set by the future relevance selector."
        ),
    )
    related_slot_id: str | None = Field(
        default=None,
        description=(
            "Template slot ID that this evidence may inform, if known. "
            "None when the relevance is general rather than slot-specific."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance confidence score (0.0–1.0).",
    )
    requires_patient_confirmation: bool = Field(
        default=True,
        description=(
            "Whether this candidate requires explicit patient "
            "confirmation before it can be used. Defaults to True — "
            "historical evidence is never auto-promoted."
        ),
    )


# ── Verification target ─────────────────────────────────────────────────────


class VerificationTargetStatus(str, Enum):
    """Status of a patient-verification target."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class VerificationTarget(BaseModel):
    """
    A patient-confirmation target grouping one or more evidence items
    that should be verified together.

    This allows the future question selector to distinguish:
        - NO INFORMATION (slot is UNKNOWN, no evidence exists)
        - HISTORICAL EVIDENCE EXISTS (evidence present, unverified)
        - PATIENT-CONFIRMED (patient has confirmed the evidence)

    The verification target does NOT generate question text or
    implement verification logic.  It provides the data contract
    that the future selector and verification engine will use.
    """

    target_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this verification target.",
    )
    evidence_ids: list[uuid.UUID] = Field(
        ...,
        min_length=1,
        description=(
            "One or more DocumentEvidence IDs grouped for verification. "
            "Must contain at least one evidence reference."
        ),
    )
    target_type: str = Field(
        ...,
        min_length=1,
        description=(
            "Category of verification. Examples: 'medication_current', "
            "'condition_active', 'allergy_current'."
        ),
    )
    related_slot_id: str | None = Field(
        default=None,
        description="Template slot this verification would inform, if known.",
    )
    status: VerificationTargetStatus = Field(
        default=VerificationTargetStatus.PENDING,
        description="Current status of the verification.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this target was created.",
    )
