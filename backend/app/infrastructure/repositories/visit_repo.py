"""
SQLAlchemy Visit Repository.

Handles persistence of Visit domain objects.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.visit import VisitModel
from app.domain.schemas.visit import Visit


class SQLAlchemyVisitRepository:
    """Repository for Visit persistence using SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        session_id: uuid.UUID,
        chief_complaint: str,
        department: str | None = None,
    ) -> Visit:
        """Create a new visit record."""
        model = VisitModel(
            session_id=session_id,
            chief_complaint=chief_complaint,
            department=department,
        )
        self._db.add(model)
        await self._db.flush()
        return self._to_domain(model)

    async def get(self, visit_id: uuid.UUID) -> Visit | None:
        """Retrieve a visit by ID."""
        stmt = select(VisitModel).where(VisitModel.id == visit_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_session(self, session_id: uuid.UUID) -> list[Visit]:
        """Retrieve all visits for a session."""
        stmt = (
            select(VisitModel)
            .where(VisitModel.session_id == session_id)
            .order_by(VisitModel.created_at)
        )
        result = await self._db.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    @staticmethod
    def _to_domain(model: VisitModel) -> Visit:
        """Map a VisitModel to a Visit domain schema."""
        return Visit(
            visit_id=model.id,
            session_id=model.session_id,
            chief_complaint=model.chief_complaint,
            department=model.department,
        )
