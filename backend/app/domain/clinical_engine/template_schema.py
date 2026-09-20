"""
Clinical Template Schema — Clinical Engine.

Pydantic v2 models that represent the structure of the Phase 7 Clinical
Content Pack v1.1 YAML files.  These models are used by the loader
(Step 1C) to parse and validate YAML templates at startup.

Design decisions:
    - Models mirror the ACTUAL YAML structure in content/templates/.
    - Optional fields remain optional when the content pack omits them.
    - Red-flag conditions are structurally represented but NOT evaluated.
    - GeneralHistoryModule is a reusable module, not a full ClinicalTemplate.
    - ``notes`` is accepted when present but is not required.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.domain.clinical_engine.enums import (
    RedFlagAction,
    RedFlagSeverity,
    SlotType,
)


# ── Terminology ───────────────────────────────────────────────────────────────


class TerminologyRef(BaseModel):
    """ICD/SNOMED-CT reference for a complaint template."""

    system: str = Field(
        ..., description="Terminology system (e.g. 'SNOMED_CT')."
    )
    code: str = Field(
        ..., description="Concept code within the terminology system."
    )
    display: str = Field(
        ..., description="Human-readable display name."
    )


# ── Question budget ──────────────────────────────────────────────────────────


class QuestionBudget(BaseModel):
    """
    Minimum and maximum question counts for a clinical template.

    Validation enforces:
        - both values are positive integers
        - min_questions ≤ max_questions
    """

    min_questions: int = Field(
        ..., gt=0, description="Minimum questions to ask."
    )
    max_questions: int = Field(
        ..., gt=0, description="Maximum questions to ask."
    )

    @model_validator(mode="after")
    def _min_le_max(self) -> QuestionBudget:
        if self.min_questions > self.max_questions:
            raise ValueError(
                f"min_questions ({self.min_questions}) must be "
                f"≤ max_questions ({self.max_questions})"
            )
        return self


# ── Slot definition ──────────────────────────────────────────────────────────


class SlotDefinition(BaseModel):
    """
    Definition of a single clinical information slot within a template.

    Optional fields (allowed_values, min, max, unit, examples) are only
    present for certain slot types in the content pack.
    """

    id: str = Field(..., description="Unique slot identifier within the template.")
    type: SlotType = Field(..., description="Expected value data type.")
    required: bool = Field(
        default=False, description="Whether this slot must be filled."
    )
    priority: int = Field(
        default=50, description="Questioning priority (lower = earlier)."
    )
    description: str = Field(
        default="", description="Clinical description of the information."
    )
    allowed_values: list[str] | None = Field(
        default=None,
        description="Closed value set for enum-type slots.",
    )
    min: float | None = Field(
        default=None,
        description="Minimum value for numeric/duration slots.",
    )
    max: float | None = Field(
        default=None,
        description="Maximum value for numeric/duration slots.",
    )
    unit: str | None = Field(
        default=None,
        description="Canonical unit for duration/numeric slots.",
    )
    examples: list[str] | None = Field(
        default=None, description="Example values for guidance."
    )


# ── Trigger definition ──────────────────────────────────────────────────────


class TriggerDefinition(BaseModel):
    """A trigger that can activate a context module."""

    id: str = Field(..., description="Unique trigger identifier.")
    description: str = Field(
        default="", description="What this trigger represents."
    )


# ── Context module definition ───────────────────────────────────────────────


class ContextModuleDefinition(BaseModel):
    """
    A conditional group of slots activated when specific triggers fire.
    """

    id: str = Field(..., description="Context module identifier.")
    triggers: list[str] = Field(
        default_factory=list,
        description="Trigger IDs that activate this module.",
    )
    slots: list[SlotDefinition] = Field(
        default_factory=list,
        description="Additional slots added when this module is active.",
    )


# ── Red-flag condition structures ────────────────────────────────────────────
#
# The YAML structure for red-flag ``when`` clauses uses:
#     all_of / any_of  →  list of predicates
#     Each predicate references a slot and applies ONE operator:
#         equals, gte, lte, contains_any, not_empty
#
# These models represent the structure for parsing/validation.
# They do NOT evaluate conditions — that belongs to the red-flag evaluator.


class RedFlagConditionPredicate(BaseModel):
    """
    A single condition predicate referencing a slot value.

    Exactly one operator field should be set.  This is validated
    structurally — the evaluator (a later step) applies the logic.
    """

    slot: str = Field(..., description="Slot ID to evaluate.")
    equals: Any | None = Field(
        default=None, description="Slot value must equal this."
    )
    gte: float | None = Field(
        default=None, description="Slot value must be ≥ this."
    )
    lte: float | None = Field(
        default=None, description="Slot value must be ≤ this."
    )
    contains_any: list[str] | None = Field(
        default=None, description="Slot text must contain any of these."
    )
    not_empty: bool | None = Field(
        default=None, description="Slot value must be non-empty."
    )

    @model_validator(mode="after")
    def _at_least_one_operator(self) -> RedFlagConditionPredicate:
        """At least one operator must be specified."""
        operators = [
            self.equals is not None,
            self.gte is not None,
            self.lte is not None,
            self.contains_any is not None,
            self.not_empty is not None,
        ]
        if not any(operators):
            raise ValueError(
                f"Red-flag predicate for slot {self.slot!r} must specify "
                f"at least one operator (equals, gte, lte, contains_any, not_empty)."
            )
        return self


class RedFlagConditionGroup(BaseModel):
    """
    A group of condition predicates combined with all_of or any_of.

    Exactly one of ``all_of`` or ``any_of`` must be set.
    """

    all_of: list[RedFlagConditionPredicate] | None = Field(
        default=None, description="All predicates must match."
    )
    any_of: list[RedFlagConditionPredicate] | None = Field(
        default=None, description="At least one predicate must match."
    )

    @model_validator(mode="after")
    def _exactly_one_group(self) -> RedFlagConditionGroup:
        has_all = self.all_of is not None
        has_any = self.any_of is not None
        if has_all == has_any:
            raise ValueError(
                "Exactly one of 'all_of' or 'any_of' must be specified "
                "in a red-flag condition group."
            )
        return self


# ── Red-flag definition ─────────────────────────────────────────────────────


class RedFlagDefinition(BaseModel):
    """A clinical red-flag rule — parsed but NOT evaluated at this layer."""

    id: str = Field(..., description="Unique red-flag identifier.")
    severity: RedFlagSeverity = Field(
        ..., description="Severity classification."
    )
    when: RedFlagConditionGroup = Field(
        ..., description="Condition group that triggers this red flag."
    )
    action: RedFlagAction = Field(
        ..., description="Required clinical action when triggered."
    )


# ── General history module ──────────────────────────────────────────────────


class GeneralHistoryModule(BaseModel):
    """
    Reusable general-history module.

    This is NOT a full ClinicalTemplate — it has no terminology or
    question_budget.  It provides reusable slots that are merged into
    complaint templates by the registry/resolver.
    """

    template_id: str = Field(
        ..., description="Module identifier (e.g. 'general_history')."
    )
    version: str = Field(
        default="1.0.0", description="Module version."
    )
    status: str = Field(
        default="demo_non_production",
        description="Module lifecycle status.",
    )
    slots: list[SlotDefinition] = Field(
        default_factory=list,
        description="Reusable slot definitions provided by this module.",
    )


# ── Clinical template ───────────────────────────────────────────────────────


class ClinicalTemplate(BaseModel):
    """
    A complete clinical complaint template parsed from YAML.

    Represents the full structure of a complaint-specific template
    (e.g. chest_pain, fever, headache).  Includes terminology, budget,
    slots, context modules, triggers, and red-flag rules.
    """

    template_id: str = Field(
        ..., description="Unique template identifier."
    )
    version: str = Field(
        ..., description="Semantic version string."
    )
    status: str = Field(
        default="demo_non_production",
        description="Template lifecycle status.",
    )
    terminology: TerminologyRef = Field(
        ..., description="Clinical terminology reference."
    )
    question_budget: QuestionBudget = Field(
        ..., description="Question count limits."
    )
    general_modules: list[str] = Field(
        default_factory=list,
        description="IDs of reusable modules to merge (e.g. 'general_history').",
    )
    slots: list[SlotDefinition] = Field(
        default_factory=list,
        description="Template-specific slot definitions.",
    )
    context_modules: list[ContextModuleDefinition] = Field(
        default_factory=list,
        description="Conditional slot groups activated by triggers.",
    )
    triggers: list[TriggerDefinition] = Field(
        default_factory=list,
        description="Trigger definitions for this template.",
    )
    red_flags: list[RedFlagDefinition] = Field(
        default_factory=list,
        description="Red-flag rules (parsed, not evaluated).",
    )
    notes: str | None = Field(
        default=None,
        description="Optional template-level notes.",
    )
