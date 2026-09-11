"""
Visit — Domain Schema.

Represents a single clinical encounter within a kiosk session.
A Visit is initiated after consent is confirmed and the patient
describes their chief complaint.

Relationship:
    KioskSession 1 → 1 Visit (in the current prototype)
    Future: a session could potentially contain multiple visit intents,
    but for SIH 2026 we model one session as one visit.

Note:
    ClinicalHistory is optional at Visit creation — it is progressively
    built during the conversation and attached when complete.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.schemas.history import ClinicalHistory


class Visit(BaseModel):
    """
    A single clinical encounter for a patient.

    Stores the top-level visit information and links to the full
    structured clinical history once it has been collected.
    """

    visit_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this visit.",
    )
    session_id: uuid.UUID = Field(
        description="The kiosk session that initiated this visit.",
    )
    chief_complaint: str = Field(
        description=(
            "The patient's primary reason for visiting, in their own words. "
            "This is the starting point for the structured history workflow."
        ),
    )
    department: str | None = Field(
        default=None,
        description=(
            "Optional target department or specialty (e.g., 'Cardiology', 'General OPD'). "
            "Used for routing in multi-department setups."
        ),
    )
    # Uses Any to avoid circular import — actual type is ClinicalHistory
    clinical_history: object | None = Field(
        default=None,
        description=(
            "The structured clinical history collected during the session (ClinicalHistory). "
            "None until the history elicitation workflow is complete."
        ),
    )
