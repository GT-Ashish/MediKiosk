"""
Tests for MediKiosk domain schemas.

Validates that:
    - All domain schemas import cleanly
    - Pydantic validation rules are enforced
    - Safety-critical invariants are upheld (is_ai_generated, requires_physician_review)
    - Enums have expected values
    - Default values are correct
"""

import uuid

import pytest

from app.domain.schemas import (
    KioskSession,
    SessionStatus,
    PatientIdentifier,
    IdentifierType,
    Consent,
    Visit,
    ClinicalHistory,
    HistoryAnswer,
    AnswerSource,
    MedicalDocument,
    DocumentExtraction,
    MedicalEntity,
    DocumentStatus,
    StructuredHistorySummary,
    ReviewStatus,
    DoctorReview,
)


# ── Import smoke test ──────────────────────────────────────────────────────────

class TestSchemaImports:
    """All domain schemas must be importable without error."""

    def test_all_schemas_importable(self) -> None:
        """Verify the top-level import works cleanly for all schema types."""
        schemas = [
            KioskSession, SessionStatus,
            PatientIdentifier, IdentifierType,
            Consent, Visit,
            ClinicalHistory, HistoryAnswer, AnswerSource,
            MedicalDocument, DocumentExtraction, MedicalEntity, DocumentStatus,
            StructuredHistorySummary, ReviewStatus,
            DoctorReview,
        ]
        assert all(s is not None for s in schemas)


# ── KioskSession ──────────────────────────────────────────────────────────────

class TestKioskSession:
    def test_default_session_is_active(self) -> None:
        session = KioskSession()
        assert session.status == SessionStatus.ACTIVE

    def test_default_consent_is_false(self) -> None:
        session = KioskSession()
        assert session.consent_given is False

    def test_session_id_is_uuid(self) -> None:
        session = KioskSession()
        assert isinstance(session.session_id, uuid.UUID)

    def test_default_language_is_english(self) -> None:
        session = KioskSession()
        assert session.language == "en"

    def test_session_status_enum_values(self) -> None:
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.ABANDONED == "abandoned"

    def test_patient_identifier_defaults_to_none(self) -> None:
        session = KioskSession()
        assert session.patient_identifier is None


# ── PatientIdentifier ─────────────────────────────────────────────────────────

class TestPatientIdentifier:
    def test_anonymous_identifier_no_hash(self) -> None:
        patient = PatientIdentifier(identifier_type=IdentifierType.ANONYMOUS)
        assert patient.identifier_hash is None
        assert patient.display_name is None

    def test_abha_id_type(self) -> None:
        patient = PatientIdentifier(
            identifier_type=IdentifierType.ABHA_ID,
            identifier_hash="a" * 64,  # SHA-256 hex string
        )
        assert patient.identifier_type == IdentifierType.ABHA_ID
        assert len(patient.identifier_hash) == 64

    def test_identifier_type_enum_values(self) -> None:
        assert IdentifierType.ABHA_ID == "abha_id"
        assert IdentifierType.MOBILE == "mobile"
        assert IdentifierType.HOSPITAL_ID == "hospital_id"
        assert IdentifierType.ANONYMOUS == "anonymous"


# ── Consent ───────────────────────────────────────────────────────────────────

class TestConsent:
    def test_consent_requires_session_id(self) -> None:
        session_id = uuid.uuid4()
        consent = Consent(
            session_id=session_id,
            data_use_acknowledged=True,
            ai_processing_acknowledged=True,
        )
        assert consent.session_id == session_id
        assert consent.data_use_acknowledged is True
        assert consent.ai_processing_acknowledged is True

    def test_consent_default_version(self) -> None:
        consent = Consent(
            session_id=uuid.uuid4(),
            data_use_acknowledged=True,
            ai_processing_acknowledged=True,
        )
        assert consent.consent_version == "1.0"


# ── ClinicalHistory ───────────────────────────────────────────────────────────

class TestClinicalHistory:
    def test_severity_valid_range(self) -> None:
        history = ClinicalHistory(
            session_id=uuid.uuid4(),
            chief_complaint="chest pain",
            severity=7,
        )
        assert history.severity == 7

    def test_severity_below_minimum_raises(self) -> None:
        with pytest.raises(Exception):
            ClinicalHistory(
                session_id=uuid.uuid4(),
                chief_complaint="chest pain",
                severity=0,
            )

    def test_severity_above_maximum_raises(self) -> None:
        with pytest.raises(Exception):
            ClinicalHistory(
                session_id=uuid.uuid4(),
                chief_complaint="chest pain",
                severity=11,
            )

    def test_severity_none_is_valid(self) -> None:
        history = ClinicalHistory(
            session_id=uuid.uuid4(),
            chief_complaint="headache",
            severity=None,
        )
        assert history.severity is None

    def test_default_lists_are_empty(self) -> None:
        history = ClinicalHistory(
            session_id=uuid.uuid4(),
            chief_complaint="fatigue",
        )
        assert history.associated_symptoms == []
        assert history.medications == []
        assert history.allergies == []
        assert history.red_flags == []
        assert history.answers == []


