"""
Tests for Phase 7 deterministic question selector.

Step 2A test suite — validates:

SESSION GUARD
    1.  non-IN_PROGRESS returns NONE
ASK_NEW
    2.  UNKNOWN slot produces ASK_NEW
    3.  retryable UNCLEAR produces ASK_NEW
    4.  exhausted UNCLEAR is not an ASK_NEW candidate
ORDERING
    5.  required normal slot beats optional normal slot
    6.  lower priority wins within the same required/optional class
DETERMINISM
    7.  repeated calls are deterministic
    8.  selector does not mutate state
VERIFY_HISTORY
    9.  eligible unverified evidence + PENDING target → VERIFY_HISTORY
    10. CONFIRMED target is ignored
    11. REJECTED target is ignored
    12. SKIPPED target is ignored
SEPARATION
    13. document evidence does NOT automatically make SlotState KNOWN
    14. no medication-name question is generated
EDGE CASES
    15. empty candidate set returns NONE (all slots filled)
    16. known related slot prevents VERIFY_HISTORY
    17. NOT_APPLICABLE related slot prevents VERIFY_HISTORY
    18. DECLINED related slot prevents VERIFY_HISTORY
MIXED ORDERING
    19. required ASK_NEW beats optional VERIFY_HISTORY
    20. required VERIFY_HISTORY beats optional ASK_NEW
    21. lower priority wins between multiple verification targets
    22. stable slot_id tie-break produces deterministic selection
    23. stable verification_target_id tie-break for same-slot targets
SAME-SLOT COLLISION
    24. UNKNOWN + same-slot PENDING target → VERIFY_HISTORY
    25. retryable UNCLEAR + same-slot PENDING target → VERIFY_HISTORY
    26. exhausted UNCLEAR + eligible PENDING target → VERIFY_HISTORY
ORPHANED TARGETS
    27. orphaned related_slot_id is ignored
    28. valid candidate is still selected when another is orphaned
RESULT MODEL
    29. SelectionResult has exactly action/slot_id/verification_target_id
    30. SelectionResult is immutable after creation
"""

from __future__ import annotations

import copy
import uuid

import pytest
from pydantic import ValidationError

from app.domain.clinical_engine.document_evidence import (
    HistoricalContextCandidate,
    VerificationTarget,
    VerificationTargetStatus,
)
from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    SlotStatus,
    SlotType,
)
from app.domain.clinical_engine.question_selector import (
    SelectionAction,
    SelectionResult,
    select_next_action,
)
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.template_schema import SlotDefinition


# ── Helpers ──────────────────────────────────────────────────────────────────


def _slot_def(
    slot_id: str,
    *,
    required: bool = False,
    priority: int = 50,
) -> SlotDefinition:
    return SlotDefinition(
        id=slot_id,
        type=SlotType.TEXT,
        required=required,
        priority=priority,
    )


def _make_candidate_and_target(
    slot_id: str,
    *,
    target_status: VerificationTargetStatus = VerificationTargetStatus.PENDING,
    requires_confirmation: bool = True,
    target_id: uuid.UUID | None = None,
) -> tuple[HistoricalContextCandidate, VerificationTarget]:
    """Create a paired candidate + target for a given slot."""
    ev_id = uuid.uuid4()
    tid = target_id or uuid.uuid4()
    candidate = HistoricalContextCandidate(
        evidence_id=ev_id,
        relevance_reason="Test relevance.",
        related_slot_id=slot_id,
        confidence=0.8,
        requires_patient_confirmation=requires_confirmation,
    )
    target = VerificationTarget(
        target_id=tid,
        evidence_ids=[ev_id],
        target_type="medication_current",
        related_slot_id=slot_id,
        status=target_status,
    )
    return candidate, target


