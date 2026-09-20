"""
Clinical Engine Enumerations.

Defines the finite value sets used throughout the Phase 7 adaptive
clinical-history engine: session lifecycle, slot state machine, slot
data types, red-flag severity levels, and red-flag actions.

These enums are string-backed for JSON serialization compatibility
with the existing Pydantic v2 schema conventions.
"""

from enum import Enum


class ClinicalSessionStatus(str, Enum):
    """Lifecycle states of a clinical history-taking session."""

    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"


class SlotStatus(str, Enum):
    """
    State of a single clinical information slot.

    The slot state machine enforces deterministic transitions —
    see SlotState.transition_to() for allowed moves.
    """

    UNKNOWN = "unknown"
    KNOWN = "known"
    NOT_APPLICABLE = "not_applicable"
    DECLINED = "declined"
    UNCLEAR = "unclear"


class SlotType(str, Enum):
    """Data type of a slot's expected value."""

    TEXT = "text"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    ENUM = "enum"
    DATE = "date"
    DURATION = "duration"


class RedFlagSeverity(str, Enum):
    """Severity classification of a clinical red-flag condition."""

    CRITICAL = "critical"
    HIGH = "high"


class RedFlagAction(str, Enum):
    """Required clinical action when a red-flag condition is triggered."""

    URGENT_CLINICIAN_REVIEW = "urgent_clinician_review"
    PROMPT_CLINICIAN_REVIEW = "prompt_clinician_review"
