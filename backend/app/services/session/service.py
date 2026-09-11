"""
SessionService — Service Protocol.

Defines the interface for kiosk session lifecycle management.

A kiosk session is the outermost container of a patient interaction.
This service is responsible for creating, retrieving, and terminating sessions.

Implementation note (Phase 6):
    The concrete implementation will be InMemorySessionService (Phase 6)
    and later DatabaseSessionService (Phase 6+). Both must implement this Protocol.

Session lifecycle:
    create_session()   → KioskSession (status=ACTIVE)
    get_session()      → KioskSession | None
    complete_session() → KioskSession (status=COMPLETED)
    abandon_session()  → KioskSession (status=ABANDONED)

Privacy note:
    Sessions must be terminated (COMPLETED or ABANDONED) to clear
    patient data from any in-memory state. When the database is added,
    completed sessions should have their in-memory state purged.
"""

import uuid
from typing import Protocol

from app.domain.schemas.session import KioskSession
from app.domain.schemas.patient import PatientIdentifier


class SessionService(Protocol):
    """
    Interface for managing kiosk session lifecycle.

    All concrete session service implementations must satisfy this Protocol.
    """

    async def create_session(
        self,
        language: str = "en",
        patient_identifier: PatientIdentifier | None = None,
    ) -> KioskSession:
        """
        Create and register a new kiosk session.

        Args:
            language: BCP-47 language code for this session (default: 'en').
            patient_identifier: Optional anonymised patient reference.
                                 May be None for walk-in patients.

        Returns:
            A new KioskSession with status=ACTIVE.
        """
        ...

    async def get_session(self, session_id: uuid.UUID) -> KioskSession | None:
        """
        Retrieve an existing session by ID.

        Args:
            session_id: The UUID of the session to retrieve.

        Returns:
            The KioskSession if found, None otherwise.
        """
        ...

    async def record_consent(
        self,
        session_id: uuid.UUID,
        data_use_acknowledged: bool,
        ai_processing_acknowledged: bool,
    ) -> KioskSession:
        """
        Record that the patient has given informed consent.

        Both data_use_acknowledged and ai_processing_acknowledged must be True.
        Raises ConsentRequiredError if either is False.
        Raises SessionNotFoundError if the session does not exist.

        Args:
            session_id: The session to record consent for.
            data_use_acknowledged: Patient acknowledged data use policy.
            ai_processing_acknowledged: Patient acknowledged AI processing.

        Returns:
            The updated KioskSession with consent_given=True.
        """
        ...

    async def complete_session(self, session_id: uuid.UUID) -> KioskSession:
        """
        Mark a session as COMPLETED (patient confirmed and exited).

        Raises SessionNotFoundError if the session does not exist.

        Args:
            session_id: The session to complete.

        Returns:
            The updated KioskSession with status=COMPLETED.
        """
        ...

    async def abandon_session(self, session_id: uuid.UUID) -> KioskSession:
        """
        Mark a session as ABANDONED (timeout or patient left).

        Raises SessionNotFoundError if the session does not exist.

        Args:
            session_id: The session to abandon.

        Returns:
            The updated KioskSession with status=ABANDONED.
        """
        ...
