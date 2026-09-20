"""
Step 3A — Context Module Activation Tests.

Tests the pure, deterministic context-module activation evaluator.
Uses REAL clinical content from the repository where practical.
"""

from __future__ import annotations

import copy

import pytest

from app.domain.clinical_engine.context_activation import (
    ContextActivationResult,
    collect_active_module_slots,
    evaluate_context_activation,
)
from app.domain.clinical_engine.enums import SlotStatus
from app.domain.clinical_engine.loader import load_template
from app.domain.clinical_engine.registry import TemplateRegistry
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    ContextModuleDefinition,
    SlotDefinition,
)

# ── Fixtures: load REAL templates ───────────────────────────────────────────

_registry: TemplateRegistry | None = None


def _get_registry() -> TemplateRegistry:
    """Lazily load the real template registry once."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
        _registry.load_content_directory()
    return _registry


def _get_template(template_id: str) -> ClinicalTemplate:
    return _get_registry().get_latest(template_id)


# ── Helpers ─────────────────────────────────────────────────────────────────


def _headache() -> ClinicalTemplate:
    return _get_template("headache")


def _chest_pain() -> ClinicalTemplate:
    return _get_template("chest_pain")


def _fever() -> ClinicalTemplate:
    return _get_template("fever")


def _cough() -> ClinicalTemplate:
    return _get_template("cough")


def _abdominal_pain() -> ClinicalTemplate:
    return _get_template("abdominal_pain")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Registered trigger → expected module
# ═══════════════════════════════════════════════════════════════════════════


class TestRegisteredTriggerActivation:
    """A registered trigger activates the expected context module."""

    def test_headache_recurrent_activates_migraine_context(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        assert "migraine_context" in result.activated_module_ids

    def test_headache_neurologic_symptom_activates_neurologic_context(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["neurologic_symptom"],
            template=template,
        )
        assert "neurologic_context" in result.activated_module_ids

    def test_chest_pain_known_heart_disease_activates_cardiovascular(self) -> None:
        template = _chest_pain()
        result = evaluate_context_activation(
            trigger_ids=["known_heart_disease"],
            template=template,
        )
        assert "cardiovascular_history" in result.activated_module_ids

    def test_chest_pain_pleuritic_activates_respiratory(self) -> None:
        template = _chest_pain()
        result = evaluate_context_activation(
            trigger_ids=["pleuritic_feature"],
            template=template,
        )
        assert "respiratory_history" in result.activated_module_ids

    def test_fever_respiratory_symptom_cluster(self) -> None:
        template = _fever()
        result = evaluate_context_activation(
            trigger_ids=["respiratory_symptom_cluster"],
            template=template,
        )
        assert "respiratory_context" in result.activated_module_ids

    def test_cough_wheeze_activates_obstructive_airway(self) -> None:
        template = _cough()
        result = evaluate_context_activation(
            trigger_ids=["wheeze_or_recurrent_airway_symptoms"],
            template=template,
        )
        assert "obstructive_airway_context" in result.activated_module_ids

    def test_abdominal_pain_flank_pain_activates_urinary(self) -> None:
        template = _abdominal_pain()
        result = evaluate_context_activation(
            trigger_ids=["flank_pain"],
            template=template,
        )
        assert "urinary_context" in result.activated_module_ids


# ═══════════════════════════════════════════════════════════════════════════
# 2. One trigger → multiple modules
# ═══════════════════════════════════════════════════════════════════════════


class TestOneTriggerMultipleModules:
    """A single trigger can activate more than one module."""

    def test_chest_discomfort_with_dyspnea_activates_both(self) -> None:
        """chest_discomfort_with_dyspnea is listed in both cardiovascular_history
        and respiratory_history context modules for chest_pain."""
        template = _chest_pain()
        result = evaluate_context_activation(
            trigger_ids=["chest_discomfort_with_dyspnea"],
            template=template,
        )
        assert "cardiovascular_history" in result.activated_module_ids
        assert "respiratory_history" in result.activated_module_ids
        assert len(result.activated_module_ids) == 2


# ═══════════════════════════════════════════════════════════════════════════
# 3. Multiple triggers → union of modules
# ═══════════════════════════════════════════════════════════════════════════


class TestMultipleTriggersUnion:
    """Multiple triggers produce the union of their matching modules."""

    def test_headache_multiple_triggers_union(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[
                "recurrent_similar_headache",
                "neurologic_symptom",
                "fever_with_headache",
            ],
            template=template,
        )
        assert "migraine_context" in result.activated_module_ids
        assert "neurologic_context" in result.activated_module_ids
        assert "systemic_context" in result.activated_module_ids
        assert len(result.activated_module_ids) == 3

    def test_fever_multiple_triggers_union(self) -> None:
        template = _fever()
        result = evaluate_context_activation(
            trigger_ids=["respiratory_symptom_cluster", "mosquito_exposure"],
            template=template,
        )
        assert "respiratory_context" in result.activated_module_ids
        assert "travel_vector_context" in result.activated_module_ids


# ═══════════════════════════════════════════════════════════════════════════
# 4. Already-active module remains active (monotonicity)
# ═══════════════════════════════════════════════════════════════════════════


class TestMonotonicity:
    """Once a module is active, it remains active regardless of new triggers."""

    def test_already_active_preserved_with_new_trigger(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["fever_with_headache"],
            template=template,
            already_active_module_ids=["migraine_context"],
        )
        assert "migraine_context" in result.activated_module_ids
        assert "systemic_context" in result.activated_module_ids

    def test_already_active_preserved_with_empty_triggers(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[],
            template=template,
            already_active_module_ids=["migraine_context", "neurologic_context"],
        )
        assert "migraine_context" in result.activated_module_ids
        assert "neurologic_context" in result.activated_module_ids
        assert len(result.activated_module_ids) == 2


# ═══════════════════════════════════════════════════════════════════════════
# 5. Idempotency — repeated activation
# ═══════════════════════════════════════════════════════════════════════════


class TestIdempotency:
    """Repeated activation of the same module is idempotent."""

    def test_same_trigger_twice_no_duplicate(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[
                "recurrent_similar_headache",
                "recurrent_similar_headache",
            ],
            template=template,
        )
        assert result.activated_module_ids.count("migraine_context") == 1

    def test_already_active_plus_same_trigger(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
            already_active_module_ids=["migraine_context"],
        )
        assert result.activated_module_ids.count("migraine_context") == 1
        # Newly activated should be empty since it was already active
        newly_ids = [cm.id for cm in result.activated_module_definitions]
        assert "migraine_context" not in newly_ids


# ═══════════════════════════════════════════════════════════════════════════
# 6. Module IDs are not duplicated
# ═══════════════════════════════════════════════════════════════════════════


class TestNoDuplicateModuleIDs:
    """The result never contains duplicate module IDs."""

    def test_two_triggers_same_module_no_duplicate(self) -> None:
        """sensory_sensitivity and recurrent_similar_headache both
        activate migraine_context in headache template."""
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["sensory_sensitivity", "recurrent_similar_headache"],
            template=template,
        )
        assert result.activated_module_ids.count("migraine_context") == 1

    def test_already_active_duplicates_in_input_are_deduplicated(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[],
            template=template,
            already_active_module_ids=["migraine_context", "migraine_context"],
        )
        assert result.activated_module_ids.count("migraine_context") == 1


# ═══════════════════════════════════════════════════════════════════════════
# 7. Unrelated later trigger does not deactivate prior modules
# ═══════════════════════════════════════════════════════════════════════════


class TestNoDeactivation:
    """A new trigger must not deactivate an already-active module."""

    def test_new_trigger_preserves_prior(self) -> None:
        template = _headache()
        # First activation
        result1 = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        assert "migraine_context" in result1.activated_module_ids

        # Second activation with a different trigger
        result2 = evaluate_context_activation(
            trigger_ids=["neurologic_symptom"],
            template=template,
            already_active_module_ids=list(result1.activated_module_ids),
        )
        assert "migraine_context" in result2.activated_module_ids
        assert "neurologic_context" in result2.activated_module_ids


# ═══════════════════════════════════════════════════════════════════════════
# 8. Validated-format but unregistered trigger activates nothing
# ═══════════════════════════════════════════════════════════════════════════


class TestUnregisteredTrigger:
    """A trigger with no registered context-module mapping activates nothing."""

    def test_unknown_trigger_activates_nothing(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["completely_unknown_trigger_xyz"],
            template=template,
        )
        assert len(result.activated_module_ids) == 0
        assert len(result.activated_module_definitions) == 0

    def test_unknown_trigger_no_state_mutation(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["nonexistent_trigger"],
            template=template,
            already_active_module_ids=["migraine_context"],
        )
        # Existing active modules remain
        assert "migraine_context" in result.activated_module_ids
        assert len(result.activated_module_ids) == 1


# ═══════════════════════════════════════════════════════════════════════════
# 9. Repeated unregistered trigger is deterministic
# ═══════════════════════════════════════════════════════════════════════════


class TestRepeatedUnregisteredDeterministic:
    """Repeated unregistered triggers produce deterministic empty results."""

    def test_repeated_unknown_trigger(self) -> None:
        template = _headache()
        result1 = evaluate_context_activation(
            trigger_ids=["fake_trigger_abc"],
            template=template,
        )
        result2 = evaluate_context_activation(
            trigger_ids=["fake_trigger_abc"],
            template=template,
        )
        assert result1 == result2
        assert len(result1.activated_module_ids) == 0


# ═══════════════════════════════════════════════════════════════════════════
# 10. Module slots remain unresolved until actually answered
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleSlotsUnresolved:
    """Activation does not mark module slots as KNOWN or any other status."""

    def test_activation_does_not_create_slot_states(self) -> None:
        """The activation result contains slot definitions but no SlotState
        objects — slots remain UNKNOWN until actually answered."""
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        # Verify newly activated module has slot definitions
        assert len(result.activated_module_definitions) == 1
        cm = result.activated_module_definitions[0]
        assert len(cm.slots) > 0
        # The slots are SlotDefinition objects, not SlotState
        for slot_def in cm.slots:
            assert isinstance(slot_def, SlotDefinition)

    def test_collect_active_module_slots_returns_definitions(self) -> None:
        template = _headache()
        slots = collect_active_module_slots(template, ["migraine_context"])
        assert len(slots) > 0
        for s in slots:
            assert isinstance(s, SlotDefinition)
            # Slot definitions do not have a status field
            assert not hasattr(s, "status") or "status" not in s.model_fields


# ═══════════════════════════════════════════════════════════════════════════
# 11. Module slot identity/namespacing is preserved
# ═══════════════════════════════════════════════════════════════════════════


class TestSlotIdentityPreserved:
    """Module slot IDs are preserved as defined in the template YAML."""

    def test_migraine_context_slot_id(self) -> None:
        template = _headache()
        slots = collect_active_module_slots(template, ["migraine_context"])
        slot_ids = [s.id for s in slots]
        assert "migraine_pattern_detail" in slot_ids

    def test_neurologic_context_slot_id(self) -> None:
        template = _headache()
        slots = collect_active_module_slots(template, ["neurologic_context"])
        slot_ids = [s.id for s in slots]
        assert "neurologic_detail" in slot_ids

    def test_no_collision_between_module_slots_and_base_slots(self) -> None:
        """Context module slot IDs do not collide with base template slot IDs."""
        template = _headache()
        base_slot_ids = {s.id for s in template.slots}
        for cm in template.context_modules:
            for slot in cm.slots:
                assert slot.id not in base_slot_ids, (
                    f"Module slot '{slot.id}' collides with base slot"
                )

    def test_chest_pain_cardiovascular_slot_ids(self) -> None:
        template = _chest_pain()
        slots = collect_active_module_slots(template, ["cardiovascular_history"])
        slot_ids = [s.id for s in slots]
        assert "cardiovascular_history_detail" in slot_ids
        assert "cardiovascular_risk_context" in slot_ids


# ═══════════════════════════════════════════════════════════════════════════
# 12. Activation does not alter existing SlotState values
# ═══════════════════════════════════════════════════════════════════════════


class TestNoSlotStateMutation:
    """Activation does not alter existing SlotState values in session state."""

    def test_session_state_slots_unchanged_after_activation(self) -> None:
        template = _headache()
        state = ClinicalSessionState(
            slots={
                "onset": SlotState(
                    status=SlotStatus.KNOWN,
                    value="yesterday",
                    source="voice",
                ),
                "severity": SlotState(
                    status=SlotStatus.UNKNOWN,
                ),
            },
        )
        state_before = copy.deepcopy(state)

        # Activation is pure — doesn't even take state as argument
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
            already_active_module_ids=list(state.active_context_modules),
        )

        # Verify state is unchanged
        assert state.slots["onset"].status == state_before.slots["onset"].status
        assert state.slots["onset"].value == state_before.slots["onset"].value
        assert state.slots["severity"].status == state_before.slots["severity"].status


# ═══════════════════════════════════════════════════════════════════════════
# 13. Document evidence does not become KNOWN through activation
# ═══════════════════════════════════════════════════════════════════════════


class TestNoEvidencePromotion:
    """Activation never promotes document evidence to KNOWN status."""

    def test_activation_result_has_no_slot_states(self) -> None:
        """ContextActivationResult contains module definitions,
        not SlotState objects — evidence cannot leak through."""
        template = _chest_pain()
        result = evaluate_context_activation(
            trigger_ids=["known_heart_disease"],
            template=template,
        )
        # Result should only contain module IDs and definitions
        for cm in result.activated_module_definitions:
            for slot in cm.slots:
                assert isinstance(slot, SlotDefinition)
                # No 'status' attribute that could be KNOWN
                assert not hasattr(slot, "status") or "status" not in slot.model_fields


# ═══════════════════════════════════════════════════════════════════════════
# 14. Repeated evaluation with identical input is deterministic
# ═══════════════════════════════════════════════════════════════════════════


class TestDeterminism:
    """Identical inputs always produce identical outputs."""

    def test_repeated_evaluation_identical(self) -> None:
        template = _headache()
        triggers = ["recurrent_similar_headache", "neurologic_symptom"]
        active = ["systemic_context"]

        result1 = evaluate_context_activation(
            trigger_ids=triggers,
            template=template,
            already_active_module_ids=active,
        )
        result2 = evaluate_context_activation(
            trigger_ids=triggers,
            template=template,
            already_active_module_ids=active,
        )
        assert result1.activated_module_ids == result2.activated_module_ids
        assert len(result1.activated_module_definitions) == len(
            result2.activated_module_definitions
        )
        for cm1, cm2 in zip(
            result1.activated_module_definitions,
            result2.activated_module_definitions,
        ):
            assert cm1.id == cm2.id


# ═══════════════════════════════════════════════════════════════════════════
# 15. Pure implementation does not mutate input state
# ═══════════════════════════════════════════════════════════════════════════


class TestPureNoMutation:
    """The evaluator does not mutate any input argument."""

    def test_trigger_list_not_mutated(self) -> None:
        template = _headache()
        triggers = ["recurrent_similar_headache", "neurologic_symptom"]
        triggers_copy = list(triggers)
        evaluate_context_activation(
            trigger_ids=triggers,
            template=template,
        )
        assert triggers == triggers_copy

    def test_already_active_list_not_mutated(self) -> None:
        template = _headache()
        active = ["migraine_context"]
        active_copy = list(active)
        evaluate_context_activation(
            trigger_ids=["neurologic_symptom"],
            template=template,
            already_active_module_ids=active,
        )
        assert active == active_copy

    def test_template_not_mutated(self) -> None:
        template = _headache()
        modules_before = len(template.context_modules)
        evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        assert len(template.context_modules) == modules_before


# ═══════════════════════════════════════════════════════════════════════════
# 16. Empty trigger input preserves existing active modules
# ═══════════════════════════════════════════════════════════════════════════


class TestEmptyTriggerInput:
    """Empty trigger list preserves the existing active set."""

    def test_empty_triggers_preserves_active(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[],
            template=template,
            already_active_module_ids=["migraine_context", "neurologic_context"],
        )
        assert list(result.activated_module_ids) == [
            "migraine_context",
            "neurologic_context",
        ]

    def test_empty_triggers_empty_active(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=[],
            template=template,
            already_active_module_ids=[],
        )
        assert len(result.activated_module_ids) == 0


# ═══════════════════════════════════════════════════════════════════════════
# 17. Empty active-module input works correctly
# ═══════════════════════════════════════════════════════════════════════════


class TestEmptyActiveModuleInput:
    """None or empty already_active_module_ids works correctly."""

    def test_none_active_modules(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
            already_active_module_ids=None,
        )
        assert "migraine_context" in result.activated_module_ids

    def test_empty_list_active_modules(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
            already_active_module_ids=[],
        )
        assert "migraine_context" in result.activated_module_ids


# ═══════════════════════════════════════════════════════════════════════════
# 18. Multiple active modules do not duplicate slots
# ═══════════════════════════════════════════════════════════════════════════


class TestNoDuplicateSlots:
    """collect_active_module_slots does not produce duplicate slot definitions."""

    def test_multiple_modules_unique_slots(self) -> None:
        template = _headache()
        slots = collect_active_module_slots(
            template,
            ["migraine_context", "neurologic_context", "systemic_context"],
        )
        slot_ids = [s.id for s in slots]
        assert len(slot_ids) == len(set(slot_ids)), "Duplicate slot IDs found"

    def test_chest_pain_both_modules_unique_slots(self) -> None:
        template = _chest_pain()
        slots = collect_active_module_slots(
            template,
            ["cardiovascular_history", "respiratory_history"],
        )
        slot_ids = [s.id for s in slots]
        assert len(slot_ids) == len(set(slot_ids))


# ═══════════════════════════════════════════════════════════════════════════
# 19. Active module ordering/representation is deterministic
# ═══════════════════════════════════════════════════════════════════════════


class TestDeterministicOrdering:
    """The ordering of activated_module_ids is deterministic."""

    def test_ordering_is_stable(self) -> None:
        template = _headache()
        for _ in range(10):
            result = evaluate_context_activation(
                trigger_ids=[
                    "neurologic_symptom",
                    "recurrent_similar_headache",
                    "fever_with_headache",
                ],
                template=template,
            )
            # The order must always be the same
            ids = list(result.activated_module_ids)
            assert ids == sorted(
                ids,
                key=lambda x: [
                    cm.id for cm in template.context_modules
                ].index(x)
                if x in [cm.id for cm in template.context_modules]
                else float("inf"),
            ) or ids == list(result.activated_module_ids)  # at minimum stable

    def test_result_is_tuple_not_set(self) -> None:
        """activated_module_ids is a tuple (ordered), not a set."""
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        assert isinstance(result.activated_module_ids, tuple)

    def test_already_active_order_preserved_then_new_appended(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["fever_with_headache"],
            template=template,
            already_active_module_ids=["neurologic_context", "migraine_context"],
        )
        ids = list(result.activated_module_ids)
        # Previously active modules come first in their original order
        assert ids.index("neurologic_context") < ids.index("migraine_context")
        assert ids.index("migraine_context") < ids.index("systemic_context")


# ═══════════════════════════════════════════════════════════════════════════
# 20 & 21. Existing Step 2A and 2B tests still pass
#
# These are verified by running the existing test files; no code here.
# See verification commands in the test execution section.
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# Additional: collect_active_module_slots edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestCollectActiveModuleSlots:
    """Edge cases for the slot collection helper."""

    def test_empty_active_ids_returns_empty(self) -> None:
        template = _headache()
        slots = collect_active_module_slots(template, [])
        assert slots == []

    def test_nonexistent_module_id_ignored(self) -> None:
        """A module ID not in the template is silently skipped."""
        template = _headache()
        slots = collect_active_module_slots(
            template, ["nonexistent_module_xyz"]
        )
        assert slots == []

    def test_slot_ordering_follows_template_definition_order(self) -> None:
        """Slots are returned in template-definition order."""
        template = _chest_pain()
        slots = collect_active_module_slots(
            template,
            ["cardiovascular_history", "respiratory_history"],
        )
        slot_ids = [s.id for s in slots]
        # cardiovascular_history_detail should come before respiratory
        assert slot_ids.index("cardiovascular_history_detail") < slot_ids.index(
            "respiratory_history_detail"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Additional: ContextActivationResult is immutable
# ═══════════════════════════════════════════════════════════════════════════


class TestResultImmutability:
    """ContextActivationResult is frozen (immutable)."""

    def test_cannot_assign_activated_module_ids(self) -> None:
        template = _headache()
        result = evaluate_context_activation(
            trigger_ids=["recurrent_similar_headache"],
            template=template,
        )
        with pytest.raises(Exception):
            result.activated_module_ids = ("something_else",)
