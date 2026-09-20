"""
Step 3B — Deterministic Red-Flag Evaluator Tests.

Tests the pure, deterministic red-flag evaluator against structured
clinical slot state. Uses REAL red-flag YAML content where practical.
"""

from __future__ import annotations

import copy

import pytest

from app.domain.clinical_engine.duration import DurationValue
from app.domain.clinical_engine.enums import (
    RedFlagAction,
    RedFlagSeverity,
    SlotStatus,
)
from app.domain.clinical_engine.red_flag_evaluator import (
    RedFlagEvaluationResult,
    RedFlagMatch,
    evaluate_red_flags,
)
from app.domain.clinical_engine.registry import TemplateRegistry
from app.domain.clinical_engine.session_state import ClinicalSessionState
from app.domain.clinical_engine.slot_state import SlotState
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    RedFlagConditionGroup,
    RedFlagConditionPredicate,
    RedFlagDefinition,
)


# ── Fixture: load REAL templates ───────────────────────────────────────────

_registry: TemplateRegistry | None = None


def _get_registry() -> TemplateRegistry:
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
        _registry.load_content_directory()
    return _registry


def _get_template(template_id: str) -> ClinicalTemplate:
    return _get_registry().get_latest(template_id)


# ── Helpers ─────────────────────────────────────────────────────────────────


def _make_state(**known_slots: object) -> ClinicalSessionState:
    """Build a session state with the given slots set to KNOWN."""
    slots = {}
    for slot_id, value in known_slots.items():
        slots[slot_id] = SlotState(status=SlotStatus.KNOWN, value=value)
    return ClinicalSessionState(slots=slots)


def _make_rf(
    rf_id: str,
    *,
    severity: RedFlagSeverity = RedFlagSeverity.CRITICAL,
    action: RedFlagAction = RedFlagAction.URGENT_CLINICIAN_REVIEW,
    all_of: list[RedFlagConditionPredicate] | None = None,
    any_of: list[RedFlagConditionPredicate] | None = None,
) -> RedFlagDefinition:
    """Build a synthetic red-flag definition for isolated tests."""
    if all_of is not None:
        group = RedFlagConditionGroup(all_of=all_of)
    elif any_of is not None:
        group = RedFlagConditionGroup(any_of=any_of)
    else:
        raise ValueError("Must provide all_of or any_of")
    return RedFlagDefinition(
        id=rf_id, severity=severity, when=group, action=action,
    )


def _pred_equals(slot: str, value: object) -> RedFlagConditionPredicate:
    return RedFlagConditionPredicate(slot=slot, equals=value)


def _pred_gte(slot: str, value: float) -> RedFlagConditionPredicate:
    return RedFlagConditionPredicate(slot=slot, gte=value)


def _pred_lte(slot: str, value: float) -> RedFlagConditionPredicate:
    return RedFlagConditionPredicate(slot=slot, lte=value)


def _pred_contains_any(
    slot: str, keywords: list[str],
) -> RedFlagConditionPredicate:
    return RedFlagConditionPredicate(slot=slot, contains_any=keywords)


def _pred_not_empty(slot: str) -> RedFlagConditionPredicate:
    return RedFlagConditionPredicate(slot=slot, not_empty=True)


# ═══════════════════════════════════════════════════════════════════════════
# 1. No red flags → no matches
# ═══════════════════════════════════════════════════════════════════════════


