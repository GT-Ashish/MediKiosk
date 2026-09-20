"""
Deterministic Question Selector — Clinical Engine.

Decides WHAT should happen next in the adaptive clinical interview.
Returns an immutable ``SelectionResult`` without mutating any input.

The selector is fully deterministic: identical inputs always produce
the identical result.  No LLM, randomness, timestamps, network calls,
or clinical inference.

Selection actions:
    ASK_NEW         — Ask the patient a new question for a slot.
    VERIFY_HISTORY  — Verify historical document-derived evidence with
                      the patient before using it.
    NONE            — No further action (session not in progress, or
                      no eligible candidates remain).

Ordering rules (single deterministic ordering for both actions):
    1. required slots before optional slots
    2. lower priority number first
    3. stable slot_id alphabetical tie-break
    4. for same-slot VERIFY_HISTORY: verification_target_id tie-break

Same-slot collision rule:
    When both ASK_NEW and VERIFY_HISTORY target the same clinical slot,
    VERIFY_HISTORY wins — verify existing evidence rather than asking
    the same question from scratch.

Hard constraints:
    - Never returns an action for non-IN_PROGRESS sessions.
    - Never mutates any input model.
    - Never generates natural-language question text.
    - Never infers clinical meaning (e.g. metformin ≠ diabetes).
    - Never auto-promotes a slot from UNKNOWN → KNOWN.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.domain.clinical_engine.document_evidence import (
    HistoricalContextCandidate,
    VerificationTarget,
    VerificationTargetStatus,
)
from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    SlotStatus,
)
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.template_schema import SlotDefinition


# ── Selection action enum ───────────────────────────────────────────────────


class SelectionAction(str, Enum):
    """The type of action the selector recommends."""

    ASK_NEW = "ask_new"
    VERIFY_HISTORY = "verify_history"
    NONE = "none"


# ── Selection result (immutable) ────────────────────────────────────────────


class SelectionResult(BaseModel):
    """
    Immutable result of the question selector.

    Contains exactly:
        action                — what to do next
        slot_id               — which clinical slot (None for NONE)
        verification_target_id — which target to verify (only for VERIFY_HISTORY)
    """

    model_config = ConfigDict(frozen=True)

    action: SelectionAction = Field(
        ..., description="Selected action type.",
    )
    slot_id: str | None = Field(
        default=None, description="Clinical slot ID, if applicable.",
    )
    verification_target_id: str | None = Field(
        default=None,
        description="Verification target ID, only for VERIFY_HISTORY.",
    )


_RESULT_NONE = SelectionResult(action=SelectionAction.NONE)


# ── Internal candidate representation ───────────────────────────────────────


class _Candidate:
    """
    Internal comparable candidate for deterministic ordering.

    Sort key: (not required, priority, slot_id, is_ask_new, target_id_str)

    - ``not required`` so True (=optional) sorts after False (=required)
    - lower priority number first
    - alphabetical slot_id for stability
    - ASK_NEW sorts after VERIFY_HISTORY for same-slot collision
      (is_ask_new=True > is_ask_new=False → VERIFY wins)
    - target_id_str for same-slot same-action tie-break
    """

    __slots__ = (
        "action", "slot_id", "target_id_str",
        "required", "priority", "sort_key",
    )

    def __init__(
        self,
        action: SelectionAction,
        slot_id: str,
        required: bool,
        priority: int,
        target_id_str: str = "",
    ) -> None:
        self.action = action
        self.slot_id = slot_id
        self.target_id_str = target_id_str
        self.required = required
        self.priority = priority
        # is_ask_new: True for ASK_NEW so it sorts AFTER VERIFY_HISTORY
        is_ask_new = action == SelectionAction.ASK_NEW
        self.sort_key = (
            not required,   # False < True → required first
            priority,
            slot_id,
            is_ask_new,     # False < True → VERIFY wins same-slot
            target_id_str,
        )

    def __lt__(self, other: _Candidate) -> bool:
        return self.sort_key < other.sort_key


# ── Selector function ──────────────────────────────────────────────────────


def select_next_action(
    state: ClinicalSessionState,
    slot_definitions: list[SlotDefinition],
    candidates: list[HistoricalContextCandidate] | None = None,
    verification_targets: list[VerificationTarget] | None = None,
) -> SelectionResult:
    """
    Deterministically select the next interview action.

    Args:
        state: Current clinical session state (read-only).
        slot_definitions: Active slot definitions from the clinical
            template (provides ``required`` and ``priority``).
        candidates: Historical context candidates already determined
            as potentially relevant by a prior step.
        verification_targets: Verification targets grouping evidence
            for patient confirmation.

    Returns:
        An immutable ``SelectionResult``.

    This function does NOT mutate any input.
    """
    # ── 1. Guard: non-IN_PROGRESS → NONE ─────────────────────────────────
    if state.session_status != ClinicalSessionStatus.IN_PROGRESS:
        return _RESULT_NONE

    candidates = candidates or []
    verification_targets = verification_targets or []

    # ── 2. Build slot definition lookup ──────────────────────────────────
    slot_def_map: dict[str, SlotDefinition] = {sd.id: sd for sd in slot_definitions}

    # ── 3. Build verification eligibility index ─────────────────────────
    #
    # For each slot_id, collect eligible (PENDING, has related_slot_id,
    # candidate requires_patient_confirmation, slot exists in template,
    # slot is not KNOWN/NOT_APPLICABLE/DECLINED) verification targets.

    # candidate evidence_id → candidate (for requires_patient_confirmation lookup)
    candidate_by_evidence: dict[str, HistoricalContextCandidate] = {}
    for c in candidates:
        candidate_by_evidence[str(c.evidence_id)] = c

    # eligible verification targets keyed by related_slot_id
    eligible_targets_by_slot: dict[str, list[VerificationTarget]] = {}

    for vt in verification_targets:
        # Must be PENDING
        if vt.status != VerificationTargetStatus.PENDING:
            continue
        # Must have a related_slot_id
        if vt.related_slot_id is None:
            continue
        # related_slot_id must exist in the active template
        if vt.related_slot_id not in slot_def_map:
            continue
        # The related slot must not be KNOWN, NOT_APPLICABLE, or DECLINED
        slot_state = state.slots.get(vt.related_slot_id)
        if slot_state is not None and slot_state.status in (
            SlotStatus.KNOWN,
            SlotStatus.NOT_APPLICABLE,
            SlotStatus.DECLINED,
        ):
            continue
        # At least one evidence_id must have a corresponding candidate
        # that requires patient confirmation
        has_confirmable = False
        for eid in vt.evidence_ids:
            c = candidate_by_evidence.get(str(eid))
            if c is not None and c.requires_patient_confirmation:
                has_confirmable = True
                break
        if not has_confirmable:
            continue

        slot_id = vt.related_slot_id
        eligible_targets_by_slot.setdefault(slot_id, []).append(vt)

    # ── 4. Build all candidates ──────────────────────────────────────────

    all_candidates: list[_Candidate] = []

    # Set of slot_ids that have eligible VERIFY_HISTORY targets
    slots_with_verify = set(eligible_targets_by_slot.keys())

    for sd in slot_definitions:
        slot_state = state.slots.get(sd.id)

        # Determine if this slot is an ASK_NEW candidate
        is_ask_candidate = False
        if slot_state is None:
            # Slot not yet in state → treated as UNKNOWN
            is_ask_candidate = True
        elif slot_state.status == SlotStatus.UNKNOWN:
            is_ask_candidate = True
        elif (
            slot_state.status == SlotStatus.UNCLEAR
            and slot_state.retry_count < 1
        ):
            is_ask_candidate = True

        # If this slot has eligible verification targets, add them
        if sd.id in slots_with_verify:
            for vt in eligible_targets_by_slot[sd.id]:
                all_candidates.append(
                    _Candidate(
                        action=SelectionAction.VERIFY_HISTORY,
                        slot_id=sd.id,
                        required=sd.required,
                        priority=sd.priority,
                        target_id_str=str(vt.target_id),
                    )
                )

        # Add ASK_NEW candidate only if no same-slot VERIFY exists
        # (same-slot collision: VERIFY wins)
        if is_ask_candidate and sd.id not in slots_with_verify:
            all_candidates.append(
                _Candidate(
                    action=SelectionAction.ASK_NEW,
                    slot_id=sd.id,
                    required=sd.required,
                    priority=sd.priority,
                )
            )

        # Also handle exhausted UNCLEAR: not an ASK_NEW candidate,
        # but eligible VERIFY_HISTORY targets were already added above.

    if not all_candidates:
        return _RESULT_NONE

    # ── 5. Sort and pick the winner ──────────────────────────────────────

    all_candidates.sort()
    winner = all_candidates[0]

    if winner.action == SelectionAction.ASK_NEW:
        return SelectionResult(
            action=SelectionAction.ASK_NEW,
            slot_id=winner.slot_id,
        )
    else:
        return SelectionResult(
            action=SelectionAction.VERIFY_HISTORY,
            slot_id=winner.slot_id,
            verification_target_id=winner.target_id_str,
        )
