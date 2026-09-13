"""
SQLAlchemy History Repository.

Handles persistence of HistoryAnswer domain objects.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.history import HistoryAnswerModel
from app.domain.schemas.history import HistoryAnswer, AnswerSource


class SQLAlchemyHistoryRepository:
    """Repository for HistoryAnswer persistence using SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_answer(
        self,
        session_id: uuid.UUID,
        visit_id: uuid.UUID | None,
        question_id: str,
        question_text: str,
        answer_text: str,
        answer_source: AnswerSource,
        confidence: float | None = None,
    ) -> HistoryAnswer:
        """Record a single patient answer."""
        model = HistoryAnswerModel(
            session_id=session_id,
            visit_id=visit_id,
            question_id=question_id,
            question_text=question_text,
            answer_text=answer_text,
            answer_source=answer_source.value,
            confidence=confidence,
        )
        self._db.add(model)
        await self._db.flush()
        return self._to_domain(model)

    async def get_answers_by_session(
        self, session_id: uuid.UUID
    ) -> list[HistoryAnswer]:
        """Retrieve all answers for a session, ordered by time."""
        stmt = (
            select(HistoryAnswerModel)
            .where(HistoryAnswerModel.session_id == session_id)
            .order_by(HistoryAnswerModel.answered_at)
        )
        result = await self._db.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_answers_by_visit(
        self, visit_id: uuid.UUID
    ) -> list[HistoryAnswer]:
        """Retrieve all answers for a visit, ordered by time."""
        stmt = (
            select(HistoryAnswerModel)
            .where(HistoryAnswerModel.visit_id == visit_id)
            .order_by(HistoryAnswerModel.answered_at)
        )
        result = await self._db.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    @staticmethod
    def _to_domain(model: HistoryAnswerModel) -> HistoryAnswer:
        """Map a HistoryAnswerModel to a HistoryAnswer domain schema."""
        return HistoryAnswer(
            question_id=model.question_id,
            question_text=model.question_text,
            answer_text=model.answer_text,
            answer_source=AnswerSource(model.answer_source),
            confidence=model.confidence,
            answered_at=model.answered_at,
        )
