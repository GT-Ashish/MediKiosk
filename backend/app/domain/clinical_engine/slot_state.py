"""
Slot State Machine — Clinical Engine.

Manages the lifecycle of a single clinical information slot during
an adaptive history-taking session.

State transitions are deterministic and backend-owned:
    UNKNOWN  → KNOWN | NOT_APPLICABLE | DECLINED | UNCLEAR
    UNCLEAR  → KNOWN | DECLINED | UNCLEAR  (retry_count ≤ 1)
    KNOWN    → KNOWN  (answer revision — updates active value)

Invalid transitions raise InvalidSlotTransitionError.

Design decisions:
    - SlotState does NOT contain a revision-history collection.
      Historical answers are preserved by ClinicalSessionState.question_history
      (implemented in a later checkpoint).
    - Maximum retry count for UNCLEAR is 1, enforced at the state level.
    - Source values (voice, text, system) are kept as plain strings
      for forward compatibility without premature abstraction.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.clinical_engine.enums import SlotStatus
from app.utils.errors import InvalidSlotTransitionError

# ── Allowed transition table ───────────────────────────────────────────────────

_ALLOWED_TRANSITIONS: dict[SlotStatus, frozenset[SlotStatus]] = {
    SlotStatus.UNKNOWN: frozenset({
        SlotStatus.KNOWN,
        SlotStatus.NOT_APPLICABLE,
        SlotStatus.DECLINED,
        SlotStatus.UNCLEAR,
    }),
    SlotStatus.UNCLEAR: frozenset({
        SlotStatus.KNOWN,
        SlotStatus.DECLINED,
        SlotStatus.UNCLEAR,
    }),
    SlotStatus.KNOWN: frozenset({
        SlotStatus.KNOWN,
    }),
    SlotStatus.NOT_APPLICABLE: frozenset(),
    SlotStatus.DECLINED: frozenset(),
}

_MAX_UNCLEAR_RETRIES: int = 1


# ── SlotState model ───────────────────────────────────────────────────────────

class SlotState(BaseModel):
    """
    State of a single clinical information slot.

    A newly created SlotState starts as UNKNOWN with retry_count 0.
    Transitions are performed exclusively via ``transition_to()``.
    """

    status: SlotStatus = Field(
        default=SlotStatus.UNKNOWN,
        description="Current lifecycle status of this slot.",
    )
    value: Any = Field(
        default=None,
        description="The extracted/parsed answer value, or None if not yet known.",
    )
    confidence: float | None = Field(
        default=None,
        description="Confidence score (0.0–1.0) from extraction, if available.",
    )
    source: str | None = Field(
        default=None,
        description="How the value was obtained (e.g. 'voice', 'text', 'system').",
    )
    raw_patient_text: str | None = Field(
        default=None,
        description="Verbatim patient utterance before extraction/parsing.",
    )
    asked_at: datetime | None = Field(
        default=None,
        description="Timestamp when the question was last posed to the patient.",
    )
    retry_count: int = Field(
        default=0,
        description="Number of times this slot has entered UNCLEAR status.",
    )

    # ── Transition logic ───────────────────────────────────────────────────

    def transition_to(
        self,
        new_status: SlotStatus,
        *,
        value: Any = None,
        confidence: float | None = None,
        source: str | None = None,
        raw_patient_text: str | None = None,
        asked_at: datetime | None = None,
    ) -> None:
        """
        Transition this slot to *new_status*, enforcing allowed moves.

        Raises:
            InvalidSlotTransitionError: If the transition is not allowed
                or the UNCLEAR retry limit has been exceeded.
        """
        allowed = _ALLOWED_TRANSITIONS.get(self.status, frozenset())

        if new_status not in allowed:
            raise InvalidSlotTransitionError(
                current_status=self.status,
                target_status=new_status,
            )

        # Enforce UNCLEAR retry limit
        if new_status == SlotStatus.UNCLEAR:
            if self.retry_count >= _MAX_UNCLEAR_RETRIES:
                raise InvalidSlotTransitionError(
                    current_status=self.status,
                    target_status=new_status,
                    reason=(
                        f"UNCLEAR retry limit exceeded "
                        f"(max {_MAX_UNCLEAR_RETRIES})"
                    ),
                )
            self.retry_count += 1

        # Apply the transition
        self.status = new_status

        if value is not None:
            self.value = value
        if confidence is not None:
            self.confidence = confidence
        if source is not None:
            self.source = source
        if raw_patient_text is not None:
            self.raw_patient_text = raw_patient_text
        if asked_at is not None:
            self.asked_at = asked_at
