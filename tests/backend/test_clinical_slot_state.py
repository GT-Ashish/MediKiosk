"""
Tests for Phase 7 clinical slot state machine.

Validates:
    1.  Default SlotState is UNKNOWN
    2.  UNKNOWN → KNOWN
    3.  UNKNOWN → NOT_APPLICABLE
    4.  UNKNOWN → DECLINED
    5.  UNKNOWN → UNCLEAR
    6.  UNCLEAR → KNOWN
    7.  UNCLEAR → DECLINED
    8.  UNCLEAR retry limit (max 1)
    9.  KNOWN → KNOWN (answer revision)
    10. Invalid transition raises InvalidSlotTransitionError
    11. KNOWN → KNOWN does not require a revision-history collection
"""

from datetime import datetime, timezone

import pytest

from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    SlotStatus,
    SlotType,
    RedFlagSeverity,
    RedFlagAction,
)
from app.domain.clinical_engine.slot_state import SlotState
from app.utils.errors import (
    ClinicalEngineError,
    InvalidSlotTransitionError,
)


# ── Enum smoke tests ──────────────────────────────────────────────────────────

class TestClinicalEnums:
    """All clinical engine enums have expected members."""

    def test_clinical_session_status_values(self) -> None:
        assert set(ClinicalSessionStatus) == {
            ClinicalSessionStatus.IN_PROGRESS,
            ClinicalSessionStatus.PAUSED,
            ClinicalSessionStatus.COMPLETED,
            ClinicalSessionStatus.ABANDONED,
            ClinicalSessionStatus.ESCALATED,
        }

    def test_slot_status_values(self) -> None:
        assert set(SlotStatus) == {
            SlotStatus.UNKNOWN,
            SlotStatus.KNOWN,
            SlotStatus.NOT_APPLICABLE,
            SlotStatus.DECLINED,
            SlotStatus.UNCLEAR,
        }

    def test_slot_type_values(self) -> None:
        assert set(SlotType) == {
            SlotType.TEXT,
            SlotType.BOOLEAN,
            SlotType.INTEGER,
            SlotType.DECIMAL,
            SlotType.ENUM,
            SlotType.DATE,
            SlotType.DURATION,
        }

    def test_red_flag_severity_values(self) -> None:
        assert set(RedFlagSeverity) == {
            RedFlagSeverity.CRITICAL,
            RedFlagSeverity.HIGH,
        }

    def test_red_flag_action_values(self) -> None:
        assert set(RedFlagAction) == {
            RedFlagAction.URGENT_CLINICIAN_REVIEW,
            RedFlagAction.PROMPT_CLINICIAN_REVIEW,
        }

    def test_enums_are_str_backed(self) -> None:
        """All enums serialize to their string value for JSON compat."""
        assert ClinicalSessionStatus.IN_PROGRESS == "in_progress"
        assert SlotStatus.UNKNOWN == "unknown"
        assert SlotType.TEXT == "text"
        assert RedFlagSeverity.CRITICAL == "critical"
        assert RedFlagAction.URGENT_CLINICIAN_REVIEW == "urgent_clinician_review"


# ── Error hierarchy tests ─────────────────────────────────────────────────────

class TestClinicalErrors:
    """Phase 7 errors fit the existing hierarchy."""

    def test_clinical_engine_error_inherits_medikiosk_error(self) -> None:
        from app.utils.errors import MediKioskError
        err = ClinicalEngineError("test")
        assert isinstance(err, MediKioskError)

    def test_invalid_slot_transition_error_inherits_clinical_engine_error(self) -> None:
        err = InvalidSlotTransitionError(
            current_status=SlotStatus.DECLINED,
            target_status=SlotStatus.KNOWN,
        )
        assert isinstance(err, ClinicalEngineError)
        assert err.current_status == SlotStatus.DECLINED
        assert err.target_status == SlotStatus.KNOWN


# ── SlotState default ─────────────────────────────────────────────────────────

class TestSlotStateDefault:
    """Test 1: A freshly created SlotState starts as UNKNOWN."""

    def test_default_status_is_unknown(self) -> None:
        slot = SlotState()
        assert slot.status == SlotStatus.UNKNOWN

    def test_default_retry_count_is_zero(self) -> None:
        slot = SlotState()
        assert slot.retry_count == 0

    def test_default_value_is_none(self) -> None:
        slot = SlotState()
        assert slot.value is None
        assert slot.confidence is None
        assert slot.source is None
        assert slot.raw_patient_text is None
        assert slot.asked_at is None


# ── Valid transitions from UNKNOWN ────────────────────────────────────────────

class TestTransitionsFromUnknown:
    """Tests 2–5: All valid exits from UNKNOWN."""

    def test_unknown_to_known(self) -> None:
        """Test 2."""
        slot = SlotState()
        slot.transition_to(
            SlotStatus.KNOWN,
            value="chest",
            source="voice",
            raw_patient_text="my chest hurts",
        )
        assert slot.status == SlotStatus.KNOWN
        assert slot.value == "chest"
        assert slot.source == "voice"
        assert slot.raw_patient_text == "my chest hurts"

    def test_unknown_to_not_applicable(self) -> None:
        """Test 3."""
        slot = SlotState()
        slot.transition_to(SlotStatus.NOT_APPLICABLE, source="system")
        assert slot.status == SlotStatus.NOT_APPLICABLE

    def test_unknown_to_declined(self) -> None:
        """Test 4."""
        slot = SlotState()
        slot.transition_to(SlotStatus.DECLINED, source="voice")
        assert slot.status == SlotStatus.DECLINED

    def test_unknown_to_unclear(self) -> None:
        """Test 5."""
        slot = SlotState()
        now = datetime.now(tz=timezone.utc)
        slot.transition_to(
            SlotStatus.UNCLEAR,
            raw_patient_text="hmm I'm not sure",
            asked_at=now,
        )
        assert slot.status == SlotStatus.UNCLEAR
        assert slot.retry_count == 1
        assert slot.asked_at == now


