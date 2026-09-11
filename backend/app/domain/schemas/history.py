"""
ClinicalHistory and HistoryAnswer — Domain Schemas.

ClinicalHistory represents the structured clinical information collected
during a MediKiosk patient session. It follows the SOCRATES mnemonic
(Site, Onset, Character, Radiation, Associated symptoms, Time/duration,
Exacerbating/relieving factors, Severity) plus standard medical history axes.

HistoryAnswer represents a single question-answer exchange from the
kiosk conversation engine. Answers are collected throughout the session
and used to build the ClinicalHistory.

AI Boundary — CRITICAL:
    The clinical workflow (conversation engine / state machine) is responsible
    for determining what questions to ask and what information is required.
    The LLM assists with:
        - Natural language understanding of patient responses
        - Conversational phrasing of follow-up questions
        - Entity extraction from free-text answers
        - Summarisation of the collected history

    The LLM does NOT:
        - Decide which clinical fields are required (the schema does this)
        - Diagnose the patient
        - Make autonomous clinical decisions
        - Replace physician review

    All history that involves LLM processing must be marked appropriately
    and included in the StructuredHistorySummary which requires physician review.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnswerSource(str, Enum):
    """
    How the patient's answer was captured.

    VOICE     — Transcribed from speech (ASR)
    TEXT      — Typed by the patient via fallback keyboard
    DOCUMENT  — Extracted from an uploaded medical document
    """

    VOICE = "voice"
    TEXT = "text"
    DOCUMENT = "document"


class HistoryAnswer(BaseModel):
    """
    A single question-answer exchange from the kiosk conversation.

    Stores both the question asked and the patient's answer, along with
    metadata about how the answer was captured and its confidence level.
    """

    question_id: str = Field(
        description="Identifier for the clinical question (e.g., 'onset', 'severity', 'location').",
    )
    question_text: str = Field(
        description="The exact question text presented to the patient.",
    )
    answer_text: str = Field(
        description="The patient's answer, verbatim or transcribed.",
    )
    answer_source: AnswerSource = Field(
        description="How this answer was captured.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score for this answer (0.0–1.0). "
            "None for manual text entry (confidence is implicitly 1.0). "
            "Set by ASR or extraction models for VOICE and DOCUMENT answers."
        ),
    )
    answered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this answer was recorded.",
    )


class ClinicalHistory(BaseModel):
    """
    Structured clinical history following SOCRATES + standard medical axes.

    This is the primary clinical data contract of the MediKiosk system.
    It is progressively populated during the conversation and then sent
    to the LLM for narrative summarisation.

    All fields except chief_complaint and session_id are optional because
    clinical history is built incrementally through conversation — not every
    patient will answer every question, and not every question is relevant
    to every chief complaint.

    The answers list preserves the raw Q&A log for audit purposes.
    """

    history_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this clinical history record.",
    )
    session_id: uuid.UUID = Field(
        description="The kiosk session this history belongs to.",
    )

    # ── SOCRATES ──────────────────────────────────────────────────────────────
    chief_complaint: str = Field(
        description="The patient's primary complaint in their own words.",
    )
    onset: str | None = Field(
        default=None,
        description="When did the complaint start? (e.g., 'yesterday', '3 days ago', 'sudden')",
    )
    duration: str | None = Field(
        default=None,
        description="How long has the complaint been present? (e.g., '2 hours', 'a week')",
    )
    location: str | None = Field(
        default=None,
        description="Where is the symptom located? (e.g., 'chest', 'left knee')",
    )
    character: str | None = Field(
        default=None,
        description="What is the nature of the symptom? (e.g., 'burning', 'sharp', 'dull ache')",
    )
    severity: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Severity on a 1–10 scale (1 = minimal, 10 = worst imaginable).",
    )
    radiation: str | None = Field(
        default=None,
        description="Does the symptom radiate anywhere? (e.g., 'radiates to the left arm')",
    )
    relieving_factors: list[str] = Field(
        default_factory=list,
        description="What makes the symptom better? (e.g., ['rest', 'antacids'])",
    )
    aggravating_factors: list[str] = Field(
        default_factory=list,
        description="What makes the symptom worse? (e.g., ['walking', 'eating'])",
    )
    associated_symptoms: list[str] = Field(
        default_factory=list,
        description="Other symptoms the patient reports alongside the chief complaint.",
    )

    # ── Standard Medical History Axes ─────────────────────────────────────────
    medications: list[str] = Field(
        default_factory=list,
        description="Current medications reported by the patient.",
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="Known allergies reported by the patient.",
    )
    past_medical_history: list[str] = Field(
        default_factory=list,
        description="Relevant past medical conditions (e.g., ['Hypertension', 'T2DM']).",
    )
    family_history: list[str] = Field(
        default_factory=list,
        description="Relevant family medical history.",
    )
    social_history: str | None = Field(
        default=None,
        description="Brief social history (e.g., smoking, alcohol, occupation — as reported by patient).",
    )
    review_of_systems: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "System-by-system review findings. "
            "Keys are system names (e.g., 'cardiovascular', 'respiratory'), "
            "values are brief findings (e.g., 'no chest pain', 'occasional cough')."
        ),
    )

    # ── Clinical Safety ────────────────────────────────────────────────────────
    red_flags: list[str] = Field(
        default_factory=list,
        description=(
            "Clinical red flags identified during history collection. "
            "These are surfaced prominently in the doctor review summary. "
            "Examples: 'sudden severe headache', 'unexplained weight loss', "
            "'chest pain with radiation to arm'."
        ),
    )

    # ── Audit Trail ────────────────────────────────────────────────────────────
    answers: list[HistoryAnswer] = Field(
        default_factory=list,
        description=(
            "Raw Q&A log from the kiosk conversation. "
            "Preserved for audit, consent verification, and AI reprocessing."
        ),
    )

    @field_validator("severity")
    @classmethod
    def severity_must_be_in_range(cls, v: int | None) -> int | None:
        """Enforce severity is 1–10 or None."""
        if v is not None and not (1 <= v <= 10):
            raise ValueError("severity must be between 1 and 10")
        return v
