"""
Deterministic Red-Flag Evaluator — Clinical Engine (Step 3B).

Pure, deterministic evaluator that checks structured clinical slot state
against registered red-flag definitions and returns matched flags.

Pipeline position:

    ClinicalSessionState.slots
            +
    registered red-flag definitions (from ClinicalTemplate.red_flags)
            ↓
    deterministic predicate evaluation
            ↓
    RedFlagEvaluationResult (matched red-flag IDs, severities, actions)

Properties:
    - Deterministic: identical inputs always produce identical output.
    - Pure: does NOT mutate any input model.
    - Safety-critical: UNKNOWN/missing slots never satisfy positive conditions.
    - No LLM, no clinical reasoning, no diagnosis.

This module does NOT:
    - Diagnose, recommend treatment, or interpret clinical meaning.
    - Set session status, escalate, or mutate any state.
    - Invent red-flag rules, severity values, or actions.
    - Use natural-language matching against raw text.
    - Cache evaluation results.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.clinical_engine.duration import DurationValue
from app.domain.clinical_engine.enums import (
    RedFlagAction,
    RedFlagSeverity,
    SlotStatus,
)
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.template_schema import (
    RedFlagConditionGroup,
    RedFlagConditionPredicate,
    RedFlagDefinition,
)


# ── Matched red-flag entry ──────────────────────────────────────────────────


class RedFlagMatch(BaseModel):
    """A single red-flag rule that matched the current session state."""

    model_config = ConfigDict(frozen=True)

    red_flag_id: str = Field(
        ..., description="ID of the matched red-flag rule.",
    )
    severity: RedFlagSeverity = Field(
        ..., description="Registered severity of the matched rule.",
    )
    action: RedFlagAction = Field(
        ..., description="Registered action for the matched rule.",
    )


# ── Evaluation result (immutable) ──────────────────────────────────────────


class RedFlagEvaluationResult(BaseModel):
    """
    Immutable result of deterministic red-flag evaluation.

    Contains all red-flag rules that matched the current session state,
    in deterministic order (the order they appear in the template's
    red_flags list).
    """

    model_config = ConfigDict(frozen=True)

    matched: tuple[RedFlagMatch, ...] = Field(
        default=(),
        description="Red-flag rules that matched, in template definition order.",
    )

    @property
    def has_matches(self) -> bool:
        """Whether any red flag matched."""
        return len(self.matched) > 0

    @property
    def matched_ids(self) -> tuple[str, ...]:
        """IDs of matched red-flag rules."""
        return tuple(m.red_flag_id for m in self.matched)


# ── Predicate evaluation ───────────────────────────────────────────────────


def _get_slot_value_for_evaluation(
    state: ClinicalSessionState,
    slot_id: str,
) -> tuple[bool, Any]:
    """
    Retrieve a slot's value for red-flag predicate evaluation.

    Returns (is_available, value) where:
        - is_available=False if the slot is missing, UNKNOWN, UNCLEAR,
          NOT_APPLICABLE, or DECLINED (value is None in all these cases).
        - is_available=True + the actual value if slot status is KNOWN.

    Safety principle: only KNOWN values participate in positive matching.
    A missing/UNKNOWN slot must NOT accidentally satisfy a positive condition.
    """
    slot_state = state.slots.get(slot_id)
    if slot_state is None:
        return False, None
    if slot_state.status != SlotStatus.KNOWN:
        return False, None
    return True, slot_state.value


def _evaluate_predicate(
    predicate: RedFlagConditionPredicate,
    state: ClinicalSessionState,
) -> bool:
    """
    Evaluate a single red-flag condition predicate against session state.

    Returns True if the predicate is satisfied, False otherwise.

    Safety rules:
        - UNKNOWN/missing slots → predicate is NOT satisfied.
        - Malformed values → predicate is NOT satisfied.
        - No type coercion beyond what Python's comparison operators do.
    """
    is_available, value = _get_slot_value_for_evaluation(state, predicate.slot)

    if not is_available:
        # UNKNOWN / missing / non-KNOWN slot → never satisfies a positive
        # condition. This is the core safety guarantee.
        return False

    # ── equals ──────────────────────────────────────────────────────────
    if predicate.equals is not None:
        if not _equals_match(value, predicate.equals):
            return False

    # ── gte ─────────────────────────────────────────────────────────────
    if predicate.gte is not None:
        numeric = _extract_numeric(value)
        if numeric is None:
            return False
        if numeric < predicate.gte:
            return False

    # ── lte ─────────────────────────────────────────────────────────────
    if predicate.lte is not None:
        numeric = _extract_numeric(value)
        if numeric is None:
            return False
        if numeric > predicate.lte:
            return False

    # ── contains_any ────────────────────────────────────────────────────
    if predicate.contains_any is not None:
        if not _contains_any_match(value, predicate.contains_any):
            return False

    # ── not_empty ───────────────────────────────────────────────────────
    if predicate.not_empty is not None and predicate.not_empty:
        if not _is_not_empty(value):
            return False

    return True


def _equals_match(value: Any, expected: Any) -> bool:
    """Check if value equals expected, with type-aware comparison."""
    # Direct equality
    if value == expected:
        return True
    # Boolean string handling: YAML `equals: true` may compare against
    # Python bool or string values from the slot
    if isinstance(expected, bool):
        if isinstance(value, bool):
            return value == expected
        # String "true"/"false" comparisons
        if isinstance(value, str):
            return value.lower() == str(expected).lower()
        return False
    return False


def _extract_numeric(value: Any) -> float | None:
    """
    Extract a numeric value for gte/lte comparison.

    Supports:
        - int, float directly
        - DurationValue → uses numeric_value
        - str that can be parsed as float (defensive only)

    Returns None if the value cannot be interpreted numerically.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, DurationValue):
        return float(value.numeric_value)
    if isinstance(value, dict) and "numeric_value" in value:
        # DurationValue stored as dict (e.g. from JSON deserialization)
        try:
            return float(value["numeric_value"])
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _contains_any_match(value: Any, keywords: list[str]) -> bool:
    """
    Check if a text value contains any of the given keywords.

    Uses case-insensitive substring matching, as the existing clinical
    content uses contains_any on text slots (e.g. chest_pain radiation
    slot checking for "arm", "shoulder", etc.).
    """
    if not isinstance(value, str):
        return False
    value_lower = value.lower()
    return any(kw.lower() in value_lower for kw in keywords)


