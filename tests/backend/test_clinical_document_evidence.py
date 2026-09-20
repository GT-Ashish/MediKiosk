"""
Tests for Phase 7 document evidence domain models.

Validates:

DOCUMENT EVIDENCE
    1.  valid document evidence
    2.  missing required provenance rejected
    3.  confidence bounds
    4.  verification status defaults correctly
    5.  patient-confirmed evidence represented correctly
    6.  patient-rejected evidence represented correctly
    7.  superseded evidence represented correctly

CONTEXT CANDIDATE
    8.  historical context candidate validates

VERIFICATION TARGET
    9.  verification target validates

MEDICATION REPRESENTATION
    10. medication evidence can represent name/dose/frequency/duration

SEPARATION GUARANTEES
    11. document evidence does NOT require a SlotState
    12. document evidence does NOT automatically create a KNOWN slot
    13. source document provenance is preserved
    14. multiple evidence items can reference the same document
    15. multiple documents can exist for the same patient over time
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.domain.clinical_engine.document_evidence import (
    DocumentEvidence,
    EvidenceDurationClass,
    EvidenceVerificationStatus,
    HistoricalContextCandidate,
    VerificationTarget,
    VerificationTargetStatus,
)
from app.domain.clinical_engine.enums import SlotStatus
from app.domain.clinical_engine.slot_state import SlotState


# ── Shared fixtures ──────────────────────────────────────────────────────────

_DOC_ID = uuid.uuid4()
_DOC_ID_2 = uuid.uuid4()
_SOURCE_DATE = datetime(2026, 3, 15, tzinfo=timezone.utc)


def _valid_evidence(**overrides) -> DocumentEvidence:
    """Build a minimal valid DocumentEvidence for testing."""
    defaults = {
        "document_id": _DOC_ID,
        "fact_type": "medication",
        "value": {"name": "Metformin", "dose": "500 mg"},
        "confidence": 0.92,
        "source_date": _SOURCE_DATE,
        "source_excerpt": "Tab Metformin 500 mg BD",
    }
    defaults.update(overrides)
    return DocumentEvidence(**defaults)


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT EVIDENCE
# ══════════════════════════════════════════════════════════════════════════════


class TestDocumentEvidence:
    """Tests 1–7."""

    def test_valid_evidence(self) -> None:
        """Test 1: A well-formed evidence item is accepted."""
        ev = _valid_evidence()
        assert ev.evidence_id is not None
        assert ev.document_id == _DOC_ID
        assert ev.fact_type == "medication"
        assert ev.value["name"] == "Metformin"
        assert ev.confidence == 0.92
        assert ev.source_date == _SOURCE_DATE
        assert ev.source_excerpt == "Tab Metformin 500 mg BD"

    def test_missing_document_id_rejected(self) -> None:
        """Test 2: document_id is required provenance."""
        with pytest.raises(ValidationError, match="document_id"):
            DocumentEvidence(
                fact_type="medication",
                value={"name": "Aspirin"},
                confidence=0.9,
            )

    def test_missing_fact_type_rejected(self) -> None:
        """Test 2b: fact_type is required."""
        with pytest.raises(ValidationError):
            DocumentEvidence(
                document_id=_DOC_ID,
                value={"name": "Aspirin"},
                confidence=0.9,
            )

    def test_blank_fact_type_rejected(self) -> None:
        """Test 2c: Whitespace-only fact_type is rejected."""
        with pytest.raises(ValidationError):
            DocumentEvidence(
                document_id=_DOC_ID,
                fact_type="   ",
                value={"name": "Aspirin"},
                confidence=0.9,
            )

    def test_missing_value_rejected(self) -> None:
        """Test 2d: value dict is required."""
        with pytest.raises(ValidationError, match="value"):
            DocumentEvidence(
                document_id=_DOC_ID,
                fact_type="medication",
                confidence=0.9,
            )

    def test_missing_confidence_rejected(self) -> None:
        """Test 2e: confidence is required."""
        with pytest.raises(ValidationError, match="confidence"):
            DocumentEvidence(
                document_id=_DOC_ID,
                fact_type="medication",
                value={"name": "Aspirin"},
            )

    def test_confidence_lower_bound(self) -> None:
        """Test 3: confidence must be ≥ 0.0."""
        with pytest.raises(ValidationError, match="confidence"):
            _valid_evidence(confidence=-0.1)

    def test_confidence_upper_bound(self) -> None:
        """Test 3b: confidence must be ≤ 1.0."""
        with pytest.raises(ValidationError, match="confidence"):
            _valid_evidence(confidence=1.1)

    def test_confidence_at_boundaries(self) -> None:
        """Test 3c: confidence at 0.0 and 1.0 are valid."""
        ev_zero = _valid_evidence(confidence=0.0)
        assert ev_zero.confidence == 0.0
        ev_one = _valid_evidence(confidence=1.0)
        assert ev_one.confidence == 1.0

    def test_verification_status_defaults_to_unverified(self) -> None:
        """Test 4: New evidence defaults to UNVERIFIED."""
        ev = _valid_evidence()
        assert ev.verification_status == EvidenceVerificationStatus.UNVERIFIED
        assert ev.patient_verified_at is None

    def test_patient_confirmed_evidence(self) -> None:
        """Test 5: Patient-confirmed evidence is representable."""
        confirmed_at = datetime.now(timezone.utc)
        ev = _valid_evidence(
            verification_status=EvidenceVerificationStatus.PATIENT_CONFIRMED,
            patient_verified_at=confirmed_at,
        )
        assert ev.verification_status == EvidenceVerificationStatus.PATIENT_CONFIRMED
        assert ev.patient_verified_at == confirmed_at

    def test_patient_rejected_evidence(self) -> None:
        """Test 6: Patient-rejected evidence is representable."""
        rejected_at = datetime.now(timezone.utc)
        ev = _valid_evidence(
            verification_status=EvidenceVerificationStatus.PATIENT_REJECTED,
            patient_verified_at=rejected_at,
        )
        assert ev.verification_status == EvidenceVerificationStatus.PATIENT_REJECTED
        assert ev.patient_verified_at == rejected_at

    def test_superseded_evidence(self) -> None:
        """Test 7: Superseded evidence is representable."""
        ev = _valid_evidence(
            verification_status=EvidenceVerificationStatus.SUPERSEDED,
        )
        assert ev.verification_status == EvidenceVerificationStatus.SUPERSEDED


# ══════════════════════════════════════════════════════════════════════════════
# ENUM SMOKE TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestEvidenceEnums:
    """Verify evidence enums have expected members and are string-backed."""

    def test_verification_status_values(self) -> None:
        assert set(EvidenceVerificationStatus) == {
            EvidenceVerificationStatus.UNVERIFIED,
            EvidenceVerificationStatus.PATIENT_CONFIRMED,
            EvidenceVerificationStatus.PATIENT_REJECTED,
            EvidenceVerificationStatus.SUPERSEDED,
        }

    def test_verification_status_str_backed(self) -> None:
        assert EvidenceVerificationStatus.UNVERIFIED == "unverified"
        assert EvidenceVerificationStatus.PATIENT_CONFIRMED == "patient_confirmed"
        assert EvidenceVerificationStatus.PATIENT_REJECTED == "patient_rejected"
        assert EvidenceVerificationStatus.SUPERSEDED == "superseded"

    def test_duration_class_values(self) -> None:
        assert set(EvidenceDurationClass) == {
            EvidenceDurationClass.SHORT_COURSE,
            EvidenceDurationClass.MAINTENANCE,
            EvidenceDurationClass.UNKNOWN,
        }

    def test_duration_class_str_backed(self) -> None:
        assert EvidenceDurationClass.SHORT_COURSE == "short_course"
        assert EvidenceDurationClass.MAINTENANCE == "maintenance"
        assert EvidenceDurationClass.UNKNOWN == "unknown"

    def test_verification_target_status_values(self) -> None:
        assert set(VerificationTargetStatus) == {
            VerificationTargetStatus.PENDING,
            VerificationTargetStatus.CONFIRMED,
            VerificationTargetStatus.REJECTED,
            VerificationTargetStatus.SKIPPED,
        }


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT CANDIDATE
# ══════════════════════════════════════════════════════════════════════════════


class TestHistoricalContextCandidate:
    """Test 8."""

    def test_valid_candidate(self) -> None:
        """Test 8: A well-formed candidate is accepted."""
        ev_id = uuid.uuid4()
        candidate = HistoricalContextCandidate(
            evidence_id=ev_id,
            relevance_reason="Patient has historical medication relevant to chest pain.",
            related_slot_id="current_medications",
            confidence=0.85,
        )
        assert candidate.candidate_id is not None
        assert candidate.evidence_id == ev_id
        assert candidate.related_slot_id == "current_medications"
        assert candidate.confidence == 0.85
        assert candidate.requires_patient_confirmation is True

    def test_candidate_without_slot(self) -> None:
        """Context candidate can have general relevance (no specific slot)."""
        candidate = HistoricalContextCandidate(
            evidence_id=uuid.uuid4(),
            relevance_reason="General medical history relevance.",
            confidence=0.6,
        )
        assert candidate.related_slot_id is None

    def test_candidate_requires_confirmation_default(self) -> None:
        """requires_patient_confirmation defaults to True."""
        candidate = HistoricalContextCandidate(
            evidence_id=uuid.uuid4(),
            relevance_reason="Test.",
            confidence=0.5,
        )
        assert candidate.requires_patient_confirmation is True

    def test_candidate_missing_evidence_id_rejected(self) -> None:
        with pytest.raises(ValidationError, match="evidence_id"):
            HistoricalContextCandidate(
                relevance_reason="Test.",
                confidence=0.5,
            )

    def test_candidate_missing_reason_rejected(self) -> None:
        with pytest.raises(ValidationError, match="relevance_reason"):
            HistoricalContextCandidate(
                evidence_id=uuid.uuid4(),
                confidence=0.5,
            )

    def test_candidate_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            HistoricalContextCandidate(
                evidence_id=uuid.uuid4(),
                relevance_reason="Test.",
                confidence=1.5,
            )


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION TARGET
# ══════════════════════════════════════════════════════════════════════════════


class TestVerificationTarget:
    """Test 9."""

    def test_valid_verification_target(self) -> None:
        """Test 9: A well-formed verification target is accepted."""
        ev_ids = [uuid.uuid4(), uuid.uuid4()]
        target = VerificationTarget(
            evidence_ids=ev_ids,
            target_type="medication_current",
            related_slot_id="current_medications",
        )
        assert target.target_id is not None
        assert target.evidence_ids == ev_ids
        assert target.target_type == "medication_current"
        assert target.related_slot_id == "current_medications"
        assert target.status == VerificationTargetStatus.PENDING
        assert target.created_at is not None

    def test_target_empty_evidence_ids_rejected(self) -> None:
        """evidence_ids must have at least one item."""
        with pytest.raises(ValidationError):
            VerificationTarget(
                evidence_ids=[],
                target_type="medication_current",
            )

    def test_target_missing_type_rejected(self) -> None:
        with pytest.raises(ValidationError, match="target_type"):
            VerificationTarget(
                evidence_ids=[uuid.uuid4()],
            )

    def test_target_status_confirmed(self) -> None:
        target = VerificationTarget(
            evidence_ids=[uuid.uuid4()],
            target_type="condition_active",
            status=VerificationTargetStatus.CONFIRMED,
        )
        assert target.status == VerificationTargetStatus.CONFIRMED

    def test_target_status_rejected(self) -> None:
        target = VerificationTarget(
            evidence_ids=[uuid.uuid4()],
            target_type="condition_active",
            status=VerificationTargetStatus.REJECTED,
        )
        assert target.status == VerificationTargetStatus.REJECTED

    def test_target_status_skipped(self) -> None:
        target = VerificationTarget(
            evidence_ids=[uuid.uuid4()],
            target_type="allergy_current",
            status=VerificationTargetStatus.SKIPPED,
        )
        assert target.status == VerificationTargetStatus.SKIPPED


# ══════════════════════════════════════════════════════════════════════════════
# MEDICATION REPRESENTATION
# ══════════════════════════════════════════════════════════════════════════════


class TestMedicationEvidence:
    """Test 10."""

    def test_medication_with_full_detail(self) -> None:
        """Test 10: Medication evidence can represent name/dose/frequency/duration."""
        ev = _valid_evidence(
            value={
                "name": "Metformin",
                "dose": "500 mg",
                "frequency": "BD",
                "duration": "30",
                "duration_unit": "days",
            },
            duration_class=EvidenceDurationClass.MAINTENANCE,
        )
        assert ev.value["name"] == "Metformin"
        assert ev.value["dose"] == "500 mg"
        assert ev.value["frequency"] == "BD"
        assert ev.value["duration"] == "30"
        assert ev.value["duration_unit"] == "days"
        assert ev.duration_class == EvidenceDurationClass.MAINTENANCE

    def test_medication_with_minimal_detail(self) -> None:
        """Medication with only a name is valid (incomplete extraction)."""
        ev = _valid_evidence(value={"name": "Aspirin"})
        assert ev.value["name"] == "Aspirin"
        assert ev.duration_class is None

    def test_duration_class_short_course(self) -> None:
        ev = _valid_evidence(
            duration_class=EvidenceDurationClass.SHORT_COURSE,
        )
        assert ev.duration_class == EvidenceDurationClass.SHORT_COURSE

    def test_duration_class_unknown(self) -> None:
        ev = _valid_evidence(
            duration_class=EvidenceDurationClass.UNKNOWN,
        )
        assert ev.duration_class == EvidenceDurationClass.UNKNOWN

    def test_non_medication_fact_types(self) -> None:
        """fact_type is flexible — not locked to 'medication'."""
        for fact_type in ["diagnosis", "allergy", "lab_value", "procedure", "vital_sign"]:
            ev = _valid_evidence(
                fact_type=fact_type,
                value={"description": f"test {fact_type}"},
            )
            assert ev.fact_type == fact_type


# ══════════════════════════════════════════════════════════════════════════════
# SEPARATION GUARANTEES
# ══════════════════════════════════════════════════════════════════════════════


class TestSeparationGuarantees:
    """Tests 11–15: Evidence layer is separate from slot state."""

    def test_evidence_does_not_require_slot_state(self) -> None:
        """Test 11: DocumentEvidence has no SlotState reference."""
        ev = _valid_evidence()
        field_names = set(DocumentEvidence.model_fields.keys())
        assert "slot_state" not in field_names
        assert "slot_status" not in field_names
        assert "slot_id" not in field_names
        # Evidence exists independently of any slot
        assert ev.evidence_id is not None

    def test_evidence_does_not_auto_create_known_slot(self) -> None:
        """Test 12: Creating evidence does NOT change any slot's status."""
        slot = SlotState()
        assert slot.status == SlotStatus.UNKNOWN

        # Create evidence — the slot must remain UNKNOWN
        _valid_evidence()
        assert slot.status == SlotStatus.UNKNOWN

        # Even "confirmed" evidence does not touch slots
        _valid_evidence(
            verification_status=EvidenceVerificationStatus.PATIENT_CONFIRMED,
        )
        assert slot.status == SlotStatus.UNKNOWN

    def test_source_provenance_preserved(self) -> None:
        """Test 13: All provenance fields are preserved."""
        source_date = datetime(2025, 6, 1, tzinfo=timezone.utc)
        ev = _valid_evidence(
            source_date=source_date,
            source_excerpt="Rx: Metformin 500 mg BD x 30 days",
        )
        assert ev.document_id == _DOC_ID
        assert ev.source_date == source_date
        assert ev.extracted_at is not None
        assert ev.source_excerpt == "Rx: Metformin 500 mg BD x 30 days"

    def test_multiple_evidence_from_same_document(self) -> None:
        """Test 14: Multiple evidence items can reference the same document."""
        ev1 = _valid_evidence(
            fact_type="medication",
            value={"name": "Metformin"},
        )
        ev2 = _valid_evidence(
            fact_type="medication",
            value={"name": "Atorvastatin"},
        )
        ev3 = _valid_evidence(
            fact_type="diagnosis",
            value={"description": "Type 2 Diabetes Mellitus"},
        )
        # All share the same document_id
        assert ev1.document_id == ev2.document_id == ev3.document_id == _DOC_ID
        # But have distinct evidence IDs
        assert len({ev1.evidence_id, ev2.evidence_id, ev3.evidence_id}) == 3

    def test_multiple_documents_for_patient(self) -> None:
        """Test 15: Multiple documents can exist for the same patient over time."""
        ev_from_doc_1 = _valid_evidence(
            document_id=_DOC_ID,
            source_date=datetime(2025, 1, 15, tzinfo=timezone.utc),
            value={"name": "Metformin"},
        )
        ev_from_doc_2 = _valid_evidence(
            document_id=_DOC_ID_2,
            source_date=datetime(2026, 3, 20, tzinfo=timezone.utc),
            value={"name": "Metformin"},
        )
        # Different documents, different dates
        assert ev_from_doc_1.document_id != ev_from_doc_2.document_id
        assert ev_from_doc_1.source_date != ev_from_doc_2.source_date
        # Both are valid evidence items
        assert ev_from_doc_1.evidence_id != ev_from_doc_2.evidence_id


