"""
MediKiosk Phase 7 — Clinical Engine Domain Layer.

This package implements the adaptive clinical-history engine's domain models,
template system, and state management. It is a pure domain layer with no
database, API, LLM, ASR/TTS, or frontend dependencies.

Architecture principle:
    The clinical engine decides WHAT to ask.
    The LLM decides HOW to ask it.
    The backend state is the single source of truth.

Submodules:
    enums              — Clinical session, slot, and template enumerations
    slot_state         — Slot state machine with deterministic transition rules
    duration           — Duration value model with unit normalization
    template_schema    — Pydantic models for clinical template YAML structure
    session_state      — Clinical conversation state model
    loader             — Generic YAML template loader
    validator          — Structural template validator
    registry           — Template registry/resolver with version pinning
    document_evidence  — Historical document evidence and verification models
    completion_policy  — Question-budget and completion-policy evaluation

Clinical content YAML files live in:
    clinical_engine/content/

This engine does NOT:
    - diagnose
    - recommend treatment
    - generate disease conclusions
    - let the LLM modify state directly
"""

from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    SlotStatus,
    SlotType,
    RedFlagSeverity,
    RedFlagAction,
)
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.duration import DurationValue
from app.domain.clinical_engine.template_schema import (
    TerminologyRef,
    QuestionBudget,
    SlotDefinition,
    TriggerDefinition,
    RedFlagConditionPredicate,
    RedFlagConditionGroup,
    RedFlagDefinition,
    ContextModuleDefinition,
    GeneralHistoryModule,
    ClinicalTemplate,
)
from app.domain.clinical_engine.session_state import (
    QuestionHistoryEntry,
    CurrentComplaint,
    PauseReason,
    InterruptionState,
    ClinicalSessionState,
)
from app.domain.clinical_engine.registry import TemplateRegistry
from app.domain.clinical_engine.document_evidence import (
    EvidenceVerificationStatus,
    EvidenceDurationClass,
    DocumentEvidence,
    HistoricalContextCandidate,
    VerificationTargetStatus,
    VerificationTarget,
)
from app.domain.clinical_engine.question_selector import (
    SelectionAction,
    SelectionResult,
    select_next_action,
)
from app.domain.clinical_engine.completion_policy import (
    CompletionDecision,
    CompletionResult,
    evaluate_completion,
)

__all__ = [
    # Enums
    "ClinicalSessionStatus",
    "SlotStatus",
    "SlotType",
    "RedFlagSeverity",
    "RedFlagAction",
    # Slot state
    "SlotState",
    # Duration
    "DurationValue",
    # Template schema
    "TerminologyRef",
    "QuestionBudget",
    "SlotDefinition",
    "TriggerDefinition",
    "RedFlagConditionPredicate",
    "RedFlagConditionGroup",
    "RedFlagDefinition",
    "ContextModuleDefinition",
    "GeneralHistoryModule",
    "ClinicalTemplate",
    # Session state
    "QuestionHistoryEntry",
    "CurrentComplaint",
    "PauseReason",
    "InterruptionState",
    "ClinicalSessionState",
    # Registry
    "TemplateRegistry",
    # Document evidence
    "EvidenceVerificationStatus",
    "EvidenceDurationClass",
    "DocumentEvidence",
    "HistoricalContextCandidate",
    "VerificationTargetStatus",
    "VerificationTarget",
    # Question selector
    "SelectionAction",
    "SelectionResult",
    "select_next_action",
    # Completion policy
    "CompletionDecision",
    "CompletionResult",
    "evaluate_completion",
]
