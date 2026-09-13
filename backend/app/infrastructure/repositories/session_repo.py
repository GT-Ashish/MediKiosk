"""
SQLAlchemy Session Repository.

Handles persistence of KioskSession domain objects.
Maps between SessionModel (ORM) and KioskSession (Pydantic).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.session import SessionModel
from app.domain.models.patient import PatientIdentifierModel
from app.domain.schemas.session import KioskSession, SessionStatus
from app.domain.schemas.patient import PatientIdentifier, IdentifierType


class SQLAlchemySessionRepository:
    """Repository for KioskSession persistence using SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        language: str = "en",
        patient_identifier: PatientIdentifier | None = None,
    ) -> KioskSession:
        """Create a new kiosk session."""
        session_model = SessionModel(
            language=language,
            status=SessionStatus.ACTIVE.value,
            consent_given=False,
        )

        if patient_identifier is not None:
            patient_model = PatientIdentifierModel(
                session_id=session_model.id,
                identifier_type=patient_identifier.identifier_type.value,
                identifier_hash=patient_identifier.identifier_hash,
                display_name=patient_identifier.display_name,
            )
            session_model.patient_identifier = patient_model

        self._db.add(session_model)
        await self._db.flush()
        # Eagerly refresh the relationship to avoid MissingGreenlet on lazy load
        await self._db.refresh(session_model, attribute_names=["patient_identifier"])
        return self._to_domain(session_model)

    async def get(self, session_id: uuid.UUID) -> KioskSession | None:
        """Retrieve a session by ID."""
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.patient_identifier))
            .where(SessionModel.id == session_id)
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def update_status(
        self, session_id: uuid.UUID, status: SessionStatus
    ) -> KioskSession | None:
        """Update the status of a session."""
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.patient_identifier))
            .where(SessionModel.id == session_id)
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.status = status.value
        await self._db.flush()
        return self._to_domain(model)

    async def update_consent(
        self, session_id: uuid.UUID, consent_given: bool
    ) -> KioskSession | None:
        """Update the consent_given flag on a session."""
        stmt = (
            select(SessionModel)
            .options(selectinload(SessionModel.patient_identifier))
            .where(SessionModel.id == session_id)
        )
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.consent_given = consent_given
        await self._db.flush()
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: SessionModel) -> KioskSession:
        """Map a SessionModel to a KioskSession domain schema."""
        patient_id = None
        if model.patient_identifier is not None:
            patient_id = PatientIdentifier(
                identifier_type=IdentifierType(model.patient_identifier.identifier_type),
                identifier_hash=model.patient_identifier.identifier_hash,
                display_name=model.patient_identifier.display_name,
            )
        return KioskSession(
            session_id=model.id,
            created_at=model.created_at,
            language=model.language,
            status=SessionStatus(model.status),
            consent_given=model.consent_given,
            patient_identifier=patient_id,
        )