def _is_not_empty(value: Any) -> bool:
    """
    Check if a value is meaningfully non-empty.

    Empty means: None, empty string, or whitespace-only string.
    """
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    # Non-string non-None values are considered non-empty
    return True


# ── Condition group evaluation ─────────────────────────────────────────────


def _evaluate_condition_group(
    group: RedFlagConditionGroup,
    state: ClinicalSessionState,
) -> bool:
    """
    Evaluate a red-flag condition group (all_of or any_of).

    For all_of: ALL predicates must match.
    For any_of: AT LEAST ONE predicate must match.
    """
    if group.all_of is not None:
        return all(
            _evaluate_predicate(pred, state) for pred in group.all_of
        )
    if group.any_of is not None:
        return any(
            _evaluate_predicate(pred, state) for pred in group.any_of
        )
    # Schema validator ensures exactly one is set; this is a safety fallback
    return False


# ── Main evaluation function ──────────────────────────────────────────────


def evaluate_red_flags(
    state: ClinicalSessionState,
    red_flag_definitions: list[RedFlagDefinition],
) -> RedFlagEvaluationResult:
    """
    Evaluate red-flag rules against the current clinical session state.

    Args:
        state: Current clinical session state (read-only).
        red_flag_definitions: The red-flag rules to evaluate,
            typically from ``ClinicalTemplate.red_flags``.

    Returns:
        An immutable ``RedFlagEvaluationResult`` containing all
        matched red-flag rules in definition order.

    This function is:
        - Pure: does NOT mutate state or red_flag_definitions.
        - Deterministic: identical inputs → identical output.
        - Safe: UNKNOWN/missing slots never create false positive matches.

    This function does NOT:
        - Set session status or lifecycle transitions.
        - Generate diagnosis or treatment recommendations.
        - Use LLM or natural-language matching.
    """
    matches: list[RedFlagMatch] = []
    seen_ids: set[str] = set()

    for rf in red_flag_definitions:
        # Skip duplicate rule IDs (defensive — validator should prevent this)
        if rf.id in seen_ids:
            continue
        seen_ids.add(rf.id)

        if _evaluate_condition_group(rf.when, state):
            matches.append(
                RedFlagMatch(
                    red_flag_id=rf.id,
                    severity=rf.severity,
                    action=rf.action,
                )
            )

    return RedFlagEvaluationResult(matched=tuple(matches))
