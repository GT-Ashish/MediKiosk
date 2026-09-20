"""
Completion Policy — Clinical Engine.

Deterministic question-budget and completion-policy layer (Step 2B).

Pipeline position:

    ClinicalSessionState + SlotDefinitions
            ↓
    Step 2A  →  SelectionResult (ASK_NEW / VERIFY_HISTORY / NONE)
            ↓
    Step 2B  →  CompletionResult (CONTINUE / COMPLETE / INCOMPLETE_REQUIRED)

Step 2B answers:
    1. Is another question permitted under the maximum budget?
    2. Has the interview reached a terminal COMPLETE state?
    3. Has the engine become unable to resolve required slots?

Precondition:
    The caller MUST ensure ``session.session_status == IN_PROGRESS``
    before invoking ``evaluate_completion``.  Step 2B does NOT handle
    non-IN_PROGRESS lifecycle states.

Step 2B does NOT:
    - Choose a slot (Step 2A responsibility)
    - Generate question text
    - Perform clinical reasoning
    - Infer relevance
    - Mutate any state
    - Manage session lifecycle transitions

min_questions is informational only — it does NOT:
    - Fabricate questions
    - Force optional questions
    - Override Step 2A priority or collision rules
    - Revive exhausted UNCLEAR slots
    - Make KNOWN slots eligible
    - Make historical evidence equivalent to KNOWN
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.domain.clinical_engine.enums import SlotStatus
from app.domain.clinical_engine.question_selector import (
    SelectionAction,
    SelectionResult,
)
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.template_schema import SlotDefinition


# ── Completion decision enum ────────────────────────────────────────────────


class CompletionDecision(str, Enum):
    """The completion-policy decision for an IN_PROGRESS session.

    CONTINUE:
        Another question is permitted and Step 2A selected a valid
        action (ASK_NEW or VERIFY_HISTORY).

    COMPLETE:
        The interview has reached a valid terminal state — all
        required slots are resolved and either:
        (a) no eligible candidates remain (Step 2A returned NONE), or
        (b) the maximum question budget is exhausted.

    INCOMPLETE_REQUIRED:
        The engine has no remaining valid path to resolve one or more
        required slots.  This can occur because:
        (a) the maximum question budget is exhausted while required
            information remains unresolved, or
        (b) Step 2A returned NONE while required information remains
            unresolved.
    """

    CONTINUE = "continue"
    COMPLETE = "complete"
    INCOMPLETE_REQUIRED = "incomplete_required"


# ── Completion result (immutable) ───────────────────────────────────────────


class CompletionResult(BaseModel):
    """Immutable result of the completion-policy evaluation.

    Contains exactly:
        decision — CONTINUE, COMPLETE, or INCOMPLETE_REQUIRED
    """

    model_config = ConfigDict(frozen=True)

    decision: CompletionDecision = Field(
        ..., description="Completion-policy decision.",
    )


# ── Resolved-status set ─────────────────────────────────────────────────────

_RESOLVED_STATUSES: frozenset[SlotStatus] = frozenset({
    SlotStatus.KNOWN,
    SlotStatus.NOT_APPLICABLE,
    SlotStatus.DECLINED,
})


# ── Helper: unresolved-required check ───────────────────────────────────────


def _has_unresolved_required(
    state: ClinicalSessionState,
    slot_definitions: list[SlotDefinition],
) -> bool:
    """Return True if any required slot is not resolved.

    A required slot is unresolved when its SlotState.status is NOT
    one of KNOWN, NOT_APPLICABLE, or DECLINED.

    Slots absent from ``state.slots`` are treated as UNKNOWN
    (unresolved).
    """
    for sd in slot_definitions:
        if not sd.required:
            continue
        slot_state = state.slots.get(sd.id)
        if slot_state is None:
            # Absent → treated as UNKNOWN → unresolved
            return True
        if slot_state.status not in _RESOLVED_STATUSES:
            return True
    return False


# ── Main evaluation function ───────────────────────────────────────────────


def evaluate_completion(
    state: ClinicalSessionState,
    slot_definitions: list[SlotDefinition],
    selection_result: SelectionResult,
) -> CompletionResult:
    """Evaluate question-budget and completion policy (Step 2B).

    Args:
        state: Current clinical session state (read-only).
            The caller MUST verify ``state.session_status == IN_PROGRESS``
            before calling this function.
        slot_definitions: Active slot definitions from the clinical
            template (provides ``required`` flag).
        selection_result: The result from Step 2A
            (``select_next_action``).

    Returns:
        An immutable ``CompletionResult``.

    This function does NOT mutate any input.
    """
    # ── 1. Max-budget enforcement ────────────────────────────────────────
    #
    # If question_budget is set and question_count >= max_questions,
    # no additional question may be authorized.
    if (
        state.question_budget is not None
        and state.question_count >= state.question_budget.max_questions
    ):
        if _has_unresolved_required(state, slot_definitions):
            return CompletionResult(
                decision=CompletionDecision.INCOMPLETE_REQUIRED,
            )
        return CompletionResult(decision=CompletionDecision.COMPLETE)

    # ── 2. Step 2A returned NONE ─────────────────────────────────────────
    #
    # No eligible ASK_NEW or VERIFY_HISTORY candidates remain.
    # Do NOT automatically return COMPLETE — check for unresolved
    # required information first.
    if selection_result.action == SelectionAction.NONE:
        if _has_unresolved_required(state, slot_definitions):
            return CompletionResult(
                decision=CompletionDecision.INCOMPLETE_REQUIRED,
            )
        return CompletionResult(decision=CompletionDecision.COMPLETE)

    # ── 3. Normal continuation ───────────────────────────────────────────
    #
    # Step 2A selected ASK_NEW or VERIFY_HISTORY, and the budget
    # has not been exhausted.
    return CompletionResult(decision=CompletionDecision.CONTINUE)