# ══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Additional structural validation tests."""

    def test_source_date_optional(self) -> None:
        """Documents without a date are valid (source_date is optional)."""
        ev = _valid_evidence(source_date=None)
        assert ev.source_date is None

    def test_source_excerpt_optional(self) -> None:
        """source_excerpt is optional."""
        ev = _valid_evidence(source_excerpt=None)
        assert ev.source_excerpt is None

    def test_extracted_at_auto_populated(self) -> None:
        """extracted_at gets a default UTC timestamp."""
        ev = _valid_evidence()
        assert ev.extracted_at is not None
        assert ev.extracted_at.tzinfo is not None

    def test_evidence_serialization_roundtrip(self) -> None:
        """Evidence can be serialized to dict and back."""
        ev = _valid_evidence(
            duration_class=EvidenceDurationClass.MAINTENANCE,
            verification_status=EvidenceVerificationStatus.PATIENT_CONFIRMED,
            patient_verified_at=datetime.now(timezone.utc),
        )
        data = ev.model_dump(mode="json")
        restored = DocumentEvidence(**data)
        assert restored.evidence_id == ev.evidence_id
        assert restored.fact_type == ev.fact_type
        assert restored.verification_status == EvidenceVerificationStatus.PATIENT_CONFIRMED
        assert restored.duration_class == EvidenceDurationClass.MAINTENANCE

    def test_empty_fact_type_string_rejected(self) -> None:
        """Empty string fact_type is rejected by min_length."""
        with pytest.raises(ValidationError):
            _valid_evidence(fact_type="")

    def test_slot_status_enum_unchanged(self) -> None:
        """SlotStatus still has exactly the original 5 values."""
        assert set(SlotStatus) == {
            SlotStatus.UNKNOWN,
            SlotStatus.KNOWN,
            SlotStatus.NOT_APPLICABLE,
            SlotStatus.DECLINED,
            SlotStatus.UNCLEAR,
        }
