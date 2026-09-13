"""
SQLAlchemy Consent Repository.

Handles persistence of Consent domain objects.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.consent import ConsentModel
from app.domain.schemas.consent import Consent


class SQLAlchemyConsentRepository:
    """Repository for Consent persistence using SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, consent: Consent) -> Consent:
        """Create a new consent record."""
        model = ConsentModel(
            session_id=consent.session_id,
            consented_at=consent.consented_at,
            consent_version=consent.consent_version,
            data_use_acknowledged=consent.data_use_acknowledged,
            ai_processing_acknowledged=consent.ai_processing_acknowledged,
        )
        self._db.add(model)
        await self._db.flush()
        return self._to_domain(model)

    async def get_by_session(self, session_id: uuid.UUID) -> Consent | None:
        """Retrieve the consent record for a session."""
        stmt = select(ConsentModel).where(ConsentModel.session_id == session_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ConsentModel) -> Consent:
        """Map a ConsentModel to a Consent domain schema."""
        return Consent(
            session_id=model.session_id,
            consented_at=model.consented_at,
            consent_version=model.consent_version,
            data_use_acknowledged=model.data_use_acknowledged,
            ai_processing_acknowledged=model.ai_processing_acknowledged,
        )