# ── HistoryAnswer ─────────────────────────────────────────────────────────────

class TestHistoryAnswer:
    def test_voice_answer(self) -> None:
        answer = HistoryAnswer(
            question_id="onset",
            question_text="When did the pain start?",
            answer_text="Yesterday morning",
            answer_source=AnswerSource.VOICE,
            confidence=0.92,
        )
        assert answer.answer_source == AnswerSource.VOICE
        assert answer.confidence == 0.92

    def test_confidence_must_be_0_to_1(self) -> None:
        with pytest.raises(Exception):
            HistoryAnswer(
                question_id="severity",
                question_text="How severe?",
                answer_text="very bad",
                answer_source=AnswerSource.TEXT,
                confidence=1.5,  # invalid — above 1.0
            )

    def test_answer_source_enum_values(self) -> None:
        assert AnswerSource.VOICE == "voice"
        assert AnswerSource.TEXT == "text"
        assert AnswerSource.DOCUMENT == "document"


# ── MedicalDocument ───────────────────────────────────────────────────────────

class TestMedicalDocument:
    def test_default_status_is_pending(self) -> None:
        doc = MedicalDocument(
            session_id=uuid.uuid4(),
            filename="report.pdf",
            mime_type="application/pdf",
        )
        assert doc.processing_status == DocumentStatus.PENDING

    def test_document_status_enum_values(self) -> None:
        assert DocumentStatus.PENDING == "pending"
        assert DocumentStatus.PROCESSING == "processing"
        assert DocumentStatus.COMPLETED == "completed"
        assert DocumentStatus.FAILED == "failed"


# ── StructuredHistorySummary — Safety Invariants ──────────────────────────────

class TestStructuredHistorySummary:
    """
    These tests enforce the most critical safety requirement in MediKiosk:
    AI-generated summaries MUST always be marked as requiring physician review.
    """

    def test_is_ai_generated_always_true(self) -> None:
        summary = StructuredHistorySummary(
            session_id=uuid.uuid4(),
            chief_complaint="chest pain",
            history_narrative="Patient reports chest pain...",
        )
        assert summary.is_ai_generated is True

    def test_requires_physician_review_always_true(self) -> None:
        summary = StructuredHistorySummary(
            session_id=uuid.uuid4(),
            chief_complaint="headache",
            history_narrative="Patient reports headache...",
        )
        assert summary.requires_physician_review is True

    def test_cannot_set_is_ai_generated_to_false(self) -> None:
        """is_ai_generated is frozen — attempting to set it to False must fail."""
        with pytest.raises(Exception):
            StructuredHistorySummary(
                session_id=uuid.uuid4(),
                chief_complaint="fatigue",
                history_narrative="Patient reports fatigue...",
                is_ai_generated=False,
            )

    def test_cannot_set_requires_physician_review_to_false(self) -> None:
        """requires_physician_review is frozen — attempting to set False must fail."""
        with pytest.raises(Exception):
            StructuredHistorySummary(
                session_id=uuid.uuid4(),
                chief_complaint="fatigue",
                history_narrative="Patient reports fatigue...",
                requires_physician_review=False,
            )

    def test_default_review_status_is_draft(self) -> None:
        summary = StructuredHistorySummary(
            session_id=uuid.uuid4(),
            chief_complaint="nausea",
            history_narrative="Patient reports nausea...",
        )
        assert summary.review_status == ReviewStatus.DRAFT

    def test_review_status_enum_values(self) -> None:
        assert ReviewStatus.DRAFT == "draft"
        assert ReviewStatus.UNDER_REVIEW == "under_review"
        assert ReviewStatus.REVIEWED == "reviewed"
        assert ReviewStatus.REJECTED == "rejected"


# ── DoctorReview ──────────────────────────────────────────────────────────────

class TestDoctorReview:
    def test_reviewed_status(self) -> None:
        review = DoctorReview(
            summary_id=uuid.uuid4(),
            reviewer_id="doctor-001",
            status=ReviewStatus.REVIEWED,
        )
        assert review.status == ReviewStatus.REVIEWED
        assert review.corrections == {}
        assert review.notes is None

    def test_review_with_corrections(self) -> None:
        review = DoctorReview(
            summary_id=uuid.uuid4(),
            reviewer_id="doctor-001",
            status=ReviewStatus.REVIEWED,
            corrections={"chief_complaint": "Acute chest pain (physician correction)"},
        )
        assert "chief_complaint" in review.corrections
