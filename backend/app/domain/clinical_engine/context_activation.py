"""
Context Module Activation — Clinical Engine (Step 3A).

Pure, deterministic evaluator that maps validated trigger identifiers
to registered context modules within a clinical template.

Pipeline position:

    validated trigger IDs
            ↓
    registered context module lookup
            ↓
    ContextActivationResult (activated module IDs + module slot definitions)
            ↓
    active slot pool available to Step 2A

Properties:
    - Deterministic: identical inputs always produce identical output.
    - Monotonic: once a module is active, it remains active.
    - Idempotent: repeated activation of the same module has no effect.
    - Pure: does NOT mutate any input model.

This module does NOT:
    - Infer disease, diagnosis, severity, or clinical meaning.
    - Perform keyword matching or natural-language interpretation.
    - Use an LLM.
    - Mutate ClinicalSessionState.
    - Invent modules, triggers, or slot values.
    - Mark module slots as KNOWN.
    - Copy document evidence into module slots.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    ContextModuleDefinition,
    SlotDefinition,
)


# ── Activation result (immutable) ───────────────────────────────────────────


class ContextActivationResult(BaseModel):
    """
    Immutable result of context module activation.

    Contains:
        activated_module_ids — deterministically ordered list of all
            module IDs that should be active after this evaluation
            (union of previously active + newly activated).
        activated_module_definitions — the ContextModuleDefinition
            objects for newly activated modules (not previously active).
    """

    model_config = ConfigDict(frozen=True)

    activated_module_ids: tuple[str, ...] = Field(
        default=(),
        description=(
            "Deterministically ordered tuple of all active context "
            "module IDs (previous + newly activated)."
        ),
    )
    activated_module_definitions: tuple[ContextModuleDefinition, ...] = Field(
        default=(),
        description=(
            "ContextModuleDefinition objects for modules newly "
            "activated in this evaluation."
        ),
    )


# ── Build trigger → module index ────────────────────────────────────────────


def _build_trigger_to_modules(
    template: ClinicalTemplate,
) -> dict[str, list[ContextModuleDefinition]]:
    """
    Build a mapping from trigger_id → list of ContextModuleDefinitions
    that are activated by that trigger.

    Uses only the context_modules defined in the template.
    """
    index: dict[str, list[ContextModuleDefinition]] = {}
    for cm in template.context_modules:
        for trigger_id in cm.triggers:
            index.setdefault(trigger_id, []).append(cm)
    return index


# ── Pure activation evaluator ───────────────────────────────────────────────


def evaluate_context_activation(
    trigger_ids: list[str],
    template: ClinicalTemplate,
    already_active_module_ids: list[str] | None = None,
) -> ContextActivationResult:
    """
    Evaluate which context modules should be active given trigger IDs.

    Args:
        trigger_ids: Validated trigger identifiers to evaluate.
            A trigger that passed input-format validation but has no
            registered context-module mapping activates nothing.
        template: The clinical template containing context_modules
            and their trigger → slot definitions.
        already_active_module_ids: Module IDs already active in
            the current session (monotonicity — these are preserved).

    Returns:
        An immutable ``ContextActivationResult``.

    This function does NOT mutate any input.
    """
    already_active = list(already_active_module_ids or [])

    # Build trigger → module index from the template's context_modules
    trigger_to_modules = _build_trigger_to_modules(template)

    # Start with the already-active set (monotonic: preserve all)
    active_set: set[str] = set(already_active)
    newly_activated: list[ContextModuleDefinition] = []

    # For each trigger, find registered modules and activate them
    for trigger_id in trigger_ids:
        matching_modules = trigger_to_modules.get(trigger_id, [])
        for cm in matching_modules:
            if cm.id not in active_set:
                active_set.add(cm.id)
                newly_activated.append(cm)

    # Build the deterministically ordered final list:
    # preserve insertion order of already_active, then append newly
    # activated in the order they were discovered (deduplicated).
    ordered_ids: list[str] = []
    seen: set[str] = set()
    for mid in already_active:
        if mid not in seen:
            ordered_ids.append(mid)
            seen.add(mid)
    for cm in newly_activated:
        if cm.id not in seen:
            ordered_ids.append(cm.id)
            seen.add(cm.id)

    return ContextActivationResult(
        activated_module_ids=tuple(ordered_ids),
        activated_module_definitions=tuple(newly_activated),
    )


# ── Slot collection helper ─────────────────────────────────────────────────


def collect_active_module_slots(
    template: ClinicalTemplate,
    active_module_ids: list[str] | tuple[str, ...],
) -> list[SlotDefinition]:
    """
    Collect slot definitions from active context modules.

    Returns a list of SlotDefinition objects from context modules
    whose IDs are in ``active_module_ids``.  Slot identity is
    preserved as-is from the template — no renaming or namespacing
    is applied because the template YAML already uses globally unique
    slot IDs within each template (enforced by the validator's
    duplicate-slot-ID check).

    The returned slots are ordered deterministically:
    modules in the order they appear in the template's context_modules
    list, slots within each module in their defined order.

    This function does NOT mutate any input.
    """
    active_set = set(active_module_ids)
    result: list[SlotDefinition] = []
    for cm in template.context_modules:
        if cm.id in active_set:
            result.extend(cm.slots)
    return result
