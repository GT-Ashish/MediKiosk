"""
KioskSession — Domain Schema.

Represents an active patient interaction at the MediKiosk terminal.
A session is the top-level container for everything that happens during
one patient visit: consent, identity, history elicitation, documents,
and the eventual AI-generated summary sent to the doctor.

Lifecycle:
    ACTIVE → COMPLETED  (normal flow)
    ACTIVE → ABANDONED  (patient left / timeout)

Privacy notes:
    - The session_id is the only persistent reference across the system.
    - No raw Aadhaar numbers or biometric data are stored here.
    - patient_identifier references only a hashed/anonymised identifier.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.schemas.patient import PatientIdentifier


class SessionStatus(str, Enum):
    """Lifecycle states of a kiosk session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class KioskSession(BaseModel):
    """
    A single patient interaction at the MediKiosk terminal.

    Created when the patient starts a session.
    Completed when the patient confirms and exits.
    Abandoned if the session times out or the patient walks away.
    """

    session_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this kiosk session.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session started.",
    )
    language: str = Field(
        default="en",
        description="BCP-47 language code chosen by the patient (e.g. 'en', 'hi', 'ta').",
    )
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="Current lifecycle status of the session.",
    )
    consent_given: bool = Field(
        default=False,
        description="Whether the patient has provided informed consent for data processing.",
    )
    # Uses Any to avoid circular import — validated at schema level via PatientIdentifier
    patient_identifier: Any | None = Field(
        default=None,
        description=(
            "Optional anonymised patient reference (PatientIdentifier). "
            "May be None for walk-in patients."
        ),
    )

    model_config = {"frozen": False}
