"""
LLM Extraction Provider — Protocol Definition.

Defines the ``LLMExtractionProvider`` Protocol that any LLM backend
(Gemini, Ollama, Azure OpenAI, etc.) must implement to serve as the
extraction component for the clinical engine.

The clinical engine depends ONLY on this Protocol — never on
provider-specific classes.

Architecture:
    Clinical engine
          ↓
    LLMExtractionProvider (this Protocol)
          ↓
    Concrete provider  (gemini_provider, fake_llm_provider, ...)
          ↓
    Remote API / local model
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.clinical_engine.extraction_schema import ExtractionResult
from app.domain.clinical_engine.template_schema import (
    ClinicalTemplate,
    SlotDefinition,
)


@runtime_checkable
class LLMExtractionProvider(Protocol):
    """
    Protocol for LLM-based clinical slot extraction.

    Implementors are responsible for:
        1. Building the extraction prompt from session context.
        2. Sending the prompt to the LLM with a structured-output schema.
        3. Parsing the response into an ExtractionResult.
        4. Implementing bounded retry on malformed output.
        5. Returning a safe-failure ExtractionResult when all retries fail.

    Implementors must NOT:
        - Mutate ClinicalSessionState or SlotState.
        - Choose the next question or activate context modules.
        - Evaluate red flags or diagnose.
    """

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
        Extract slot observations from a patient response.

        Args:
            template: The clinical template for the current session.
            active_slot_ids: IDs of slots currently being asked about.
            slot_definitions: Full slot definitions for context.
            available_trigger_ids: Closed trigger vocabulary.
            patient_response: Verbatim patient utterance text.
            language: BCP-47 language code for the session.

        Returns:
            An immutable ExtractionResult containing:
                - per-slot observations
                - proposed trigger IDs
                - detected language
                - retry_required flag (True on safe failure)
        """
        ...
