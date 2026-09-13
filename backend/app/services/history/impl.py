"""
HistoryService — Concrete Implementation.

Implements the HistoryService Protocol using repository pattern.
Assembles ClinicalHistory from persisted HistoryAnswer records.
"""

import uuid

from app.domain.schemas.history import ClinicalHistory, HistoryAnswer, AnswerSource
from app.infrastructure.repositories.session_repo import SQLAlchemySessionRepository
from app.infrastructure.repositories.history_repo import SQLAlchemyHistoryRepository
from app.infrastructure.repositories.visit_repo import SQLAlchemyVisitRepository
from app.utils.errors import SessionNotFoundError, ConsentRequiredError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class HistoryServiceImpl:
    """
    Concrete implementation of the HistoryService Protocol.

    Records individual Q&A answers and assembles them into structured
    ClinicalHistory objects.
    """

    def __init__(
        self,
        session_repo: SQLAlchemySessionRepository,
        history_repo: SQLAlchemyHistoryRepository,
        visit_repo: SQLAlchemyVisitRepository,
    ) -> None:
        self._session_repo = session_repo
        self._history_repo = history_repo
        self._visit_repo = visit_repo

    async def record_answer(
        self,
        session_id: uuid.UUID,
        question_id: str,
        question_text: str,
        answer_text: str,
        answer_source: AnswerSource,
        confidence: float | None = None,
        visit_id: uuid.UUID | None = None,
    ) -> HistoryAnswer:
        """Record a single patient answer from the kiosk conversation."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if not session.consent_given:
            raise ConsentRequiredError(session_id)

        answer = await self._history_repo.create_answer(
            session_id=session_id,
            visit_id=visit_id,
            question_id=question_id,
            question_text=question_text,
            answer_text=answer_text,
            answer_source=answer_source,
            confidence=confidence,
        )

        logger.info(
            "Answer recorded for session %s, question %s",
            session_id, question_id,
        )
        return answer

    async def get_history(self, session_id: uuid.UUID) -> ClinicalHistory | None:
        """Retrieve the current clinical history for a session."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        answers = await self._history_repo.get_answers_by_session(session_id)
        if not answers:
            return None

        # Get the visit to obtain the chief complaint
        visits = await self._visit_repo.get_by_session(session_id)
        chief_complaint = visits[0].chief_complaint if visits else "Not specified"

        return self._build_history(session_id, chief_complaint, answers)

    async def get_visit_history(
        self, visit_id: uuid.UUID
    ) -> ClinicalHistory | None:
        """Retrieve the clinical history for a specific visit."""
        visit = await self._visit_repo.get(visit_id)
        if visit is None:
            return None

        answers = await self._history_repo.get_answers_by_visit(visit_id)
        if not answers:
            return None

        return self._build_history(
            visit.session_id, visit.chief_complaint, answers
        )

    async def build_structured_history(
        self,
        session_id: uuid.UUID,
        chief_complaint: str,
    ) -> ClinicalHistory:
        """Assemble a ClinicalHistory from all recorded answers for a session."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if not session.consent_given:
            raise ConsentRequiredError(session_id)

        answers = await self._history_repo.get_answers_by_session(session_id)
        return self._build_history(session_id, chief_complaint, answers)

    @staticmethod
    def _build_history(
        session_id: uuid.UUID,
        chief_complaint: str,
        answers: list[HistoryAnswer],
    ) -> ClinicalHistory:
        """
        Build a ClinicalHistory from collected answers.

        Maps well-known question_id values to the corresponding
        ClinicalHistory fields. In Phase 7+, an LLM may enhance this mapping.
        """
        # Map question_ids to history fields
        field_map: dict[str, str | None] = {}
        list_field_map: dict[str, list[str]] = {}

        for answer in answers:
            qid = answer.question_id.lower()
            if qid in ("onset", "duration", "location", "character",
                        "radiation", "social_history"):
                field_map[qid] = answer.answer_text
            elif qid == "severity":
                try:
                    field_map["severity"] = str(int(answer.answer_text))
                except (ValueError, TypeError):
                    field_map["severity"] = None
            elif qid in ("relieving_factors", "aggravating_factors",
                          "associated_symptoms", "medications", "allergies",
                          "past_medical_history", "family_history", "red_flags"):
                list_field_map.setdefault(qid, []).append(answer.answer_text)

        severity_val = None
        if "severity" in field_map and field_map["severity"] is not None:
            try:
                s = int(field_map["severity"])
                if 1 <= s <= 10:
                    severity_val = s
            except (ValueError, TypeError):
                pass

        return ClinicalHistory(
            session_id=session_id,
            chief_complaint=chief_complaint,
            onset=field_map.get("onset"),
            duration=field_map.get("duration"),
            location=field_map.get("location"),
            character=field_map.get("character"),
            severity=severity_val,
            radiation=field_map.get("radiation"),
            relieving_factors=list_field_map.get("relieving_factors", []),
            aggravating_factors=list_field_map.get("aggravating_factors", []),
            associated_symptoms=list_field_map.get("associated_symptoms", []),
            medications=list_field_map.get("medications", []),
            allergies=list_field_map.get("allergies", []),
            past_medical_history=list_field_map.get("past_medical_history", []),
            family_history=list_field_map.get("family_history", []),
            social_history=field_map.get("social_history"),
            red_flags=list_field_map.get("red_flags", []),
            answers=answers,
        )
