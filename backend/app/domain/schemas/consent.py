"""
Consent — Domain Schema.

Records a patient's informed consent for data processing within a MediKiosk session.

Consent architecture:
    - Consent is mandatory before any clinical data is collected.
    - Two explicit acknowledgements are required:
        1. data_use_acknowledged — patient understands their data will be processed.
        2. ai_processing_acknowledged — patient understands AI will assist with
           history elicitation and summarisation.
    - AI-generated summaries are explicitly marked as drafts requiring physician review.
    - Consent version is versioned so that policy changes can be tracked.
    - Consent records are tied to a session_id, not to a persistent patient record,
      since persistent identity is deferred.

Future note:
    When ABDM integration is implemented, consent records may need to conform
    to the ABDM Consent Framework. This schema intentionally leaves room for that.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Consent(BaseModel):
    """
    Patient informed consent record for a kiosk session.

    Both ai_processing_acknowledged and data_use_acknowledged must be True
    before the clinical history workflow begins. The service layer enforces this.
    """

    session_id: uuid.UUID = Field(
        description="The kiosk session this consent belongs to.",
    )
    consented_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when consent was recorded.",
    )
    consent_version: str = Field(
        default="1.0",
        description=(
            "Version of the consent policy the patient agreed to. "
            "Increment when the consent text changes materially."
        ),
    )
    data_use_acknowledged: bool = Field(
        description=(
            "Patient explicitly acknowledged that their clinical data will be "
            "processed to generate a structured history for their doctor."
        ),
    )
    ai_processing_acknowledged: bool = Field(
        description=(
            "Patient explicitly acknowledged that AI will assist with history "
            "elicitation and that AI-generated outputs require physician review."
        ),
    )