class TestNoRedFlags:
    def test_no_rules_no_matches(self) -> None:
        state = _make_state(onset="yesterday")
        result = evaluate_red_flags(state, [])
        assert not result.has_matches
        assert result.matched == ()

    def test_no_slots_no_matches(self) -> None:
        state = ClinicalSessionState()
        rf = _make_rf("test_rf", all_of=[_pred_equals("some_slot", True)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 2. Single positive red flag → exactly that match
# ═══════════════════════════════════════════════════════════════════════════


class TestSinglePositiveMatch:
    def test_equals_true_match(self) -> None:
        state = _make_state(hemoptysis=True)
        rf = _make_rf("coughing_blood", all_of=[_pred_equals("hemoptysis", True)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches
        assert len(result.matched) == 1
        assert result.matched[0].red_flag_id == "coughing_blood"

    def test_real_chest_pain_with_breathing_difficulty(self) -> None:
        """Use REAL chest_pain template red flag."""
        template = _get_template("chest_pain")
        state = _make_state(associated_shortness_of_breath=True)
        result = evaluate_red_flags(state, template.red_flags)
        assert "chest_pain_with_breathing_difficulty" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 3. Single negative red flag → no match
# ═══════════════════════════════════════════════════════════════════════════


class TestSingleNegativeNoMatch:
    def test_equals_false_no_match(self) -> None:
        state = _make_state(hemoptysis=False)
        rf = _make_rf("coughing_blood", all_of=[_pred_equals("hemoptysis", True)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_real_chest_pain_no_breathing_issue(self) -> None:
        template = _get_template("chest_pain")
        state = _make_state(associated_shortness_of_breath=False)
        result = evaluate_red_flags(state, template.red_flags)
        assert "chest_pain_with_breathing_difficulty" not in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 4. ALL_OF with every child true → match
# ═══════════════════════════════════════════════════════════════════════════


class TestAllOfAllTrue:
    def test_two_predicates_both_true(self) -> None:
        state = _make_state(slot_a=True, slot_b=True)
        rf = _make_rf("both_true", all_of=[
            _pred_equals("slot_a", True),
            _pred_equals("slot_b", True),
        ])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_real_headache_fever_any_of_match(self) -> None:
        """headache_with_fever_or_neck_stiffness uses any_of."""
        template = _get_template("headache")
        state = _make_state(fever_present=True)
        result = evaluate_red_flags(state, template.red_flags)
        assert "headache_with_fever_or_neck_stiffness" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 5. ALL_OF with one child false → no match
# ═══════════════════════════════════════════════════════════════════════════


class TestAllOfOneFalse:
    def test_two_predicates_one_false(self) -> None:
        state = _make_state(slot_a=True, slot_b=False)
        rf = _make_rf("both_true", all_of=[
            _pred_equals("slot_a", True),
            _pred_equals("slot_b", True),
        ])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 6. ANY_OF with one child true → match
# ═══════════════════════════════════════════════════════════════════════════


class TestAnyOfOneTrue:
    def test_any_of_one_true_matches(self) -> None:
        state = _make_state(slot_a=False, slot_b=True)
        rf = _make_rf("any_match", any_of=[
            _pred_equals("slot_a", True),
            _pred_equals("slot_b", True),
        ])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_real_headache_fever_or_stiffness_one_matches(self) -> None:
        """headache_with_fever_or_neck_stiffness: any_of fever_present
        or neck_stiffness_present."""
        template = _get_template("headache")
        state = _make_state(neck_stiffness_present=True, fever_present=False)
        result = evaluate_red_flags(state, template.red_flags)
        assert "headache_with_fever_or_neck_stiffness" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 7. ANY_OF with all children false → no match
# ═══════════════════════════════════════════════════════════════════════════


class TestAnyOfAllFalse:
    def test_any_of_all_false_no_match(self) -> None:
        state = _make_state(slot_a=False, slot_b=False)
        rf = _make_rf("any_match", any_of=[
            _pred_equals("slot_a", True),
            _pred_equals("slot_b", True),
        ])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_real_headache_neither_fever_nor_stiffness(self) -> None:
        template = _get_template("headache")
        state = _make_state(fever_present=False, neck_stiffness_present=False)
        result = evaluate_red_flags(state, template.red_flags)
        assert "headache_with_fever_or_neck_stiffness" not in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 8. UNKNOWN slot does not satisfy positive equality condition
# ═══════════════════════════════════════════════════════════════════════════


class TestUnknownSlotSafety:
    def test_unknown_slot_does_not_match_equals_true(self) -> None:
        state = ClinicalSessionState(
            slots={
                "hemoptysis": SlotState(status=SlotStatus.UNKNOWN),
            },
        )
        rf = _make_rf("rf1", all_of=[_pred_equals("hemoptysis", True)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_unclear_slot_does_not_match(self) -> None:
        state = ClinicalSessionState(
            slots={
                "hemoptysis": SlotState(status=SlotStatus.UNCLEAR),
            },
        )
        rf = _make_rf("rf1", all_of=[_pred_equals("hemoptysis", True)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 9. Missing slot does not satisfy positive equality condition
# ═══════════════════════════════════════════════════════════════════════════


class TestMissingSlotSafety:
    def test_slot_absent_does_not_match(self) -> None:
        state = ClinicalSessionState(slots={})
        rf = _make_rf("rf1", all_of=[_pred_equals("nonexistent_slot", True)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_missing_slot_does_not_match_not_empty(self) -> None:
        state = ClinicalSessionState(slots={})
        rf = _make_rf("rf1", all_of=[_pred_not_empty("nonexistent_slot")])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 10. not_empty only matches an actually populated value
# ═══════════════════════════════════════════════════════════════════════════


class TestNotEmpty:
    def test_not_empty_with_text(self) -> None:
        state = _make_state(trauma_history="fell down stairs")
        rf = _make_rf("rf1", all_of=[_pred_not_empty("trauma_history")])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_not_empty_with_empty_string(self) -> None:
        state = _make_state(trauma_history="")
        rf = _make_rf("rf1", all_of=[_pred_not_empty("trauma_history")])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_not_empty_with_whitespace_only(self) -> None:
        state = _make_state(trauma_history="   ")
        rf = _make_rf("rf1", all_of=[_pred_not_empty("trauma_history")])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_real_headache_trauma_not_empty(self) -> None:
        """headache_after_head_trauma uses not_empty on trauma_history."""
        template = _get_template("headache")
        state = _make_state(trauma_history="hit head on door")
        result = evaluate_red_flags(state, template.red_flags)
        assert "headache_after_head_trauma" in result.matched_ids

    def test_real_headache_trauma_empty_no_match(self) -> None:
        template = _get_template("headache")
        state = _make_state(trauma_history="")
        result = evaluate_red_flags(state, template.red_flags)
        assert "headache_after_head_trauma" not in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 11. Numeric gte works
# ═══════════════════════════════════════════════════════════════════════════


class TestGte:
    def test_gte_match(self) -> None:
        state = _make_state(severity=9)
        rf = _make_rf("severe", all_of=[_pred_gte("severity", 8)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_gte_exact_boundary(self) -> None:
        state = _make_state(severity=8)
        rf = _make_rf("severe", all_of=[_pred_gte("severity", 8)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_gte_below_no_match(self) -> None:
        state = _make_state(severity=7)
        rf = _make_rf("severe", all_of=[_pred_gte("severity", 8)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_real_chest_pain_severe(self) -> None:
        """severe_chest_pain: severity gte 8."""
        template = _get_template("chest_pain")
        state = _make_state(severity=9)
        result = evaluate_red_flags(state, template.red_flags)
        assert "severe_chest_pain" in result.matched_ids

    def test_real_abdominal_pain_severe(self) -> None:
        """severe_abdominal_pain: severity gte 8."""
        template = _get_template("abdominal_pain")
        state = _make_state(severity=8)
        result = evaluate_red_flags(state, template.red_flags)
        assert "severe_abdominal_pain" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 12. Numeric lte works
# ═══════════════════════════════════════════════════════════════════════════


class TestLte:
    def test_lte_match(self) -> None:
        state = _make_state(time_to_peak=3)
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_lte_exact_boundary(self) -> None:
        state = _make_state(time_to_peak=5)
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_lte_above_no_match(self) -> None:
        state = _make_state(time_to_peak=6)
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_real_headache_thunderclap(self) -> None:
        """thunderclap_headache: time_to_peak lte 5 (minutes)."""
        template = _get_template("headache")
        state = _make_state(time_to_peak=3)
        result = evaluate_red_flags(state, template.red_flags)
        assert "thunderclap_headache" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 13. Duration comparison via DurationValue
# ═══════════════════════════════════════════════════════════════════════════


class TestDurationComparison:
    def test_duration_value_lte_match(self) -> None:
        """DurationValue.numeric_value is used for numeric comparison."""
        dv = DurationValue(numeric_value=3.0, unit="minutes")
        state = _make_state(time_to_peak=dv)
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches

    def test_duration_value_lte_no_match(self) -> None:
        dv = DurationValue(numeric_value=10.0, unit="minutes")
        state = _make_state(time_to_peak=dv)
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_duration_dict_form(self) -> None:
        """DurationValue stored as dict (e.g. from JSON roundtrip)."""
        state = _make_state(
            time_to_peak={"numeric_value": 2.5, "unit": "minutes"},
        )
        rf = _make_rf("thunderclap", all_of=[_pred_lte("time_to_peak", 5)])
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 14. Multiple simultaneous red flags are all returned
# ═══════════════════════════════════════════════════════════════════════════


class TestMultipleMatches:
    def test_two_flags_both_match(self) -> None:
        state = _make_state(hemoptysis=True, shortness_of_breath=True)
        template = _get_template("cough")
        result = evaluate_red_flags(state, template.red_flags)
        assert "coughing_blood" in result.matched_ids
        assert "cough_with_breathing_difficulty" in result.matched_ids
        assert len(result.matched) >= 2

    def test_real_headache_multiple_flags(self) -> None:
        """Multiple headache red flags triggered simultaneously."""
        template = _get_template("headache")
        state = _make_state(
            time_to_peak=2,
            new_neurologic_deficit_present=True,
            fever_present=True,
        )
        result = evaluate_red_flags(state, template.red_flags)
        assert "thunderclap_headache" in result.matched_ids
        assert "headache_with_new_neurologic_symptoms" in result.matched_ids
        assert "headache_with_fever_or_neck_stiffness" in result.matched_ids
        assert len(result.matched) >= 3


# ═══════════════════════════════════════════════════════════════════════════
# 15. Duplicate rule evaluation does not duplicate matches
# ═══════════════════════════════════════════════════════════════════════════


class TestNoDuplicateMatches:
    def test_duplicate_rule_id_deduplicated(self) -> None:
        state = _make_state(hemoptysis=True)
        rf = _make_rf("rf1", all_of=[_pred_equals("hemoptysis", True)])
        # Pass same rule twice
        result = evaluate_red_flags(state, [rf, rf])
        assert len(result.matched) == 1


# ═══════════════════════════════════════════════════════════════════════════
# 16. Repeated evaluation of identical state is deterministic
# ═══════════════════════════════════════════════════════════════════════════


class TestDeterminism:
    def test_repeated_evaluation_identical(self) -> None:
        template = _get_template("chest_pain")
        state = _make_state(
            associated_shortness_of_breath=True,
            severity=9,
        )
        r1 = evaluate_red_flags(state, template.red_flags)
        r2 = evaluate_red_flags(state, template.red_flags)
        assert r1.matched_ids == r2.matched_ids
        assert len(r1.matched) == len(r2.matched)

    def test_deterministic_ordering(self) -> None:
        """Matches follow template definition order."""
        template = _get_template("cough")
        state = _make_state(hemoptysis=True, shortness_of_breath=True, chest_pain=True)
        results = [evaluate_red_flags(state, template.red_flags) for _ in range(10)]
        for r in results:
            assert r.matched_ids == results[0].matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 17. Changing state changes evaluation appropriately
# ═══════════════════════════════════════════════════════════════════════════


class TestStateChangeAffectsResult:
    def test_adding_known_slot_triggers_flag(self) -> None:
        template = _get_template("cough")
        # Initially no hemoptysis
        state1 = _make_state(hemoptysis=False)
        r1 = evaluate_red_flags(state1, template.red_flags)
        assert "coughing_blood" not in r1.matched_ids

        # Now hemoptysis is True
        state2 = _make_state(hemoptysis=True)
        r2 = evaluate_red_flags(state2, template.red_flags)
        assert "coughing_blood" in r2.matched_ids

    def test_removing_slot_clears_flag(self) -> None:
        """Re-evaluation with different state produces different result."""
        rf = _make_rf("rf1", all_of=[_pred_equals("x", True)])
        state_with = _make_state(x=True)
        state_without = ClinicalSessionState(slots={})
        r1 = evaluate_red_flags(state_with, [rf])
        r2 = evaluate_red_flags(state_without, [rf])
        assert r1.has_matches
        assert not r2.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 18. Evaluator does not mutate session state
# ═══════════════════════════════════════════════════════════════════════════


class TestNoSessionMutation:
    def test_session_state_unchanged(self) -> None:
        template = _get_template("chest_pain")
        state = _make_state(
            associated_shortness_of_breath=True,
            severity=9,
        )
        state_before = copy.deepcopy(state)
        evaluate_red_flags(state, template.red_flags)
        # Verify nothing mutated
        assert state.session_status == state_before.session_status
        assert state.question_count == state_before.question_count
        assert state.red_flags == state_before.red_flags
        assert len(state.slots) == len(state_before.slots)
        for sid, ss in state.slots.items():
            assert ss.status == state_before.slots[sid].status
            assert ss.value == state_before.slots[sid].value


# ═══════════════════════════════════════════════════════════════════════════
# 19. Evaluator does not mutate slot state
# ═══════════════════════════════════════════════════════════════════════════


class TestNoSlotMutation:
    def test_slot_values_unchanged(self) -> None:
        state = _make_state(severity=9, hemoptysis=True)
        rf = _make_rf("rf1", all_of=[_pred_gte("severity", 8)])
        slots_before = {
            sid: (ss.status, ss.value)
            for sid, ss in state.slots.items()
        }
        evaluate_red_flags(state, [rf])
        for sid, ss in state.slots.items():
            assert (ss.status, ss.value) == slots_before[sid]


# ═══════════════════════════════════════════════════════════════════════════
# 20. Evaluator does not mutate rule definitions
# ═══════════════════════════════════════════════════════════════════════════


class TestNoRuleMutation:
    def test_rules_unchanged(self) -> None:
        template = _get_template("headache")
        rules_before = len(template.red_flags)
        ids_before = [rf.id for rf in template.red_flags]
        state = _make_state(time_to_peak=2, new_neurologic_deficit_present=True)
        evaluate_red_flags(state, template.red_flags)
        assert len(template.red_flags) == rules_before
        assert [rf.id for rf in template.red_flags] == ids_before


# ═══════════════════════════════════════════════════════════════════════════
# 21. Registered severity is preserved
# ═══════════════════════════════════════════════════════════════════════════


class TestSeverityPreserved:
    def test_critical_severity_preserved(self) -> None:
        state = _make_state(hemoptysis=True)
        template = _get_template("cough")
        result = evaluate_red_flags(state, template.red_flags)
        match = next(m for m in result.matched if m.red_flag_id == "coughing_blood")
        assert match.severity == RedFlagSeverity.CRITICAL

    def test_high_severity_preserved(self) -> None:
        state = _make_state(chest_pain=True)
        template = _get_template("cough")
        result = evaluate_red_flags(state, template.red_flags)
        match = next(
            m for m in result.matched if m.red_flag_id == "cough_with_chest_pain"
        )
        assert match.severity == RedFlagSeverity.HIGH


# ═══════════════════════════════════════════════════════════════════════════
# 22. Registered action is preserved
# ═══════════════════════════════════════════════════════════════════════════


class TestActionPreserved:
    def test_urgent_action_preserved(self) -> None:
        state = _make_state(hemoptysis=True)
        template = _get_template("cough")
        result = evaluate_red_flags(state, template.red_flags)
        match = next(m for m in result.matched if m.red_flag_id == "coughing_blood")
        assert match.action == RedFlagAction.URGENT_CLINICIAN_REVIEW

    def test_prompt_action_preserved(self) -> None:
        state = _make_state(jaundice=True)
        template = _get_template("abdominal_pain")
        result = evaluate_red_flags(state, template.red_flags)
        match = next(
            m for m in result.matched
            if m.red_flag_id == "abdominal_pain_with_jaundice"
        )
        assert match.action == RedFlagAction.PROMPT_CLINICIAN_REVIEW


# ═══════════════════════════════════════════════════════════════════════════
# 23. No diagnosis is generated
# ═══════════════════════════════════════════════════════════════════════════


class TestNoDiagnosis:
    def test_result_has_no_diagnosis_field(self) -> None:
        result = RedFlagEvaluationResult(matched=())
        # The result model only has 'matched'
        assert not hasattr(result, "diagnosis")
        assert "diagnosis" not in RedFlagEvaluationResult.model_fields


# ═══════════════════════════════════════════════════════════════════════════
# 24. No treatment recommendation is generated
# ═══════════════════════════════════════════════════════════════════════════


class TestNoTreatment:
    def test_result_has_no_treatment_field(self) -> None:
        result = RedFlagEvaluationResult(matched=())
        assert not hasattr(result, "treatment")
        assert "treatment" not in RedFlagEvaluationResult.model_fields

    def test_match_has_no_treatment_field(self) -> None:
        m = RedFlagMatch(
            red_flag_id="test",
            severity=RedFlagSeverity.CRITICAL,
            action=RedFlagAction.URGENT_CLINICIAN_REVIEW,
        )
        assert not hasattr(m, "treatment")
        assert "treatment" not in RedFlagMatch.model_fields


# ═══════════════════════════════════════════════════════════════════════════
# 25. Template-scoped red flags: unrelated template rules not evaluated
# ═══════════════════════════════════════════════════════════════════════════


class TestTemplateScoping:
    def test_chest_pain_flags_not_triggered_by_cough_state(self) -> None:
        """Chest pain red flags reference chest-pain-specific slots."""
        template = _get_template("chest_pain")
        # cough-specific state; chest_pain red flags should not match
        state = _make_state(hemoptysis=True, shortness_of_breath=True)
        result = evaluate_red_flags(state, template.red_flags)
        # hemoptysis is not a chest_pain red-flag slot
        assert "coughing_blood" not in result.matched_ids

    def test_evaluator_only_checks_given_definitions(self) -> None:
        """The evaluator does not load other templates' rules."""
        state = _make_state(hemoptysis=True)
        # Only evaluate headache rules — no hemoptysis red flag there
        template = _get_template("headache")
        result = evaluate_red_flags(state, template.red_flags)
        assert "coughing_blood" not in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# 26. Malformed in-memory rule does not produce false emergency match
# ═══════════════════════════════════════════════════════════════════════════


class TestMalformedRuleSafety:
    def test_non_numeric_value_for_gte_no_match(self) -> None:
        """gte on a non-numeric value → no match, not an error."""
        state = _make_state(severity="not_a_number")
        rf = _make_rf("rf1", all_of=[_pred_gte("severity", 8)])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_none_value_in_known_slot_no_match(self) -> None:
        """A KNOWN slot with value=None should not match not_empty."""
        state = ClinicalSessionState(
            slots={"x": SlotState(status=SlotStatus.KNOWN, value=None)},
        )
        rf = _make_rf("rf1", all_of=[_pred_not_empty("x")])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches

    def test_non_string_value_for_contains_any_no_match(self) -> None:
        """contains_any on a non-string value → no match."""
        state = _make_state(radiation=42)
        rf = _make_rf("rf1", all_of=[_pred_contains_any("radiation", ["arm"])])
        result = evaluate_red_flags(state, [rf])
        assert not result.has_matches


# ═══════════════════════════════════════════════════════════════════════════
# 27. Real red-flag YAML definitions load and evaluate successfully
# ═══════════════════════════════════════════════════════════════════════════


class TestRealYAMLIntegration:
    @pytest.mark.parametrize("template_id", [
        "chest_pain", "fever", "cough", "abdominal_pain", "headache",
    ])
    def test_template_red_flags_load_successfully(
        self, template_id: str,
    ) -> None:
        template = _get_template(template_id)
        assert len(template.red_flags) > 0
        # Evaluate against empty state — should produce no matches
        state = ClinicalSessionState(slots={})
        result = evaluate_red_flags(state, template.red_flags)
        # No false positives from empty state
        assert not result.has_matches

    def test_contains_any_real_chest_pain_radiation(self) -> None:
        """chest_pain_with_arm_or_jaw_radiation uses contains_any."""
        template = _get_template("chest_pain")
        state = _make_state(radiation="pain radiating to left arm")
        result = evaluate_red_flags(state, template.red_flags)
        assert "chest_pain_with_arm_or_jaw_radiation" in result.matched_ids

    def test_contains_any_no_match_unrelated_text(self) -> None:
        template = _get_template("chest_pain")
        state = _make_state(radiation="pain in the chest only")
        result = evaluate_red_flags(state, template.red_flags)
        assert "chest_pain_with_arm_or_jaw_radiation" not in result.matched_ids

    def test_all_fever_red_flags(self) -> None:
        """All four fever red flags evaluate correctly."""
        template = _get_template("fever")
        # All true
        state = _make_state(
            confusion_present=True,
            severe_neck_stiffness_present=True,
            breathing_difficulty_present=True,
            unable_to_keep_fluids_down=True,
        )
        result = evaluate_red_flags(state, template.red_flags)
        assert "fever_with_confusion" in result.matched_ids
        assert "fever_with_severe_neck_stiffness" in result.matched_ids
        assert "fever_with_breathing_difficulty" in result.matched_ids
        assert "fever_with_inability_to_keep_fluids" in result.matched_ids


# ═══════════════════════════════════════════════════════════════════════════
# Additional: Result immutability
# ═══════════════════════════════════════════════════════════════════════════


class TestResultImmutability:
    def test_result_is_frozen(self) -> None:
        result = evaluate_red_flags(ClinicalSessionState(), [])
        with pytest.raises(Exception):
            result.matched = ()

    def test_match_is_frozen(self) -> None:
        m = RedFlagMatch(
            red_flag_id="x",
            severity=RedFlagSeverity.CRITICAL,
            action=RedFlagAction.URGENT_CLINICIAN_REVIEW,
        )
        with pytest.raises(Exception):
            m.red_flag_id = "y"


# ═══════════════════════════════════════════════════════════════════════════
# Additional: contains_any case-insensitive behavior
# ═══════════════════════════════════════════════════════════════════════════


class TestContainsAnyCaseInsensitive:
    def test_case_insensitive_match(self) -> None:
        state = _make_state(radiation="Pain in LEFT ARM and SHOULDER")
        rf = _make_rf(
            "rf1", all_of=[_pred_contains_any("radiation", ["arm", "jaw"])],
        )
        result = evaluate_red_flags(state, [rf])
        assert result.has_matches
