"""
HistoryService — Service Protocol.

Defines the interface for clinical history elicitation and retrieval.

The HistoryService is responsible for:
    - Recording individual Q&A answers from the kiosk conversation
    - Building a structured ClinicalHistory from collected answers
    - Retrieving the current history for a session

Clinical workflow note:
    The conversation engine (deferred to Phase 7+) calls record_answer()
    for each patient response. The clinical workflow/state machine decides
    which questions to ask — NOT the LLM.

    build_structured_history() assembles the collected answers into a
    ClinicalHistory. In Phase 7+, this may involve an LLM extraction
    step for natural language answers.

Implementation note (Phase 6):
    Concrete implementation will be InMemoryHistoryService.
    The history is stored in memory keyed by session_id.
"""

import uuid
from typing import Protocol

from app.domain.schemas.history import ClinicalHistory, HistoryAnswer, AnswerSource


class HistoryService(Protocol):
    """
    Interface for clinical history elicitation and retrieval.
    """

    async def record_answer(
        self,
        session_id: uuid.UUID,
        question_id: str,
        question_text: str,
        answer_text: str,
        answer_source: AnswerSource,
        confidence: float | None = None,
    ) -> HistoryAnswer:
        """
        Record a single patient answer from the kiosk conversation.

        Called by the conversation engine each time the patient answers
        a clinical question.

        Args:
            session_id: The session this answer belongs to.
            question_id: Identifier for the clinical question (e.g., 'onset', 'severity').
            question_text: The question text shown to the patient.
            answer_text: The patient's answer (verbatim or transcribed).
            answer_source: How the answer was captured (VOICE, TEXT, DOCUMENT).
            confidence: Optional confidence score (0.0–1.0) from ASR/extraction.

        Returns:
            The recorded HistoryAnswer.
        Raises:
            SessionNotFoundError: If the session does not exist.
            ConsentRequiredError: If consent has not been given for this session.
        """
        ...

    async def get_history(self, session_id: uuid.UUID) -> ClinicalHistory | None:
        """
        Retrieve the current clinical history for a session.

        Args:
            session_id: The session to retrieve history for.

        Returns:
            The ClinicalHistory if history has been started, None otherwise.
        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        ...

    async def build_structured_history(
        self,
        session_id: uuid.UUID,
        chief_complaint: str,
    ) -> ClinicalHistory:
        """
        Assemble a ClinicalHistory from all recorded answers for a session.

        This is the point where raw Q&A answers are structured into the
        formal ClinicalHistory schema. In Phase 7+, this may involve an
        LLM extraction step for natural-language answers.

        Args:
            session_id: The session to build history for.
            chief_complaint: The patient's chief complaint.

        Returns:
            A populated ClinicalHistory.
        Raises:
            SessionNotFoundError: If the session does not exist.
            ConsentRequiredError: If consent has not been given.
        """
        ...
