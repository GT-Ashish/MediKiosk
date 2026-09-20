"""
Tests for Phase 7 clinical session state, template schema, and duration models.

Step 1B test suite — validates:

SESSION STATE
    1.  ClinicalSessionState created with defaults
    2.  session_status defaults to IN_PROGRESS
    3.  question_count starts at 0
    4.  slots starts empty
    5.  question_history starts empty
    6.  red_flags starts empty
    7.  active_context_modules starts empty
    8.  interruption structure is valid
    9.  all interruption fields are represented
    10. template version pinning works
    11. question budget validation works

QUESTION HISTORY
    12. QuestionHistoryEntry validates correctly
    13. previous answer can be represented in question_history
    14. SlotState itself contains no revision-history list

DURATION
    15. valid DurationValue
    16. seconds → minutes normalization
    17. unitless duration rejected when unit is required
    18. invalid numeric duration rejected

TEMPLATE MODELS
    19. valid chest_pain-shaped template can parse
    20. valid headache duration slot can parse
    21. red-flag condition structure parses without evaluating it
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.domain.clinical_engine.duration import DurationValue
from app.domain.clinical_engine.enums import (
    ClinicalSessionStatus,
    RedFlagAction,
    RedFlagSeverity,
    SlotStatus,
    SlotType,
)
from app.domain.clinical_engine.session_state import (
    ClinicalSessionState,
    CurrentComplaint,
    InterruptionState,
    PauseReason,
    QuestionHistoryEntry,
)
from app.domain.clinical_engine.slot_state import SlotState
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


# ── Session State Defaults ───────────────────────────────────────────────────

class TestClinicalSessionStateDefaults:
    """Tests 1–7: A freshly created session has sensible domain defaults."""

    def test_can_create_with_defaults(self) -> None:
        """Test 1."""
        state = ClinicalSessionState()
        assert state.session_id is not None

    def test_session_status_defaults_to_in_progress(self) -> None:
        """Test 2."""
        state = ClinicalSessionState()
        assert state.session_status == ClinicalSessionStatus.IN_PROGRESS

    def test_question_count_starts_at_zero(self) -> None:
        """Test 3."""
        state = ClinicalSessionState()
        assert state.question_count == 0

    def test_slots_starts_empty(self) -> None:
        """Test 4."""
        state = ClinicalSessionState()
        assert state.slots == {}

    def test_question_history_starts_empty(self) -> None:
        """Test 5."""
        state = ClinicalSessionState()
        assert state.question_history == []

    def test_red_flags_starts_empty(self) -> None:
        """Test 6."""
        state = ClinicalSessionState()
        assert state.red_flags == []

    def test_active_context_modules_starts_empty(self) -> None:
        """Test 7."""
        state = ClinicalSessionState()
        assert state.active_context_modules == []


# ── Interruption State ───────────────────────────────────────────────────────

class TestInterruptionState:
    """Tests 8–9: Interruption metadata is valid and complete."""

    def test_interruption_defaults_are_none(self) -> None:
        """Test 8."""
        state = ClinicalSessionState()
        interruption = state.interruption
        assert isinstance(interruption, InterruptionState)
        assert interruption.last_active_at is None
        assert interruption.resume_token is None
        assert interruption.pause_reason is None
        assert interruption.paused_at is None
        assert interruption.resumed_at is None

    def test_all_interruption_fields_are_represented(self) -> None:
        """Test 9: All five required interruption fields exist."""
        now = datetime.now(tz=timezone.utc)
        interruption = InterruptionState(
            last_active_at=now,
            resume_token="tok-abc-123",
            pause_reason=PauseReason.TIMEOUT,
            paused_at=now,
            resumed_at=now,
        )
        assert interruption.last_active_at == now
        assert interruption.resume_token == "tok-abc-123"
        assert interruption.pause_reason == PauseReason.TIMEOUT
        assert interruption.paused_at == now
        assert interruption.resumed_at == now

    def test_pause_reason_enum_values(self) -> None:
        """PauseReason contains the three required values."""
        assert set(PauseReason) == {
            PauseReason.TIMEOUT,
            PauseReason.PATIENT_LEFT,
            PauseReason.EXPLICIT_PAUSE,
        }


# ── Template Version Pinning ─────────────────────────────────────────────────

class TestTemplateVersionPinning:
    """Test 10: CurrentComplaint pins template version."""

    def test_current_complaint_pins_version(self) -> None:
        complaint = CurrentComplaint(
            template_id="chest_pain",
            template_version="1.0.0",
            terminology_system="SNOMED_CT",
            terminology_code="29857009",
            display_name="Chest pain",
        )
        state = ClinicalSessionState(current_complaint=complaint)
        assert state.current_complaint is not None
        assert state.current_complaint.template_id == "chest_pain"
        assert state.current_complaint.template_version == "1.0.0"
        assert state.current_complaint.terminology_system == "SNOMED_CT"
        assert state.current_complaint.terminology_code == "29857009"
        assert state.current_complaint.display_name == "Chest pain"


# ── Question Budget Validation ───────────────────────────────────────────────

class TestQuestionBudget:
    """Test 11: Budget validation on the session model."""

    def test_valid_budget(self) -> None:
        budget = QuestionBudget(min_questions=9, max_questions=14)
        assert budget.min_questions == 9
        assert budget.max_questions == 14

    def test_min_greater_than_max_rejected(self) -> None:
        with pytest.raises(ValidationError):
            QuestionBudget(min_questions=15, max_questions=10)

    def test_zero_min_rejected(self) -> None:
        with pytest.raises(ValidationError):
            QuestionBudget(min_questions=0, max_questions=10)

    def test_negative_max_rejected(self) -> None:
        with pytest.raises(ValidationError):
            QuestionBudget(min_questions=1, max_questions=-1)

    def test_session_with_budget(self) -> None:
        budget = QuestionBudget(min_questions=9, max_questions=14)
        state = ClinicalSessionState(question_budget=budget)
        assert state.question_budget is not None
        assert state.question_budget.min_questions == 9


# ── Question History ─────────────────────────────────────────────────────────

class TestQuestionHistory:
    """Tests 12–14."""

    def test_question_history_entry_validates(self) -> None:
        """Test 12."""
        entry = QuestionHistoryEntry(
            slot_id="onset",
            phrased_text="When did your chest pain start?",
            language="en",
            answer_raw_text="About 2 hours ago",
        )
        assert entry.slot_id == "onset"
        assert entry.answer_raw_text == "About 2 hours ago"

    def test_previous_answer_in_history(self) -> None:
        """Test 13: Revision audit trail lives in question_history."""
        state = ClinicalSessionState()

        # First answer
        state.question_history.append(
            QuestionHistoryEntry(
                slot_id="onset",
                phrased_text="When did your chest pain start?",
                answer_raw_text="2 hours ago",
            )
        )

        # Revision — second entry for same slot
        state.question_history.append(
            QuestionHistoryEntry(
                slot_id="onset",
                phrased_text="You mentioned 2 hours — could you be more specific?",
                answer_raw_text="Actually, about 3 hours ago",
            )
        )

        onset_entries = [e for e in state.question_history if e.slot_id == "onset"]
        assert len(onset_entries) == 2
        assert onset_entries[0].answer_raw_text == "2 hours ago"
        assert onset_entries[1].answer_raw_text == "Actually, about 3 hours ago"

    def test_slot_state_has_no_history_list(self) -> None:
        """Test 14: SlotState must NOT contain a revision-history collection."""
        field_names = set(SlotState.model_fields.keys())
        assert "history" not in field_names
        assert "revision_history" not in field_names
        assert "previous_values" not in field_names


# ── Duration ─────────────────────────────────────────────────────────────────

class TestDurationValue:
    """Tests 15–18."""

    def test_valid_duration(self) -> None:
        """Test 15."""
        d = DurationValue(numeric_value=5.0, unit="minutes")
        assert d.numeric_value == 5.0
        assert d.unit == "minutes"

    def test_seconds_to_minutes_normalization(self) -> None:
        """Test 16: 30 seconds → 0.5 minutes."""
        d = DurationValue(numeric_value=30.0, unit="seconds")
        normalized = d.normalize_to("minutes")
        assert normalized.unit == "minutes"
        assert abs(normalized.numeric_value - 0.5) < 1e-6

    def test_unitless_duration_rejected(self) -> None:
        """Test 17: Blank/whitespace-only unit rejected."""
        with pytest.raises(ValidationError):
            DurationValue(numeric_value=5.0, unit="")

        with pytest.raises(ValidationError):
            DurationValue(numeric_value=5.0, unit="   ")

    def test_negative_numeric_value_rejected(self) -> None:
        """Test 18: Negative duration is invalid."""
        with pytest.raises(ValidationError):
            DurationValue(numeric_value=-1.0, unit="minutes")

    def test_identity_normalization(self) -> None:
        """Normalizing minutes to minutes returns an equivalent copy."""
        d = DurationValue(numeric_value=5.0, unit="minutes")
        normalized = d.normalize_to("minutes")
        assert normalized.numeric_value == 5.0
        assert normalized.unit == "minutes"

    def test_unsupported_conversion_raises(self) -> None:
        """Unsupported unit conversions raise ValueError."""
        d = DurationValue(numeric_value=1.0, unit="days")
        with pytest.raises(ValueError, match="Unsupported duration conversion"):
            d.normalize_to("minutes")

    def test_hours_to_minutes(self) -> None:
        """1 hour → 60 minutes."""
        d = DurationValue(numeric_value=1.0, unit="hours")
        normalized = d.normalize_to("minutes")
        assert normalized.numeric_value == 60.0


# ── Template Schema Models ───────────────────────────────────────────────────

class TestTemplateSchemaModels:
    """Tests 19–21: Structural model parsing."""

    def test_chest_pain_shaped_template_parses(self) -> None:
        """Test 19: A template shaped like chest_pain.yaml parses."""
        template = ClinicalTemplate(
            template_id="chest_pain",
            version="1.0.0",
            status="demo_non_production",
            terminology=TerminologyRef(
                system="SNOMED_CT",
                code="29857009",
                display="Chest pain",
            ),
            question_budget=QuestionBudget(
                min_questions=9,
                max_questions=14,
            ),
            general_modules=["general_history"],
            slots=[
                SlotDefinition(
                    id="onset",
                    type=SlotType.TEXT,
                    required=True,
                    priority=1,
                    description="When pain/discomfort began.",
                ),
                SlotDefinition(
                    id="severity",
                    type=SlotType.INTEGER,
                    required=True,
                    priority=6,
                    min=0,
                    max=10,
                    description="Severity on 0-10 scale.",
                ),
                SlotDefinition(
                    id="temporal_course",
                    type=SlotType.ENUM,
                    required=True,
                    priority=2,
                    allowed_values=[
                        "constant", "intermittent", "recurrent_episodes",
                        "first_episode", "worsening", "improving",
                        "unchanged", "unknown",
                    ],
                    description="Pattern since onset.",
                ),
                SlotDefinition(
                    id="associated_shortness_of_breath",
                    type=SlotType.BOOLEAN,
                    required=True,
                    priority=10,
                    description="Shortness of breath with the complaint.",
                ),
            ],
            context_modules=[
                ContextModuleDefinition(
                    id="cardiovascular_history",
                    triggers=[
                        "known_heart_disease",
                        "exertional_chest_discomfort",
                    ],
                    slots=[
                        SlotDefinition(
                            id="cardiovascular_history_detail",
                            type=SlotType.TEXT,
                            required=False,
                            priority=30,
                        ),
                    ],
                ),
            ],
            triggers=[
                TriggerDefinition(
                    id="exertional_chest_discomfort",
                    description="Symptoms occur with exertion.",
                ),
            ],
            red_flags=[
                RedFlagDefinition(
                    id="chest_pain_with_breathing_difficulty",
                    severity=RedFlagSeverity.CRITICAL,
                    when=RedFlagConditionGroup(
                        all_of=[
                            RedFlagConditionPredicate(
                                slot="associated_shortness_of_breath",
                                equals=True,
                            ),
                        ],
                    ),
                    action=RedFlagAction.URGENT_CLINICIAN_REVIEW,
                ),
            ],
        )
        assert template.template_id == "chest_pain"
        assert template.version == "1.0.0"
        assert len(template.slots) == 4
        assert len(template.red_flags) == 1

    def test_headache_duration_slot_parses(self) -> None:
        """Test 20: Duration slot with unit, min, max parses correctly."""
        slot = SlotDefinition(
            id="time_to_peak",
            type=SlotType.DURATION,
            required=False,
            priority=2,
            unit="minutes",
            min=0,
            max=1440,
            description="Time from onset to maximum intensity.",
        )
        assert slot.type == SlotType.DURATION
        assert slot.unit == "minutes"
        assert slot.min == 0
        assert slot.max == 1440

    def test_red_flag_condition_structure_parses(self) -> None:
        """Test 21: Red-flag conditions parse without evaluation."""
        # all_of with equals
        group_all = RedFlagConditionGroup(
            all_of=[
                RedFlagConditionPredicate(
                    slot="associated_shortness_of_breath",
                    equals=True,
                ),
            ],
        )
        assert group_all.all_of is not None
        assert group_all.any_of is None

        # any_of with multiple predicates
        group_any = RedFlagConditionGroup(
            any_of=[
                RedFlagConditionPredicate(slot="fever_present", equals=True),
                RedFlagConditionPredicate(slot="neck_stiffness_present", equals=True),
            ],
        )
        assert group_any.any_of is not None
        assert len(group_any.any_of) == 2

        # gte/lte predicates
        pred_gte = RedFlagConditionPredicate(slot="severity", gte=8)
        assert pred_gte.gte == 8

        # contains_any predicate
        pred_contains = RedFlagConditionPredicate(
            slot="radiation",
            contains_any=["arm", "shoulder", "jaw"],
        )
        assert pred_contains.contains_any is not None
        assert "arm" in pred_contains.contains_any

        # not_empty predicate
        pred_not_empty = RedFlagConditionPredicate(
            slot="trauma_history", not_empty=True,
        )
        assert pred_not_empty.not_empty is True


# ── Template Schema Validation ───────────────────────────────────────────────

class TestTemplateSchemaValidation:
    """Structural validation on template models."""

    def test_red_flag_predicate_requires_operator(self) -> None:
        """A predicate with no operator is rejected."""
        with pytest.raises(ValidationError, match="at least one operator"):
            RedFlagConditionPredicate(slot="onset")

    def test_red_flag_group_requires_exactly_one(self) -> None:
        """Both all_of and any_of, or neither, is rejected."""
        pred = RedFlagConditionPredicate(slot="onset", equals=True)

        with pytest.raises(ValidationError, match="Exactly one"):
            RedFlagConditionGroup(all_of=[pred], any_of=[pred])

        with pytest.raises(ValidationError, match="Exactly one"):
            RedFlagConditionGroup()

    def test_general_history_module_parses(self) -> None:
        """GeneralHistoryModule parses without terminology or budget."""
        module = GeneralHistoryModule(
            template_id="general_history",
            version="1.0.0",
            status="demo_non_production",
            slots=[
                SlotDefinition(
                    id="past_medical_history",
                    type=SlotType.TEXT,
                    required=True,
                    priority=70,
                ),
                SlotDefinition(
                    id="current_medications",
                    type=SlotType.TEXT,
                    required=True,
                    priority=71,
                ),
            ],
        )
        assert module.template_id == "general_history"
        assert len(module.slots) == 2
        # Verify it does NOT have terminology or question_budget
        assert not hasattr(module, "terminology")
        assert not hasattr(module, "question_budget")

    def test_negative_question_count_rejected(self) -> None:
        """question_count must be non-negative."""
        with pytest.raises(ValidationError):
            ClinicalSessionState(question_count=-1)
