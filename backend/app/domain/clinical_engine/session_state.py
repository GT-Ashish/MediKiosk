"""
Clinical Session State — Clinical Engine.

Pydantic v2 models for the Phase 7 adaptive clinical history-taking
session state.  This is the in-memory representation of an active
session — it is the single source of truth for what has been asked,
what is known, and what remains.

Design decisions:
    - SlotState does NOT own revision history.
      KNOWN → KNOWN updates the active value; the previous answer is
      preserved in question_history.
    - Interruption metadata is modelled but pause/resume behavior
      is not implemented here.
    - Question budget is structural — no enforcement logic yet.
    - Template version pinning is via CurrentComplaint fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.domain.clinical_engine.enums import ClinicalSessionStatus
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.template_schema import QuestionBudget


# ── Question history ─────────────────────────────────────────────────────────


class QuestionHistoryEntry(BaseModel):
    """
    Record of a single question posed during the session.

    Used to build the audit trail and to preserve previous answers
    when a slot is revised (KNOWN → KNOWN).
    """

    slot_id: str = Field(
        ..., description="ID of the slot this question targeted."
    )
    phrased_text: str = Field(
        ..., description="The question as actually phrased to the patient."
    )
    language: str = Field(
        default="en",
        description="BCP-47 language code used for this question.",
    )
    asked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the question was asked.",
    )
    answer_raw_text: str | None = Field(
        default=None,
        description="Verbatim patient answer, or None if not yet answered.",
    )


# ── Current complaint (template version pinning) ────────────────────────────


class CurrentComplaint(BaseModel):
    """
    Identifies the clinical template and version pinned to this session.

    Once a session starts, it remains pinned to the template version
    that was active at session creation — even if the template is
    updated in the registry later.
    """

    template_id: str = Field(
        ..., description="Template identifier (e.g. 'chest_pain')."
    )
    template_version: str = Field(
        ..., description="Pinned template version (e.g. '1.0.0')."
    )
    terminology_system: str | None = Field(
        default=None, description="Terminology system (e.g. 'SNOMED_CT')."
    )
    terminology_code: str | None = Field(
        default=None, description="Terminology concept code."
    )
    display_name: str | None = Field(
        default=None, description="Human-readable complaint name."
    )


# ── Interruption state ──────────────────────────────────────────────────────


class PauseReason(str, Enum):
    """Reason a clinical session was paused."""

    TIMEOUT = "timeout"
    PATIENT_LEFT = "patient_left"
    EXPLICIT_PAUSE = "explicit_pause"


class InterruptionState(BaseModel):
    """
    Metadata for session pause/resume handling.

    All fields are initially None for a new, uninterrupted session.
    """

    last_active_at: datetime | None = Field(
        default=None,
        description="Last activity timestamp before interruption.",
    )
    resume_token: str | None = Field(
        default=None,
        description="Opaque token used to securely resume the session.",
    )
    pause_reason: PauseReason | None = Field(
        default=None,
        description="Why the session was paused.",
    )
    paused_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the session was paused.",
    )
    resumed_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the session was resumed.",
    )


# ── Clinical session state ──────────────────────────────────────────────────


class ClinicalSessionState(BaseModel):
    """
    Complete in-memory state of an adaptive clinical history-taking session.

    This is the single source of truth for what has been asked, what
    is known, and what remains during a clinical interview.
    """

    session_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this clinical session.",
    )
    patient_ref: str | None = Field(
        default=None,
        description="Anonymised patient reference, if available.",
    )
    language: str = Field(
        default="en",
        description="BCP-47 language code for this session.",
    )
    session_status: ClinicalSessionStatus = Field(
        default=ClinicalSessionStatus.IN_PROGRESS,
        description="Current lifecycle status.",
    )
    current_complaint: CurrentComplaint | None = Field(
        default=None,
        description="Template/version pinned for this session.",
    )
    active_context_modules: list[str] = Field(
        default_factory=list,
        description="IDs of context modules currently activated.",
    )
    slots: dict[str, SlotState] = Field(
        default_factory=dict,
        description="Slot ID → SlotState mapping for all active slots.",
    )
    red_flags: list[str] = Field(
        default_factory=list,
        description="IDs of red-flag rules that have been triggered.",
    )
    question_history: list[QuestionHistoryEntry] = Field(
        default_factory=list,
        description="Ordered audit trail of questions asked.",
    )
    question_count: int = Field(
        default=0,
        ge=0,
        description="Number of questions asked so far.",
    )
    question_budget: QuestionBudget | None = Field(
        default=None,
        description="Min/max question limits copied from the template.",
    )
    interruption: InterruptionState = Field(
        default_factory=InterruptionState,
        description="Pause/resume metadata.",
    )
