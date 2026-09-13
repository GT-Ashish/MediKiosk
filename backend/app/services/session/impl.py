"""
SessionService — Concrete Implementation.

Implements the SessionService Protocol using repository pattern.
Business logic lives here; database logic lives in the repository.
"""

import uuid

from app.domain.schemas.session import KioskSession, SessionStatus
from app.domain.schemas.consent import Consent
from app.domain.schemas.patient import PatientIdentifier
from app.infrastructure.repositories.session_repo import SQLAlchemySessionRepository
from app.infrastructure.repositories.consent_repo import SQLAlchemyConsentRepository
from app.utils.errors import SessionNotFoundError, ConsentRequiredError, MediKioskValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SessionServiceImpl:
    """
    Concrete implementation of the SessionService Protocol.

    Coordinates session lifecycle through the session and consent repositories.
    """

    def __init__(
        self,
        session_repo: SQLAlchemySessionRepository,
        consent_repo: SQLAlchemyConsentRepository,
    ) -> None:
        self._session_repo = session_repo
        self._consent_repo = consent_repo

    async def create_session(
        self,
        language: str = "en",
        patient_identifier: PatientIdentifier | None = None,
    ) -> KioskSession:
        """Create and register a new kiosk session."""
        session = await self._session_repo.create(
            language=language,
            patient_identifier=patient_identifier,
        )
        logger.info("Session created: %s", session.session_id)
        return session

    async def get_session(self, session_id: uuid.UUID) -> KioskSession | None:
        """Retrieve an existing session by ID."""
        return await self._session_repo.get(session_id)

    async def record_consent(
        self,
        session_id: uuid.UUID,
        data_use_acknowledged: bool,
        ai_processing_acknowledged: bool,
    ) -> KioskSession:
        """
        Record that the patient has given informed consent.

        Both acknowledgements must be True. Raises ConsentRequiredError otherwise.
        """
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if session.status != SessionStatus.ACTIVE:
            raise MediKioskValidationError(
                f"Cannot record consent on a {session.status.value} session.",
                field="status",
            )

        if not data_use_acknowledged or not ai_processing_acknowledged:
            raise ConsentRequiredError(session_id)

        # Create the consent record
        consent = Consent(
            session_id=session_id,
            data_use_acknowledged=data_use_acknowledged,
            ai_processing_acknowledged=ai_processing_acknowledged,
        )
        await self._consent_repo.create(consent)

        # Update the session flag
        updated = await self._session_repo.update_consent(session_id, True)
        if updated is None:
            raise SessionNotFoundError(session_id)

        logger.info("Consent recorded for session: %s", session_id)
        return updated

    async def complete_session(self, session_id: uuid.UUID) -> KioskSession:
        """Mark a session as COMPLETED."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if session.status != SessionStatus.ACTIVE:
            raise MediKioskValidationError(
                f"Cannot complete a {session.status.value} session.",
                field="status",
            )

        updated = await self._session_repo.update_status(
            session_id, SessionStatus.COMPLETED
        )
        if updated is None:
            raise SessionNotFoundError(session_id)

        logger.info("Session completed: %s", session_id)
        return updated

    async def abandon_session(self, session_id: uuid.UUID) -> KioskSession:
        """Mark a session as ABANDONED."""
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)

        if session.status != SessionStatus.ACTIVE:
            raise MediKioskValidationError(
                f"Cannot abandon a {session.status.value} session.",
                field="status",
            )

        updated = await self._session_repo.update_status(
            session_id, SessionStatus.ABANDONED
        )
        if updated is None:
            raise SessionNotFoundError(session_id)

        logger.info("Session abandoned: %s", session_id)
        return updated