# ── Valid transitions from UNCLEAR ────────────────────────────────────────────

class TestTransitionsFromUnclear:
    """Tests 6–8: Exits from UNCLEAR including retry limit."""

    def _make_unclear_slot(self) -> SlotState:
        slot = SlotState()
        slot.transition_to(SlotStatus.UNCLEAR, raw_patient_text="um")
        return slot

    def test_unclear_to_known(self) -> None:
        """Test 6."""
        slot = self._make_unclear_slot()
        slot.transition_to(SlotStatus.KNOWN, value="3 days", source="voice")
        assert slot.status == SlotStatus.KNOWN
        assert slot.value == "3 days"

    def test_unclear_to_declined(self) -> None:
        """Test 7."""
        slot = self._make_unclear_slot()
        slot.transition_to(SlotStatus.DECLINED, source="voice")
        assert slot.status == SlotStatus.DECLINED

    def test_unclear_retry_limit_exceeded(self) -> None:
        """Test 8: Second UNCLEAR transition must raise because max retries = 1."""
        slot = self._make_unclear_slot()
        assert slot.retry_count == 1  # already used the one retry

        with pytest.raises(InvalidSlotTransitionError) as exc_info:
            slot.transition_to(SlotStatus.UNCLEAR, raw_patient_text="still unsure")

        assert "retry limit" in str(exc_info.value.detail).lower()


# ── Answer revision (KNOWN → KNOWN) ──────────────────────────────────────────

class TestKnownToKnownRevision:
    """Tests 9 & 11: Revising an already-known answer."""

    def test_known_to_known_updates_value(self) -> None:
        """Test 9: KNOWN → KNOWN replaces the active value."""
        slot = SlotState()
        slot.transition_to(SlotStatus.KNOWN, value="2 days", source="voice")
        assert slot.value == "2 days"

        slot.transition_to(SlotStatus.KNOWN, value="3 days", source="text")
        assert slot.status == SlotStatus.KNOWN
        assert slot.value == "3 days"
        assert slot.source == "text"

    def test_known_to_known_no_history_collection(self) -> None:
        """
        Test 11: SlotState must NOT contain a revision-history collection.

        KNOWN → KNOWN simply overwrites the active value.
        Historical answers will be stored in ClinicalSessionState.question_history.
        """
        slot = SlotState()
        slot.transition_to(SlotStatus.KNOWN, value="original")
        slot.transition_to(SlotStatus.KNOWN, value="revised")

        # Verify no history-related attribute exists on SlotState
        assert not hasattr(slot, "history")
        assert not hasattr(slot, "revision_history")
        assert not hasattr(slot, "previous_values")

        # Model fields should not include history either
        field_names = set(SlotState.model_fields.keys())
        assert "history" not in field_names
        assert "revision_history" not in field_names
        assert "previous_values" not in field_names


# ── Invalid transitions ──────────────────────────────────────────────────────

class TestInvalidTransitions:
    """Test 10: Disallowed state jumps raise InvalidSlotTransitionError."""

    @pytest.mark.parametrize(
        "from_status,to_status",
        [
            (SlotStatus.DECLINED, SlotStatus.KNOWN),
            (SlotStatus.DECLINED, SlotStatus.UNKNOWN),
            (SlotStatus.NOT_APPLICABLE, SlotStatus.KNOWN),
            (SlotStatus.NOT_APPLICABLE, SlotStatus.UNKNOWN),
            (SlotStatus.NOT_APPLICABLE, SlotStatus.UNCLEAR),
            (SlotStatus.DECLINED, SlotStatus.UNCLEAR),
            (SlotStatus.KNOWN, SlotStatus.UNKNOWN),
            (SlotStatus.KNOWN, SlotStatus.DECLINED),
            (SlotStatus.KNOWN, SlotStatus.NOT_APPLICABLE),
            (SlotStatus.KNOWN, SlotStatus.UNCLEAR),
            (SlotStatus.UNKNOWN, SlotStatus.UNKNOWN),
        ],
        ids=[
            "DECLINED→KNOWN",
            "DECLINED→UNKNOWN",
            "N/A→KNOWN",
            "N/A→UNKNOWN",
            "N/A→UNCLEAR",
            "DECLINED→UNCLEAR",
            "KNOWN→UNKNOWN",
            "KNOWN→DECLINED",
            "KNOWN→N/A",
            "KNOWN→UNCLEAR",
            "UNKNOWN→UNKNOWN",
        ],
    )
    def test_invalid_transition_raises(
        self,
        from_status: SlotStatus,
        to_status: SlotStatus,
    ) -> None:
        slot = SlotState()

        # Drive the slot into the required starting state
        if from_status == SlotStatus.KNOWN:
            slot.transition_to(SlotStatus.KNOWN, value="setup")
        elif from_status == SlotStatus.DECLINED:
            slot.transition_to(SlotStatus.DECLINED)
        elif from_status == SlotStatus.NOT_APPLICABLE:
            slot.transition_to(SlotStatus.NOT_APPLICABLE)
        elif from_status == SlotStatus.UNCLEAR:
            slot.transition_to(SlotStatus.UNCLEAR)
        # UNKNOWN is the default — no setup needed

        with pytest.raises(InvalidSlotTransitionError):
            slot.transition_to(to_status, value="should fail")
