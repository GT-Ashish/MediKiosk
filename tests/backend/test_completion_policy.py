"""
Tests for Phase 7 completion policy (Step 2B).

Step 2B sits downstream of the Step 2A selector in the pipeline:

    Step 2A  →  SelectionResult (ASK_NEW / VERIFY_HISTORY / NONE)
        ↓
    Step 2B  →  CompletionResult (CONTINUE / COMPLETE / INCOMPLETE_REQUIRED)

Step 2B answers:
    - Is another question permitted under the maximum budget?
    - Has the interview reached a terminal COMPLETE state?
    - Has the engine become unable to resolve required slots?

Precondition:
    session.session_status == IN_PROGRESS (caller-enforced).

Test categories:

NORMAL CONTINUATION
    1.  below max budget + ASK_NEW → CONTINUE
    2.  below max budget + VERIFY_HISTORY → CONTINUE

MAX BUDGET ENFORCEMENT
    3.  exactly max budget + unresolved required → INCOMPLETE_REQUIRED
    4.  above max budget + unresolved required → INCOMPLETE_REQUIRED
    5.  exactly max budget + no unresolved required → COMPLETE
    6.  above max budget + no unresolved required → COMPLETE

STEP 2A NONE HANDLING
    7.  NONE + unresolved required → INCOMPLETE_REQUIRED
    8.  NONE + no unresolved required → COMPLETE
    9.  NONE + exhausted UNCLEAR required slot → INCOMPLETE_REQUIRED
    10. NONE + UNKNOWN required slot → INCOMPLETE_REQUIRED (synthetic)
    11. NONE + UNKNOWN optional only → COMPLETE

MIN_QUESTIONS (INFORMATIONAL ONLY)
    12. below min_questions + eligible candidate → CONTINUE
    13. below min_questions + no eligible candidate + no unresolved required → COMPLETE
    14. below min_questions + no eligible candidate + unresolved required → INCOMPLETE_REQUIRED
    15. min_questions does NOT reorder required vs optional
    16. min_questions does NOT revive exhausted UNCLEAR
    17. min_questions does NOT make KNOWN eligible

DOCUMENT EVIDENCE
    18. document evidence does NOT make a required slot resolved

RESOLVED STATUS TESTS
    19. NOT_APPLICABLE required slot counts as resolved
    20. DECLINED required slot counts as resolved
    21. KNOWN required slot counts as resolved
    22. UNKNOWN required slot counts as unresolved
    23. UNCLEAR required slot counts as unresolved

PURITY
    24. no state mutation
    25. deterministic repeated calls

BOUNDARY VALUES
    26. question_count = max_questions - 1 + ASK_NEW → CONTINUE
    27. question_count = max_questions + ASK_NEW → INCOMPLETE_REQUIRED
    28. question_count = max_questions + 1 + no unresolved → COMPLETE
    29. question_count = min_questions - 1 + ASK_NEW → CONTINUE
    30. question_count = min_questions + ASK_NEW → CONTINUE
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from app.domain.clinical_engine.completion_policy import (
    CompletionDecision,
    CompletionResult,
    evaluate_completion,
)
from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    SlotStatus,
    SlotType,
)
from app.domain.clinical_engine.question_selector import (
    SelectionAction,
    SelectionResult,
)
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.template_schema import (
    QuestionBudget,
    SlotDefinition,
)


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


def _budget(min_q: int = 5, max_q: int = 20) -> QuestionBudget:
    return QuestionBudget(min_questions=min_q, max_questions=max_q)


def _state(
    *,
    question_count: int = 0,
    budget: QuestionBudget | None = None,
    **slot_overrides: SlotState,
) -> ClinicalSessionState:
    """Build an IN_PROGRESS session with given slots and budget."""
    return ClinicalSessionState(
        session_status=ClinicalSessionStatus.IN_PROGRESS,
        question_count=question_count,
        question_budget=budget,
        slots=slot_overrides,
    )


def _ask_new(slot_id: str = "onset") -> SelectionResult:
    return SelectionResult(action=SelectionAction.ASK_NEW, slot_id=slot_id)


def _verify_history(
    slot_id: str = "med",
    target_id: str = "tid-1",
) -> SelectionResult:
    return SelectionResult(
        action=SelectionAction.VERIFY_HISTORY,
        slot_id=slot_id,
        verification_target_id=target_id,
    )


_NONE = SelectionResult(action=SelectionAction.NONE)


# ══════════════════════════════════════════════════════════════════════════════
# NORMAL CONTINUATION
# ══════════════════════════════════════════════════════════════════════════════


class TestNormalContinuation:
    """Tests 1–2."""

    def test_below_max_ask_new_continue(self) -> None:
        """Test 1: below max budget + ASK_NEW → CONTINUE."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_below_max_verify_history_continue(self) -> None:
        """Test 2: below max budget + VERIFY_HISTORY → CONTINUE."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("med", required=True)]
        result = evaluate_completion(state, defs, _verify_history("med"))
        assert result.decision == CompletionDecision.CONTINUE


# ══════════════════════════════════════════════════════════════════════════════
# MAX BUDGET ENFORCEMENT
# ══════════════════════════════════════════════════════════════════════════════


class TestMaxBudget:
    """Tests 3–6."""

    def test_exactly_max_unresolved_required_incomplete(self) -> None:
        """Test 3: question_count == max_questions + unresolved → INCOMPLETE_REQUIRED."""
        state = _state(question_count=20, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_above_max_unresolved_required_incomplete(self) -> None:
        """Test 4: question_count > max_questions + unresolved → INCOMPLETE_REQUIRED."""
        state = _state(question_count=25, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_exactly_max_no_unresolved_complete(self) -> None:
        """Test 5: question_count == max_questions + no unresolved → COMPLETE."""
        state = _state(
            question_count=20,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="2 hours ago"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_above_max_no_unresolved_complete(self) -> None:
        """Test 6: question_count > max_questions + no unresolved → COMPLETE."""
        state = _state(
            question_count=25,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="2 hours ago"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2A NONE HANDLING
# ══════════════════════════════════════════════════════════════════════════════


class TestStep2ANone:
    """Tests 7–11."""

    def test_none_unresolved_required_incomplete(self) -> None:
        """Test 7: NONE + unresolved required → INCOMPLETE_REQUIRED."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_none_no_unresolved_complete(self) -> None:
        """Test 8: NONE + no unresolved required → COMPLETE."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="2 hours ago"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_none_exhausted_unclear_required_incomplete(self) -> None:
        """Test 9: NONE + exhausted UNCLEAR required → INCOMPLETE_REQUIRED."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNCLEAR, retry_count=1),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_none_unknown_required_incomplete(self) -> None:
        """Test 10: NONE + UNKNOWN required slot → INCOMPLETE_REQUIRED.

        Synthetic test: an actual Step 2A invocation would generate
        ASK_NEW for an UNKNOWN slot, not NONE.  This verifies the
        unresolved-required detection itself.
        """
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNKNOWN),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_none_unknown_optional_only_complete(self) -> None:
        """Test 11: NONE + UNKNOWN optional only → COMPLETE."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("optional_q", required=False)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE


# ══════════════════════════════════════════════════════════════════════════════
# MIN_QUESTIONS (INFORMATIONAL ONLY)
# ══════════════════════════════════════════════════════════════════════════════


class TestMinQuestions:
    """Tests 12–17."""

    def test_below_min_eligible_candidate_continue(self) -> None:
        """Test 12: below min_questions + eligible candidate → CONTINUE."""
        state = _state(question_count=2, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_below_min_no_eligible_no_unresolved_complete(self) -> None:
        """Test 13: below min + NONE + no unresolved → COMPLETE."""
        state = _state(
            question_count=2,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="2 hours ago"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_below_min_no_eligible_unresolved_incomplete(self) -> None:
        """Test 14: below min + NONE + unresolved required → INCOMPLETE_REQUIRED."""
        state = _state(
            question_count=2,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNCLEAR, retry_count=1),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_min_does_not_reorder_required_vs_optional(self) -> None:
        """Test 15: min_questions does not change ordering.

        With question_count below min_questions, an ASK_NEW on a
        required slot still returns CONTINUE — the min is informational.
        """
        state = _state(question_count=1, budget=_budget(5, 20))
        defs = [
            _slot_def("req_slot", required=True, priority=10),
            _slot_def("opt_slot", required=False, priority=1),
        ]
        # Step 2A would select opt_slot (lower priority if both were
        # ASK_NEW candidates), but the selection_result is passed to
        # Step 2B directly.  Step 2B does not reorder.
        result = evaluate_completion(state, defs, _ask_new("opt_slot"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_min_does_not_revive_exhausted_unclear(self) -> None:
        """Test 16: min_questions does not revive exhausted UNCLEAR.

        Even below min_questions, an exhausted UNCLEAR required slot
        with NONE from Step 2A → INCOMPLETE_REQUIRED.
        """
        state = _state(
            question_count=1,
            budget=_budget(10, 20),
            onset=SlotState(status=SlotStatus.UNCLEAR, retry_count=1),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_min_does_not_make_known_eligible(self) -> None:
        """Test 17: min_questions does not make KNOWN slots eligible.

        Below min_questions with all required slots KNOWN and Step 2A
        returning NONE → COMPLETE, not forced to continue.
        """
        state = _state(
            question_count=1,
            budget=_budget(10, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="answer"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT EVIDENCE
# ══════════════════════════════════════════════════════════════════════════════


class TestDocumentEvidence:
    """Test 18."""

    def test_evidence_does_not_resolve_required(self) -> None:
        """Test 18: evidence does not make a required slot resolved.

        A required slot that is still UNKNOWN remains unresolved
        regardless of whether document evidence exists for it.
        Step 2B treats UNKNOWN as unresolved.
        """
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            med=SlotState(status=SlotStatus.UNKNOWN),
        )
        defs = [_slot_def("med", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED


# ══════════════════════════════════════════════════════════════════════════════
# RESOLVED STATUS TESTS
# ══════════════════════════════════════════════════════════════════════════════


class TestResolvedStatus:
    """Tests 19–23."""

    def test_not_applicable_counts_as_resolved(self) -> None:
        """Test 19: NOT_APPLICABLE required slot is resolved."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.NOT_APPLICABLE),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_declined_counts_as_resolved(self) -> None:
        """Test 20: DECLINED required slot is resolved."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.DECLINED),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_known_counts_as_resolved(self) -> None:
        """Test 21: KNOWN required slot is resolved."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="answer"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_unknown_counts_as_unresolved(self) -> None:
        """Test 22: UNKNOWN required slot is unresolved."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNKNOWN),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_unclear_counts_as_unresolved(self) -> None:
        """Test 23: UNCLEAR required slot is unresolved."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNCLEAR, retry_count=0),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED


# ══════════════════════════════════════════════════════════════════════════════
# PURITY
# ══════════════════════════════════════════════════════════════════════════════


class TestPurity:
    """Tests 24–25."""

    def test_no_state_mutation(self) -> None:
        """Test 24: evaluate_completion does not mutate any input."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNKNOWN),
        )
        defs = [_slot_def("onset", required=True)]
        sel = _ask_new("onset")

        state_before = state.model_dump()
        defs_before = [d.model_dump() for d in defs]
        sel_before = sel.model_dump()

        evaluate_completion(state, defs, sel)

        assert state.model_dump() == state_before
        assert [d.model_dump() for d in defs] == defs_before
        assert sel.model_dump() == sel_before

    def test_deterministic_repeated_calls(self) -> None:
        """Test 25: identical inputs produce identical results."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.UNKNOWN),
        )
        defs = [_slot_def("onset", required=True)]
        sel = _ask_new("onset")

        results = [evaluate_completion(state, defs, sel) for _ in range(10)]
        assert all(r == results[0] for r in results)


# ══════════════════════════════════════════════════════════════════════════════
# BOUNDARY VALUES
# ══════════════════════════════════════════════════════════════════════════════


class TestBoundaryValues:
    """Tests 26–30."""

    def test_max_minus_one_ask_new_continue(self) -> None:
        """Test 26: question_count = max_questions - 1 + ASK_NEW → CONTINUE."""
        state = _state(question_count=19, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_exactly_max_ask_new_incomplete(self) -> None:
        """Test 27: question_count = max_questions + ASK_NEW → INCOMPLETE_REQUIRED.

        The max-budget check fires first and blocks the action.
        """
        state = _state(question_count=20, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_max_plus_one_no_unresolved_complete(self) -> None:
        """Test 28: question_count = max_questions + 1 + no unresolved → COMPLETE."""
        state = _state(
            question_count=21,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="answer"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_min_minus_one_ask_new_continue(self) -> None:
        """Test 29: question_count = min_questions - 1 + ASK_NEW → CONTINUE."""
        state = _state(question_count=4, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_min_exactly_ask_new_continue(self) -> None:
        """Test 30: question_count = min_questions + ASK_NEW → CONTINUE."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE


# ══════════════════════════════════════════════════════════════════════════════
# COMPLETION RESULT MODEL
# ══════════════════════════════════════════════════════════════════════════════


class TestCompletionResult:
    """Verify CompletionResult contract."""

    def test_result_has_exactly_one_field(self) -> None:
        """CompletionResult has exactly the 'decision' field."""
        fields = set(CompletionResult.model_fields.keys())
        assert fields == {"decision"}

    def test_result_is_immutable(self) -> None:
        """Frozen model prevents mutation."""
        result = CompletionResult(decision=CompletionDecision.CONTINUE)
        with pytest.raises(ValidationError):
            result.decision = CompletionDecision.COMPLETE


# ══════════════════════════════════════════════════════════════════════════════
# NO QUESTION_BUDGET (None) EDGE CASE
# ══════════════════════════════════════════════════════════════════════════════


class TestNoBudget:
    """When question_budget is None, max-budget check is skipped."""

    def test_no_budget_ask_new_continue(self) -> None:
        """No budget set + ASK_NEW → CONTINUE (no max enforcement)."""
        state = _state(question_count=100)
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _ask_new("onset"))
        assert result.decision == CompletionDecision.CONTINUE

    def test_no_budget_none_no_unresolved_complete(self) -> None:
        """No budget set + NONE + no unresolved → COMPLETE."""
        state = _state(
            question_count=100,
            onset=SlotState(status=SlotStatus.KNOWN, value="answer"),
        )
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE

    def test_no_budget_none_unresolved_incomplete(self) -> None:
        """No budget set + NONE + unresolved required → INCOMPLETE_REQUIRED."""
        state = _state(question_count=100)
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED


# ══════════════════════════════════════════════════════════════════════════════
# ABSENT SLOT HANDLING
# ══════════════════════════════════════════════════════════════════════════════


class TestAbsentSlot:
    """Slots not present in state.slots are treated as UNKNOWN."""

    def test_absent_required_slot_is_unresolved(self) -> None:
        """A required slot not in state.slots is treated as UNKNOWN → unresolved."""
        state = _state(question_count=5, budget=_budget(5, 20))
        defs = [_slot_def("onset", required=True)]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.INCOMPLETE_REQUIRED

    def test_absent_optional_slot_is_not_unresolved_required(self) -> None:
        """An absent optional slot does not count as unresolved required."""
        state = _state(
            question_count=5,
            budget=_budget(5, 20),
            onset=SlotState(status=SlotStatus.KNOWN, value="answer"),
        )
        defs = [
            _slot_def("onset", required=True),
            _slot_def("optional_q", required=False),
        ]
        result = evaluate_completion(state, defs, _NONE)
        assert result.decision == CompletionDecision.COMPLETE
