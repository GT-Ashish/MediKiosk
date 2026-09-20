"""
Tests for Phase 7 clinical template loader, validator, and registry.

Step 1C test suite — validates:

LOADING
    1.  chest_pain loads
    2.  fever loads
    3.  cough loads
    4.  abdominal_pain loads
    5.  headache loads
    6.  general_history loads as GeneralHistoryModule
    7.  trigger registry loads

VALIDATION (negative — small inline fixtures)
    8.  malformed template rejected
    9.  duplicate slot rejected
    10. unknown trigger rejected
    11. dangling red-flag slot rejected
    12. invalid enum rejected (enum slot without allowed_values)
    13. invalid numeric range rejected
    14. invalid question budget rejected
    15. invalid/missing duration unit rejected
    20. unsupported red-flag operator rejected

REGISTRY
    16. template version preserved
    17. registry lookup by template_id + version
    18. latest-template lookup works
    19. general_history resolution works
    21. all supplied templates validate successfully
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from app.domain.clinical_engine.enums import (
    RedFlagAction,
    RedFlagSeverity,
    SlotType,
)
from app.domain.clinical_engine.loader import (
    load_general_module,
    load_red_flag_rules,
    load_template,
    load_trigger_registry,
    load_yaml_file,
)
from app.domain.clinical_engine.registry import TemplateRegistry
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    ContextModuleDefinition,
    GeneralHistoryModule,
    QuestionBudget,
    RedFlagConditionGroup,
    RedFlagConditionPredicate,
    RedFlagDefinition,
    SlotDefinition,
    TerminologyRef,
    TriggerDefinition,
)
from app.domain.clinical_engine.validator import (
    ValidationResult,
    validate_template,
    validate_template_set,
)
from app.utils.errors import (
    ClinicalEngineError,
    TemplateNotFoundError,
    TemplateValidationError,
)

# ── Paths ────────────────────────────────────────────────────────────────────

_CONTENT_DIR = Path(__file__).resolve().parents[2] / "backend" / "app" / "domain" / "clinical_engine" / "content"
_TEMPLATES_DIR = _CONTENT_DIR / "templates"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _write_yaml(tmp_path: Path, filename: str, data: dict | str) -> Path:
    """Write a YAML file into a tmp directory and return its path."""
    path = tmp_path / filename
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    return path


def _minimal_template(**overrides) -> dict:
    """Return a minimal valid template dict for negative testing."""
    base = {
        "template_id": "test_template",
        "version": "1.0.0",
        "status": "demo_non_production",
        "terminology": {
            "system": "SNOMED_CT",
            "code": "12345",
            "display": "Test",
        },
        "question_budget": {
            "min_questions": 5,
            "max_questions": 10,
        },
        "slots": [
            {
                "id": "onset",
                "type": "text",
                "required": True,
                "priority": 1,
                "description": "When it started.",
            }
        ],
    }
    base.update(overrides)
    return base


# ══════════════════════════════════════════════════════════════════════════════
# LOADING TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestTemplateLoading:
    """Tests 1–7: All supplied templates and global files load."""

    def test_chest_pain_loads(self) -> None:
        """Test 1."""
        template = load_template(_TEMPLATES_DIR / "chest_pain.yaml")
        assert template.template_id == "chest_pain"
        assert template.version == "1.0.0"
        assert template.terminology.system == "SNOMED_CT"
        assert len(template.slots) > 0
        assert len(template.red_flags) > 0

    def test_fever_loads(self) -> None:
        """Test 2."""
        template = load_template(_TEMPLATES_DIR / "fever.yaml")
        assert template.template_id == "fever"

    def test_cough_loads(self) -> None:
        """Test 3."""
        template = load_template(_TEMPLATES_DIR / "cough.yaml")
        assert template.template_id == "cough"

    def test_abdominal_pain_loads(self) -> None:
        """Test 4."""
        template = load_template(_TEMPLATES_DIR / "abdominal_pain.yaml")
        assert template.template_id == "abdominal_pain"

    def test_headache_loads(self) -> None:
        """Test 5."""
        template = load_template(_TEMPLATES_DIR / "headache.yaml")
        assert template.template_id == "headache"
        # Verify the duration slot with unit
        time_to_peak = next(
            (s for s in template.slots if s.id == "time_to_peak"), None
        )
        assert time_to_peak is not None
        assert time_to_peak.type == SlotType.DURATION
        assert time_to_peak.unit == "minutes"

    def test_general_history_loads(self) -> None:
        """Test 6."""
        module = load_general_module(_TEMPLATES_DIR / "general_history.yaml")
        assert isinstance(module, GeneralHistoryModule)
        assert module.template_id == "general_history"
        assert len(module.slots) == 6
        # Should NOT be a ClinicalTemplate
        assert not isinstance(module, ClinicalTemplate)

    def test_trigger_registry_loads(self) -> None:
        """Test 7."""
        triggers = load_trigger_registry(_CONTENT_DIR / "triggers.yaml")
        assert isinstance(triggers, dict)
        assert "chest_pain" in triggers
        assert "fever" in triggers
        assert "headache" in triggers
        assert "exertional_chest_discomfort" in triggers["chest_pain"]

    def test_red_flag_rules_load(self) -> None:
        """Global red-flag rules load as data."""
        rules = load_red_flag_rules(_CONTENT_DIR / "red_flags.yaml")
        assert "global_rules" in rules
        assert "version" in rules

    def test_missing_file_raises(self) -> None:
        """Missing YAML file raises ClinicalEngineError."""
        with pytest.raises(ClinicalEngineError, match="not found"):
            load_yaml_file(Path("/nonexistent/file.yaml"))


# ══════════════════════════════════════════════════════════════════════════════
# SAFETY FIELD TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestSafetyFields:
    """Verify boolean safety-critical slots from content pack."""

    def test_chest_pain_boolean_safety_fields(self) -> None:
        template = load_template(_TEMPLATES_DIR / "chest_pain.yaml")
        boolean_slots = [s for s in template.slots if s.type == SlotType.BOOLEAN]
        boolean_ids = {s.id for s in boolean_slots}
        assert "associated_shortness_of_breath" in boolean_ids
        assert "associated_sweating" in boolean_ids
        assert "associated_dizziness_or_fainting" in boolean_ids

    def test_headache_boolean_safety_fields(self) -> None:
        template = load_template(_TEMPLATES_DIR / "headache.yaml")
        boolean_slots = [s for s in template.slots if s.type == SlotType.BOOLEAN]
        boolean_ids = {s.id for s in boolean_slots}
        assert "new_neurologic_deficit_present" in boolean_ids
        assert "fever_present" in boolean_ids
        assert "neck_stiffness_present" in boolean_ids


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION NEGATIVE TESTS (using tmp fixtures)
# ══════════════════════════════════════════════════════════════════════════════

class TestValidationNegative:
    """Tests 8–15, 20: Malformed templates are rejected."""

    def test_malformed_template_rejected(self, tmp_path: Path) -> None:
        """Test 8: YAML that doesn't match ClinicalTemplate schema."""
        bad = {"template_id": "bad", "version": "1.0.0"}
        path = _write_yaml(tmp_path, "bad.yaml", bad)
        with pytest.raises(Exception):  # Pydantic ValidationError
            load_template(path)

    def test_duplicate_slot_rejected(self) -> None:
        """Test 9: Duplicate slot IDs produce a validation error."""
        template = ClinicalTemplate(
            **_minimal_template(
                slots=[
                    {"id": "onset", "type": "text", "required": True, "priority": 1},
                    {"id": "onset", "type": "text", "required": False, "priority": 2},
                ]
            )
        )
        result = validate_template(template)
        assert not result.is_valid
        dup_issues = [i for i in result.issues if "Duplicate slot" in i.message]
        assert len(dup_issues) > 0

    def test_unknown_trigger_rejected(self) -> None:
        """Test 10: Context module referencing unknown trigger."""
        template = ClinicalTemplate(
            **_minimal_template(
                context_modules=[
                    {
                        "id": "test_context",
                        "triggers": ["nonexistent_trigger"],
                        "slots": [],
                    }
                ],
                triggers=[],
            )
        )
        trigger_reg = {"test_template": []}
        result = validate_template(template, trigger_registry=trigger_reg)
        assert not result.is_valid
        trig_issues = [i for i in result.issues if "Unknown trigger" in i.message]
        assert len(trig_issues) > 0

    def test_dangling_red_flag_slot_rejected(self) -> None:
        """Test 11: Red-flag referencing a non-existent slot."""
        template = ClinicalTemplate(
            **_minimal_template(
                red_flags=[
                    {
                        "id": "test_rf",
                        "severity": "critical",
                        "when": {
                            "all_of": [
                                {"slot": "nonexistent_slot", "equals": True}
                            ]
                        },
                        "action": "urgent_clinician_review",
                    }
                ]
            )
        )
        result = validate_template(template)
        assert not result.is_valid
        rf_issues = [i for i in result.issues if "non-existent slot" in i.message]
        assert len(rf_issues) > 0

    def test_invalid_enum_rejected(self) -> None:
        """Test 12: Enum slot without allowed_values."""
        template = ClinicalTemplate(
            **_minimal_template(
                slots=[
                    {
                        "id": "bad_enum",
                        "type": "enum",
                        "required": True,
                        "priority": 1,
                    }
                ]
            )
        )
        result = validate_template(template)
        assert not result.is_valid
        enum_issues = [i for i in result.issues if "allowed_values" in i.message]
        assert len(enum_issues) > 0

    def test_invalid_numeric_range_rejected(self) -> None:
        """Test 13: min > max on a numeric slot."""
        template = ClinicalTemplate(
            **_minimal_template(
                slots=[
                    {
                        "id": "bad_range",
                        "type": "integer",
                        "required": True,
                        "priority": 1,
                        "min": 10,
                        "max": 5,
                    }
                ]
            )
        )
        result = validate_template(template)
        assert not result.is_valid
        range_issues = [i for i in result.issues if "min" in i.message and "max" in i.message]
        assert len(range_issues) > 0

    def test_invalid_question_budget_rejected(self, tmp_path: Path) -> None:
        """Test 14: Question budget with min > max."""
        bad_data = _minimal_template(
            question_budget={"min_questions": 20, "max_questions": 5}
        )
        path = _write_yaml(tmp_path, "bad_budget.yaml", bad_data)
        with pytest.raises(Exception):  # Pydantic ValidationError
            load_template(path)

    def test_duration_without_unit_rejected(self) -> None:
        """Test 15: Duration slot with numeric range but no unit."""
        template = ClinicalTemplate(
            **_minimal_template(
                slots=[
                    {
                        "id": "bad_duration",
                        "type": "duration",
                        "required": False,
                        "priority": 1,
                        "min": 0,
                        "max": 100,
                        # no unit declared
                    }
                ]
            )
        )
        result = validate_template(template)
        assert not result.is_valid
        dur_issues = [i for i in result.issues if "unit" in i.message]
        assert len(dur_issues) > 0

    def test_unsupported_red_flag_operator_rejected(self) -> None:
        """Test 20: Red-flag predicate with no operator raises Pydantic error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            RedFlagConditionPredicate(slot="onset")


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestTemplateRegistry:
    """Tests 16–19, 21."""

    def test_template_version_preserved(self) -> None:
        """Test 16."""
        template = load_template(_TEMPLATES_DIR / "chest_pain.yaml")
        assert template.version == "1.0.0"

    def test_registry_lookup_by_id_and_version(self) -> None:
        """Test 17."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        template = registry.get("chest_pain", "1.0.0")
        assert template.template_id == "chest_pain"
        assert template.version == "1.0.0"

    def test_latest_template_lookup(self) -> None:
        """Test 18."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        template = registry.get_latest("fever")
        assert template.template_id == "fever"
        assert template.version == "1.0.0"

    def test_general_history_resolution(self) -> None:
        """Test 19."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        chest_pain = registry.get("chest_pain", "1.0.0")
        resolved_slots = registry.resolve_general_modules(chest_pain)
        slot_ids = [s.id for s in resolved_slots]
        assert "past_medical_history" in slot_ids
        assert "current_medications" in slot_ids
        assert "medication_allergies" in slot_ids
        assert len(resolved_slots) == 6

    def test_all_supplied_templates_validate(self) -> None:
        """Test 21: Full content directory loads and validates."""
        registry = TemplateRegistry()
        result = registry.load_content_directory(_CONTENT_DIR)
        assert result.is_valid
        available = registry.list_available()
        template_ids = {tid for tid, _ in available}
        assert template_ids == {
            "chest_pain", "fever", "cough", "abdominal_pain", "headache",
        }

    def test_template_not_found_raises(self) -> None:
        """Missing template raises TemplateNotFoundError."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        with pytest.raises(TemplateNotFoundError):
            registry.get("nonexistent", "1.0.0")

    def test_template_not_found_wrong_version(self) -> None:
        """Wrong version raises TemplateNotFoundError."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        with pytest.raises(TemplateNotFoundError):
            registry.get("chest_pain", "99.0.0")

    def test_duplicate_registration_raises(self) -> None:
        """Re-registering same template+version raises TemplateValidationError."""
        registry = TemplateRegistry()
        template = load_template(_TEMPLATES_DIR / "chest_pain.yaml")
        registry.register(template)
        with pytest.raises(TemplateValidationError):
            registry.register(template)

    def test_list_available_returns_sorted(self) -> None:
        """list_available returns sorted (template_id, version) pairs."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        available = registry.list_available()
        assert available == sorted(available)
        assert len(available) == 5

    def test_trigger_registry_accessible(self) -> None:
        """Trigger registry is available after loading."""
        registry = TemplateRegistry()
        registry.load_content_directory(_CONTENT_DIR)
        triggers = registry.trigger_registry
        assert "chest_pain" in triggers
        assert "headache" in triggers


# ══════════════════════════════════════════════════════════════════════════════
# ERROR HIERARCHY TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestTemplateErrors:
    """TemplateValidationError and TemplateNotFoundError fit the hierarchy."""

    def test_template_validation_error_inherits(self) -> None:
        err = TemplateValidationError(
            template_id="test", errors=["bad slot"]
        )
        assert isinstance(err, ClinicalEngineError)
        assert err.template_id == "test"
        assert "bad slot" in err.detail

    def test_template_not_found_error_inherits(self) -> None:
        err = TemplateNotFoundError(template_id="test", version="1.0.0")
        assert isinstance(err, ClinicalEngineError)
        assert err.template_id == "test"
        assert err.version == "1.0.0"
