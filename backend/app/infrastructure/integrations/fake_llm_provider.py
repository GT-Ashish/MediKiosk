"""
Fake LLM Extraction Provider — Testing Only.

A deterministic, network-free implementation of LLMExtractionProvider
for unit tests.  Returns configurable ExtractionResult objects.

Usage::

    from app.infrastructure.integrations.fake_llm_provider import (
        FakeLLMProvider,
    )

    # Simple: always returns a fixed result
    provider = FakeLLMProvider(result=my_extraction_result)
    result = provider.extract(...)

    # Simulate retry: first call malformed, second succeeds
    provider = FakeLLMProvider(
        results_sequence=[None, my_extraction_result],
    )

    # Simulate total failure: both attempts malformed
    provider = FakeLLMProvider(
        results_sequence=[None, None],
    )
"""

from __future__ import annotations

from app.domain.clinical_engine.extraction_schema import ExtractionResult
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    SlotDefinition,
)


class FakeLLMProvider:
    """
    Deterministic fake LLM provider for testing.

    Behaviour modes:
        1. **Fixed result**: Pass ``result`` — every call returns it.
        2. **Sequence**: Pass ``results_sequence`` — each internal attempt
           consumes the next item.  ``None`` means "malformed output"
           (triggers retry).  When all items are ``None``, returns safe failure.

    The provider mimics the bounded-retry contract:
        - Up to 2 internal attempts (first + one retry).
        - ``None`` in the sequence → malformed response.
        - If both attempts yield ``None`` → safe failure.

    Call count is tracked in ``call_count`` for assertions.
    """

    def __init__(
        self,
        *,
        result: ExtractionResult | None = None,
        results_sequence: list[ExtractionResult | None] | None = None,
    ) -> None:
        if result is not None and results_sequence is not None:
            raise ValueError(
                "Provide either 'result' or 'results_sequence', not both."
            )
        if result is not None:
            # Fixed mode: both attempts succeed with same result
            self._sequence = [result, result]
        elif results_sequence is not None:
            # Pad to at least 2 entries (first attempt + retry)
            self._sequence = list(results_sequence)
            while len(self._sequence) < 2:
                self._sequence.append(self._sequence[-1] if self._sequence else None)
        else:
            # Default: safe failure
            self._sequence = [None, None]

        self.call_count: int = 0

    def extract(
        self,
        template: ClinicalTemplate,
        active_slot_ids: list[str],
        slot_definitions: list[SlotDefinition],
        available_trigger_ids: list[str],
        patient_response: str,
        language: str,
    ) -> ExtractionResult:
        """
        Simulate extraction with bounded retry.

        Consumes up to 2 items from the results sequence:
            - 1st item = first attempt
            - 2nd item = retry attempt (if 1st was None)

        Returns safe failure if both are None.
        """
        self.call_count += 1

        # First attempt
        first = self._sequence[0] if len(self._sequence) > 0 else None
        if first is not None:
            return first

        # Retry
        second = self._sequence[1] if len(self._sequence) > 1 else None
        if second is not None:
            return second

        # Safe failure — both malformed
        return ExtractionResult(
            observations=[],
            proposed_triggers=[],
            detected_language=None,
            retry_required=True,
        )
