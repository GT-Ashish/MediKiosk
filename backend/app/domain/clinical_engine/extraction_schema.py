"""
Structured Extraction Contract — Clinical Engine (Step 4A).

Immutable Pydantic v2 models representing the output of LLM-based
clinical-slot extraction.  These models are the ONLY interface between
the LLM provider layer and the clinical engine.

Design rules:
    - ExtractionResult is frozen (immutable).  It is a proposal, not a
      committed state change.
    - Absence of a SlotObservation for a given slot means NOT_ADDRESSED
      (the patient did not mention that slot).  The LLM is NOT asked to
      produce explicit NOT_ADDRESSED entries.
    - ``value`` uses concrete JSON-compatible types only — no ``Any``.
      Step 4B will validate/normalize against ``SlotDefinition.type``.
    - ``retry_required`` is True only after the bounded retry mechanism
      exhausts its budget.  It signals safe failure: no observations,
      no trigger proposals, no state mutation.
    - Trigger proposals are closed-vocabulary identifiers — the LLM
      must not invent new ones.  Validation is deferred to Step 4B.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.clinical_engine.duration import DurationValue


# ── Slot observation outcome ─────────────────────────────────────────────────


class SlotObservationOutcome(str, Enum):
    """Outcome of a single slot observation extracted from patient speech.

    ANSWERED        — patient supplied a usable value.
    UNCLEAR         — patient addressed the topic but was unsure / vague.
    DECLINED        — patient explicitly refused to answer.
    NOT_APPLICABLE  — patient explicitly indicated it does not apply.

    NOT_ADDRESSED is represented by the *absence* of a SlotObservation.
    """

    ANSWERED = "answered"
    UNCLEAR = "unclear"
    DECLINED = "declined"
    NOT_APPLICABLE = "not_applicable"


# ── Slot observation ─────────────────────────────────────────────────────────


class SlotObservation(BaseModel):
    """
    A single slot observation extracted from the patient response.

    For ANSWERED outcomes: ``value`` is required (non-None).
    For all other outcomes: ``value`` must be None.

    ``confidence`` is extraction metadata only — it does NOT override
    backend validation or trigger any clinical logic.
    """

    model_config = ConfigDict(frozen=True)

    slot_id: str = Field(
        ..., min_length=1, description="Slot identifier from the template."
    )
    outcome: SlotObservationOutcome = Field(
        ..., description="Extraction outcome for this slot."
    )
    value: str | int | float | bool | None = Field(
        default=None,
        description=(
            "Extracted value (concrete JSON type).  "
            "Present only when outcome is ANSWERED."
        ),
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Extraction confidence 0.0–1.0 (metadata only).",
    )
    unit: str | None = Field(
        default=None,
        description="Unit string for numeric/duration slots (e.g. 'minutes').",
    )
    duration: DurationValue | None = Field(
        default=None,
        description="Structured duration for duration-type slots.",
    )

    @model_validator(mode="after")
    def _value_presence(self) -> SlotObservation:
        """Enforce value ↔ outcome consistency."""
        if self.outcome == SlotObservationOutcome.ANSWERED:
            if self.value is None:
                raise ValueError(
                    f"SlotObservation for '{self.slot_id}': "
                    f"outcome is ANSWERED but value is None."
                )
        else:
            if self.value is not None:
                raise ValueError(
                    f"SlotObservation for '{self.slot_id}': "
                    f"outcome is {self.outcome.value} but value is set "
                    f"({self.value!r}).  value must be None for non-ANSWERED."
                )
        return self


# ── Trigger proposal ─────────────────────────────────────────────────────────


class TriggerProposal(BaseModel):
    """
    A proposed trigger extracted from the patient response.

    This is only a *proposal* — the trigger ID must be validated against
    the closed trigger vocabulary before activation (Step 4B).
    """

    model_config = ConfigDict(frozen=True)

    trigger_id: str = Field(
        ..., min_length=1, description="Trigger identifier from the vocabulary."
    )


# ── Extraction result ────────────────────────────────────────────────────────


class ExtractionResult(BaseModel):
    """
    Complete structured extraction result from an LLM provider call.

    This is the sole output contract between the LLM layer and the
    clinical engine.  It is immutable and does NOT mutate any session
    or slot state.

    Fields:
        observations      — per-slot extraction observations.
        proposed_triggers — trigger IDs proposed by the model.
        detected_language — BCP-47 language code detected, or None.
        retry_required    — True only after safe failure (both attempts
                            returned malformed output).  When True,
                            observations and proposed_triggers are empty.
    """

    model_config = ConfigDict(frozen=True)

    observations: list[SlotObservation] = Field(
        default_factory=list,
        description="Per-slot observations extracted from the response.",
    )
    proposed_triggers: list[TriggerProposal] = Field(
        default_factory=list,
        description="Trigger IDs proposed by the model.",
    )
    detected_language: str | None = Field(
        default=None,
        description="BCP-47 language code detected in the patient response.",
    )
    retry_required: bool = Field(
        default=False,
        description=(
            "True when extraction failed after all retry attempts.  "
            "Observations and triggers will be empty."
        ),
    )

    @model_validator(mode="after")
    def _safe_failure_consistency(self) -> ExtractionResult:
        """When retry_required, observations and triggers must be empty."""
        if self.retry_required:
            if self.observations:
                raise ValueError(
                    "retry_required is True but observations is non-empty.  "
                    "Safe failure must not return partial data."
                )
            if self.proposed_triggers:
                raise ValueError(
                    "retry_required is True but proposed_triggers is non-empty.  "
                    "Safe failure must not return partial data."
                )
        return self
