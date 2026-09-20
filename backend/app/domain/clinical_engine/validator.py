"""
Clinical Template Validator — Clinical Engine.

Structural and reference validation for clinical templates.
This validator checks that templates are internally consistent and
that cross-references (triggers, red-flag slot references) resolve.

This module does NOT:
    - evaluate red-flag conditions
    - execute triggers
    - perform clinical reasoning
    - use an LLM
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.clinical_engine.enums import SlotType
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    GeneralHistoryModule,
    RedFlagConditionPredicate,
    SlotDefinition,
)


# ── Validation result ────────────────────────────────────────────────────────


@dataclass
class ValidationIssue:
    """A single validation problem found in a template."""

    template_id: str
    field: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.template_id}.{self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Aggregate result of validating one or more templates."""

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    def add(
        self,
        template_id: str,
        field_name: str,
        message: str,
        *,
        severity: str = "error",
    ) -> None:
        self.issues.append(
            ValidationIssue(
                template_id=template_id,
                field=field_name,
                message=message,
                severity=severity,
            )
        )

    def merge(self, other: ValidationResult) -> None:
        self.issues.extend(other.issues)


# ── Slot collection helpers ─────────────────────────────────────────────────


def _collect_all_slot_ids(
    template: ClinicalTemplate,
    general_modules: dict[str, GeneralHistoryModule] | None = None,
) -> tuple[list[str], set[str]]:
    """
    Collect all slot IDs reachable from a template (base + context modules
    + resolved general modules).

    Returns (ordered_ids, unique_ids).
    """
    ordered: list[str] = []
    for slot in template.slots:
        ordered.append(slot.id)
    for cm in template.context_modules:
        for slot in cm.slots:
            ordered.append(slot.id)
    if general_modules:
        for mod_id in template.general_modules:
            mod = general_modules.get(mod_id)
            if mod:
                for slot in mod.slots:
                    ordered.append(slot.id)
    return ordered, set(ordered)


def _collect_all_slots(
    template: ClinicalTemplate,
    general_modules: dict[str, GeneralHistoryModule] | None = None,
) -> list[SlotDefinition]:
    """Collect all SlotDefinition objects reachable from a template."""
    slots: list[SlotDefinition] = list(template.slots)
    for cm in template.context_modules:
        slots.extend(cm.slots)
    if general_modules:
        for mod_id in template.general_modules:
            mod = general_modules.get(mod_id)
            if mod:
                slots.extend(mod.slots)
    return slots


def _build_slot_map(slots: list[SlotDefinition]) -> dict[str, SlotDefinition]:
    """Build a slot_id → SlotDefinition lookup (last wins for duplicates)."""
    return {s.id: s for s in slots}


# ── Template-level validation ───────────────────────────────────────────────


def validate_template(
    template: ClinicalTemplate,
    *,
    trigger_registry: dict[str, list[str]] | None = None,
    general_modules: dict[str, GeneralHistoryModule] | None = None,
) -> ValidationResult:
    """
    Validate a single ClinicalTemplate structurally.

    Checks:
        - version is non-empty
        - terminology is well-formed
        - question budget passes validation (already Pydantic-enforced)
        - no duplicate slot IDs within template + context modules + general modules
        - slot types are valid
        - enum slots have allowed_values
        - numeric slots have valid min/max ranges
        - duration slots with numeric comparison have a declared unit
        - context module trigger references exist in the closed vocabulary
        - red-flag slot references resolve
        - red-flag operators are supported

    Does NOT evaluate conditions or perform clinical reasoning.
    """
    result = ValidationResult()
    tid = template.template_id

    # ── Version ──────────────────────────────────────────────────────────
    if not template.version or not template.version.strip():
        result.add(tid, "version", "Template version must not be empty.")

    # ── Terminology ──────────────────────────────────────────────────────
    if not template.terminology.system.strip():
        result.add(tid, "terminology.system", "Terminology system is empty.")
    if not template.terminology.code.strip():
        result.add(tid, "terminology.code", "Terminology code is empty.")
    if not template.terminology.display.strip():
        result.add(tid, "terminology.display", "Terminology display is empty.")

    # ── Slots ────────────────────────────────────────────────────────────
    ordered_ids, unique_ids = _collect_all_slot_ids(template, general_modules)
    # Duplicate slot ID check
    seen: set[str] = set()
    for sid in ordered_ids:
        if sid in seen:
            result.add(tid, f"slots.{sid}", f"Duplicate slot ID: '{sid}'.")
        seen.add(sid)

    # Per-slot validation
    all_slots = _collect_all_slots(template, general_modules)
    for slot in all_slots:
        _validate_slot(slot, tid, result)

    # ── Context module trigger references ────────────────────────────────
    if trigger_registry is not None:
        # Build closed vocabulary for this template
        registered_trigger_ids: set[str] = set()
        reg_for_template = trigger_registry.get(tid, [])
        registered_trigger_ids.update(reg_for_template)
        # Also include triggers declared inline in the template itself
        for trig in template.triggers:
            registered_trigger_ids.add(trig.id)

        for cm in template.context_modules:
            for trig_ref in cm.triggers:
                if trig_ref not in registered_trigger_ids:
                    result.add(
                        tid,
                        f"context_modules.{cm.id}.triggers",
                        f"Unknown trigger reference: '{trig_ref}'.",
                    )

    # ── Red-flag validation ──────────────────────────────────────────────
    slot_map = _build_slot_map(all_slots)
    for rf in template.red_flags:
        _validate_red_flag(rf, tid, slot_map, result)

    # ── General module references ────────────────────────────────────────
    if general_modules is not None:
        for mod_ref in template.general_modules:
            if mod_ref not in general_modules:
                result.add(
                    tid,
                    "general_modules",
                    f"Referenced general module '{mod_ref}' not found.",
                )

    return result