def _in_progress_state(**slot_overrides: SlotState) -> ClinicalSessionState:
    """Build an IN_PROGRESS session with given slots."""
    return ClinicalSessionState(
        session_status=ClinicalSessionStatus.IN_PROGRESS,
        slots=slot_overrides,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SESSION GUARD
# ══════════════════════════════════════════════════════════════════════════════


class TestSessionGuard:
    """Test 1."""

    @pytest.mark.parametrize(
        "status",
        [
            ClinicalSessionStatus.PAUSED,
            ClinicalSessionStatus.COMPLETED,
            ClinicalSessionStatus.ABANDONED,
            ClinicalSessionStatus.ESCALATED,
        ],
        ids=["PAUSED", "COMPLETED", "ABANDONED", "ESCALATED"],
    )
    def test_non_in_progress_returns_none(
        self, status: ClinicalSessionStatus,
    ) -> None:
        """Test 1: Any non-IN_PROGRESS session returns NONE."""
        state = ClinicalSessionState(session_status=status)
        result = select_next_action(
            state,
            slot_definitions=[_slot_def("onset", required=True, priority=1)],
        )
        assert result.action == SelectionAction.NONE
        assert result.slot_id is None
        assert result.verification_target_id is None


# ══════════════════════════════════════════════════════════════════════════════
# ASK_NEW
# ══════════════════════════════════════════════════════════════════════════════


class TestAskNew:
    """Tests 2–4."""

    def test_unknown_slot_produces_ask_new(self) -> None:
        """Test 2."""
        state = _in_progress_state()
        result = select_next_action(
            state,
            slot_definitions=[_slot_def("onset", required=True, priority=1)],
        )
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "onset"
        assert result.verification_target_id is None

    def test_retryable_unclear_produces_ask_new(self) -> None:
        """Test 3: UNCLEAR with retry_count=0 is retryable."""
        slot = SlotState(status=SlotStatus.UNCLEAR, retry_count=0)
        state = _in_progress_state(onset=slot)
        result = select_next_action(
            state,
            slot_definitions=[_slot_def("onset", required=True, priority=1)],
        )
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "onset"

    def test_exhausted_unclear_not_ask_candidate(self) -> None:
        """Test 4: UNCLEAR with retry_count≥1 is not selectable for ASK_NEW."""
        slot = SlotState(status=SlotStatus.UNCLEAR, retry_count=1)
        state = _in_progress_state(onset=slot)
        result = select_next_action(
            state,
            slot_definitions=[_slot_def("onset", required=True, priority=1)],
        )
        assert result.action == SelectionAction.NONE


# ══════════════════════════════════════════════════════════════════════════════
# ORDERING
# ══════════════════════════════════════════════════════════════════════════════


class TestOrdering:
    """Tests 5–6."""

    def test_required_beats_optional(self) -> None:
        """Test 5: required slot wins over optional."""
        state = _in_progress_state()
        result = select_next_action(
            state,
            slot_definitions=[
                _slot_def("optional_a", required=False, priority=1),
                _slot_def("required_b", required=True, priority=99),
            ],
        )
        assert result.slot_id == "required_b"

    def test_lower_priority_wins(self) -> None:
        """Test 6: Within same required class, lower priority wins."""
        state = _in_progress_state()
        result = select_next_action(
            state,
            slot_definitions=[
                _slot_def("high_pri", required=True, priority=10),
                _slot_def("low_pri", required=True, priority=1),
            ],
        )
        assert result.slot_id == "low_pri"


# ══════════════════════════════════════════════════════════════════════════════
# DETERMINISM
# ══════════════════════════════════════════════════════════════════════════════


class TestDeterminism:
    """Tests 7–8."""

    def test_repeated_calls_deterministic(self) -> None:
        """Test 7: Identical inputs produce identical results."""
        state = _in_progress_state()
        defs = [
            _slot_def("alpha", required=True, priority=5),
            _slot_def("beta", required=True, priority=5),
            _slot_def("gamma", required=False, priority=1),
        ]
        results = [select_next_action(state, defs) for _ in range(10)]
        assert all(r == results[0] for r in results)

    def test_selector_does_not_mutate_state(self) -> None:
        """Test 8: No input model is modified."""
        slot = SlotState(status=SlotStatus.UNKNOWN)
        state = _in_progress_state(onset=slot)
        defs = [_slot_def("onset", required=True, priority=1)]

        state_before = state.model_dump()
        slot_before = slot.model_dump()

        select_next_action(state, defs)

        assert state.model_dump() == state_before
        assert slot.model_dump() == slot_before


# ══════════════════════════════════════════════════════════════════════════════
# VERIFY_HISTORY
# ══════════════════════════════════════════════════════════════════════════════


class TestVerifyHistory:
    """Tests 9–12."""

    def test_eligible_pending_target_produces_verify(self) -> None:
        """Test 9: PENDING target with eligible candidate → VERIFY_HISTORY."""
        state = _in_progress_state()
        defs = [_slot_def("current_medications", required=True, priority=1)]
        cand, target = _make_candidate_and_target("current_medications")

        result = select_next_action(
            state, defs,
            candidates=[cand],
            verification_targets=[target],
        )
        assert result.action == SelectionAction.VERIFY_HISTORY
        assert result.slot_id == "current_medications"
        assert result.verification_target_id == str(target.target_id)

    def test_confirmed_target_ignored(self) -> None:
        """Test 10."""
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target(
            "med", target_status=VerificationTargetStatus.CONFIRMED,
        )
        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        # Falls through to ASK_NEW since target is not PENDING
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "med"

    def test_rejected_target_ignored(self) -> None:
        """Test 11."""
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target(
            "med", target_status=VerificationTargetStatus.REJECTED,
        )
        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.ASK_NEW

    def test_skipped_target_ignored(self) -> None:
        """Test 12."""
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target(
            "med", target_status=VerificationTargetStatus.SKIPPED,
        )
        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.ASK_NEW


# ══════════════════════════════════════════════════════════════════════════════
# SEPARATION
# ══════════════════════════════════════════════════════════════════════════════


class TestSeparation:
    """Tests 13–14."""

    def test_evidence_does_not_make_slot_known(self) -> None:
        """Test 13: Evidence existence does NOT auto-promote slot."""
        slot = SlotState(status=SlotStatus.UNKNOWN)
        state = _in_progress_state(med=slot)
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert slot.status == SlotStatus.UNKNOWN

    def test_no_medication_name_in_result(self) -> None:
        """Test 14: SelectionResult contains no natural-language text."""
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        # Result fields are action enum, slot_id, target_id — no text
        field_names = set(SelectionResult.model_fields.keys())
        assert "question_text" not in field_names
        assert "medication_name" not in field_names
        assert "phrased_text" not in field_names


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests 15–18."""

    def test_all_slots_filled_returns_none(self) -> None:
        """Test 15: No eligible candidates → NONE."""
        state = _in_progress_state(
            onset=SlotState(status=SlotStatus.KNOWN, value="2 hours ago"),
        )
        result = select_next_action(
            state,
            slot_definitions=[_slot_def("onset", required=True, priority=1)],
        )
        assert result.action == SelectionAction.NONE

    def test_known_slot_prevents_verify(self) -> None:
        """Test 16."""
        state = _in_progress_state(
            med=SlotState(status=SlotStatus.KNOWN, value="confirmed"),
        )
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.NONE

    def test_not_applicable_slot_prevents_verify(self) -> None:
        """Test 17."""
        state = _in_progress_state(
            med=SlotState(status=SlotStatus.NOT_APPLICABLE),
        )
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.NONE

    def test_declined_slot_prevents_verify(self) -> None:
        """Test 18."""
        state = _in_progress_state(
            med=SlotState(status=SlotStatus.DECLINED),
        )
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.NONE


# ══════════════════════════════════════════════════════════════════════════════
# MIXED ORDERING
# ══════════════════════════════════════════════════════════════════════════════


class TestMixedOrdering:
    """Tests 19–23."""

    def test_required_ask_beats_optional_verify(self) -> None:
        """Test 19: required ASK_NEW beats optional VERIFY_HISTORY."""
        state = _in_progress_state()
        defs = [
            _slot_def("onset", required=True, priority=1),
            _slot_def("med_hist", required=False, priority=2),
        ]
        cand, target = _make_candidate_and_target("med_hist")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "onset"

    def test_required_verify_beats_optional_ask(self) -> None:
        """Test 20: required VERIFY_HISTORY beats optional ASK_NEW."""
        state = _in_progress_state()
        defs = [
            _slot_def("med_hist", required=True, priority=1),
            _slot_def("optional_q", required=False, priority=2),
        ]
        cand, target = _make_candidate_and_target("med_hist")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.VERIFY_HISTORY
        assert result.slot_id == "med_hist"

    def test_lower_priority_wins_among_verify_targets(self) -> None:
        """Test 21: Lower priority wins between verification targets."""
        state = _in_progress_state()
        defs = [
            _slot_def("slot_high", required=True, priority=10),
            _slot_def("slot_low", required=True, priority=1),
        ]
        cand1, t1 = _make_candidate_and_target("slot_high")
        cand2, t2 = _make_candidate_and_target("slot_low")

        result = select_next_action(
            state, defs,
            candidates=[cand1, cand2],
            verification_targets=[t1, t2],
        )
        assert result.slot_id == "slot_low"

    def test_stable_slot_id_tiebreak(self) -> None:
        """Test 22: Alphabetical slot_id breaks ties."""
        state = _in_progress_state()
        defs = [
            _slot_def("beta", required=True, priority=5),
            _slot_def("alpha", required=True, priority=5),
        ]
        result = select_next_action(state, defs)
        assert result.slot_id == "alpha"

    def test_cross_slot_mixed_action_tie_decided_by_slot_id(self) -> None:
        """
        Cross-slot equal-priority tie: slot_id tie-breaks before action.

        ASK_NEW on 'alpha' vs VERIFY_HISTORY on 'beta', with identical
        required=True and priority=10. Because these are different slots,
        the same-slot VERIFY_HISTORY override does NOT apply; 'alpha'
        wins alphabetically, producing ASK_NEW instead of VERIFY_HISTORY.
        """
        state = _in_progress_state()
        defs = [
            _slot_def("beta", required=True, priority=10),
            _slot_def("alpha", required=True, priority=10),
        ]
        cand, target = _make_candidate_and_target("beta")

        result = select_next_action(
            state,
            defs,
            candidates=[cand],
            verification_targets=[target],
        )
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "alpha"
        assert result.verification_target_id is None

    def test_stable_target_id_tiebreak(self) -> None:
        """Test 23: For same-slot verification targets, target_id breaks ties."""
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]

        tid_a = uuid.UUID("00000000-0000-0000-0000-000000000001")
        tid_b = uuid.UUID("00000000-0000-0000-0000-000000000002")

        cand_a, target_a = _make_candidate_and_target("med", target_id=tid_a)
        cand_b, target_b = _make_candidate_and_target("med", target_id=tid_b)

        result = select_next_action(
            state, defs,
            candidates=[cand_b, cand_a],  # order reversed in input
            verification_targets=[target_b, target_a],
        )
        assert result.verification_target_id == str(tid_a)


# ══════════════════════════════════════════════════════════════════════════════
# SAME-SLOT COLLISION
# ══════════════════════════════════════════════════════════════════════════════


class TestSameSlotCollision:
    """Tests 24–26."""

    def test_unknown_plus_verify_target_selects_verify(self) -> None:
        """Test 24: UNKNOWN + same-slot PENDING target → VERIFY_HISTORY."""
        state = _in_progress_state()  # onset not in slots → UNKNOWN
        defs = [_slot_def("onset", required=True, priority=1)]
        cand, target = _make_candidate_and_target("onset")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.VERIFY_HISTORY
        assert result.slot_id == "onset"

    def test_retryable_unclear_plus_verify_selects_verify(self) -> None:
        """Test 25: retryable UNCLEAR + same-slot → VERIFY_HISTORY."""
        slot = SlotState(status=SlotStatus.UNCLEAR, retry_count=0)
        state = _in_progress_state(onset=slot)
        defs = [_slot_def("onset", required=True, priority=1)]
        cand, target = _make_candidate_and_target("onset")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.VERIFY_HISTORY
        assert result.slot_id == "onset"

    def test_exhausted_unclear_plus_verify_selects_verify(self) -> None:
        """Test 26: exhausted UNCLEAR + eligible target → VERIFY_HISTORY."""
        slot = SlotState(status=SlotStatus.UNCLEAR, retry_count=1)
        state = _in_progress_state(onset=slot)
        defs = [_slot_def("onset", required=True, priority=1)]
        cand, target = _make_candidate_and_target("onset")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        assert result.action == SelectionAction.VERIFY_HISTORY
        assert result.slot_id == "onset"


# ══════════════════════════════════════════════════════════════════════════════
# ORPHANED TARGETS
# ══════════════════════════════════════════════════════════════════════════════


class TestOrphanedTargets:
    """Tests 27–28."""

    def test_orphaned_slot_id_ignored(self) -> None:
        """Test 27: Target with non-existent related_slot_id is skipped."""
        state = _in_progress_state()
        defs = [_slot_def("onset", required=True, priority=1)]
        cand, target = _make_candidate_and_target("nonexistent_slot")

        result = select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )
        # Falls through to ASK_NEW for "onset"
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "onset"

    def test_valid_candidate_selected_alongside_orphan(self) -> None:
        """Test 28: An orphaned target doesn't prevent valid selection."""
        state = _in_progress_state()
        defs = [
            _slot_def("onset", required=True, priority=1),
            _slot_def("med", required=True, priority=2),
        ]
        cand_orphan, target_orphan = _make_candidate_and_target("ghost_slot")
        cand_valid, target_valid = _make_candidate_and_target("med")

        result = select_next_action(
            state, defs,
            candidates=[cand_orphan, cand_valid],
            verification_targets=[target_orphan, target_valid],
        )
        # "onset" (priority=1) has no verify → ASK_NEW
        # "med" (priority=2) has verify → VERIFY_HISTORY
        # onset is required+priority 1 → wins
        assert result.action == SelectionAction.ASK_NEW
        assert result.slot_id == "onset"


# ══════════════════════════════════════════════════════════════════════════════
# RESULT MODEL
# ══════════════════════════════════════════════════════════════════════════════


class TestSelectionResult:
    """Tests 29–30."""

    def test_result_has_exactly_three_fields(self) -> None:
        """Test 29: SelectionResult has exactly action/slot_id/verification_target_id."""
        fields = set(SelectionResult.model_fields.keys())
        assert fields == {"action", "slot_id", "verification_target_id"}

    def test_result_is_immutable(self) -> None:
        """Test 30: Frozen model prevents mutation."""
        result = SelectionResult(
            action=SelectionAction.ASK_NEW,
            slot_id="onset",
        )
        with pytest.raises(ValidationError):
            result.slot_id = "something_else"


# ══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL MUTATION SAFETY
# ══════════════════════════════════════════════════════════════════════════════


class TestMutationSafety:
    """Verify no selector call mutates any input object."""

    def test_candidates_not_mutated(self) -> None:
        state = _in_progress_state()
        defs = [_slot_def("med", required=True, priority=1)]
        cand, target = _make_candidate_and_target("med")

        cand_dump = cand.model_dump()
        target_dump = target.model_dump()

        select_next_action(
            state, defs, candidates=[cand], verification_targets=[target],
        )

        assert cand.model_dump() == cand_dump
        assert target.model_dump() == target_dump

    def test_slot_definitions_not_mutated(self) -> None:
        state = _in_progress_state()
        defs = [
            _slot_def("a", required=True, priority=1),
            _slot_def("b", required=False, priority=2),
        ]
        defs_dump = [d.model_dump() for d in defs]

        select_next_action(state, defs)

        assert [d.model_dump() for d in defs] == defs_dump