# ── Slot validation ──────────────────────────────────────────────────────────


def _validate_slot(
    slot: SlotDefinition,
    template_id: str,
    result: ValidationResult,
) -> None:
    """Validate a single SlotDefinition."""

    # Enum slots must have allowed_values
    if slot.type == SlotType.ENUM:
        if not slot.allowed_values:
            result.add(
                template_id,
                f"slots.{slot.id}.allowed_values",
                f"Enum slot '{slot.id}' must define allowed_values.",
            )

    # Numeric range validation
    if slot.min is not None and slot.max is not None:
        if slot.min > slot.max:
            result.add(
                template_id,
                f"slots.{slot.id}.min/max",
                f"Slot '{slot.id}' has min ({slot.min}) > max ({slot.max}).",
            )

    # Duration slots with numeric comparison should have a unit
    if slot.type == SlotType.DURATION:
        if (slot.min is not None or slot.max is not None) and not slot.unit:
            result.add(
                template_id,
                f"slots.{slot.id}.unit",
                f"Duration slot '{slot.id}' with numeric range must declare a unit.",
            )


# ── Red-flag validation ──────────────────────────────────────────────────────


def _validate_red_flag(
    rf: "RedFlagDefinition",
    template_id: str,
    slot_map: dict[str, SlotDefinition],
    result: ValidationResult,
) -> None:
    """Validate a red-flag definition's slot references and operators."""
    from app.domain.clinical_engine.template_schema import RedFlagDefinition

    predicates: list[RedFlagConditionPredicate] = []
    if rf.when.all_of:
        predicates.extend(rf.when.all_of)
    if rf.when.any_of:
        predicates.extend(rf.when.any_of)

    for pred in predicates:
        # Check slot reference exists
        if pred.slot not in slot_map:
            result.add(
                template_id,
                f"red_flags.{rf.id}.when.slot",
                f"Red-flag '{rf.id}' references non-existent slot '{pred.slot}'.",
            )
            continue

        slot_def = slot_map[pred.slot]

        # Structural compatibility checks (no clinical reasoning)
        if pred.gte is not None or pred.lte is not None:
            # Numeric comparisons should target numeric or duration slots
            if slot_def.type not in (
                SlotType.INTEGER,
                SlotType.DECIMAL,
                SlotType.DURATION,
            ):
                result.add(
                    template_id,
                    f"red_flags.{rf.id}.when.{pred.slot}",
                    (
                        f"Numeric operator (gte/lte) on non-numeric slot "
                        f"'{pred.slot}' (type: {slot_def.type.value})."
                    ),
                    severity="warning",
                )

        if pred.contains_any is not None:
            # contains_any should target text slots
            if slot_def.type not in (SlotType.TEXT,):
                result.add(
                    template_id,
                    f"red_flags.{rf.id}.when.{pred.slot}",
                    (
                        f"contains_any operator on non-text slot "
                        f"'{pred.slot}' (type: {slot_def.type.value})."
                    ),
                    severity="warning",
                )


# ── Cross-template validation ───────────────────────────────────────────────


def validate_template_set(
    templates: list[ClinicalTemplate],
    *,
    trigger_registry: dict[str, list[str]] | None = None,
    general_modules: dict[str, GeneralHistoryModule] | None = None,
) -> ValidationResult:
    """
    Validate a collection of templates for cross-cutting issues.

    Checks:
        - No duplicate template_id + version pairs
        - Each template passes individual validation
    """
    result = ValidationResult()

    # Duplicate template_id + version check
    seen_keys: set[tuple[str, str]] = set()
    for tmpl in templates:
        key = (tmpl.template_id, tmpl.version)
        if key in seen_keys:
            result.add(
                tmpl.template_id,
                "template_id/version",
                (
                    f"Duplicate template: '{tmpl.template_id}' "
                    f"version '{tmpl.version}'."
                ),
            )
        seen_keys.add(key)

    # Per-template validation
    for tmpl in templates:
        per_template = validate_template(
            tmpl,
            trigger_registry=trigger_registry,
            general_modules=general_modules,
        )
        result.merge(per_template)

    return result
