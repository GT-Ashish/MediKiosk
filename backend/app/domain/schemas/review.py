"""
DoctorReview — Domain Schema.

Records a physician's review of an AI-generated StructuredHistorySummary.

A DoctorReview is created when the physician interacts with the summary
in the doctor dashboard. The doctor can:
    - Accept the summary as-is (status → REVIEWED)
    - Accept with corrections (status → REVIEWED, corrections populated)
    - Reject the summary (status → REJECTED, notes explaining why)

Authentication note:
    reviewer_id is an opaque string for now. Authentication and physician
    identity verification are deferred to Phase 6+. In the prototype,
    the doctor dashboard is accessed without authentication (SIH demo scope).

Clinical record note:
    A REVIEWED DoctorReview is the closest thing to a clinical record
    in the current MediKiosk prototype. It represents the physician's
    explicit sign-off on the AI-generated history.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.domain.schemas.summary import ReviewStatus


class DoctorReview(BaseModel):
    """
    Physician review of an AI-generated clinical history summary.

    Created when the doctor submits their review via the doctor dashboard.
    Links back to the summary via summary_id.
    """

    review_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this review record.",
    )
    summary_id: uuid.UUID = Field(
        description="The StructuredHistorySummary being reviewed.",
    )
    reviewed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the review was submitted.",
    )
    reviewer_id: str = Field(
        description=(
            "Opaque identifier for the reviewing physician. "
            "Authentication deferred to Phase 6+. "
            "In the prototype, this may be a static doctor ID."
        ),
    )
    status: ReviewStatus = Field(
        description="The outcome of this review (REVIEWED or REJECTED).",
    )
    notes: str | None = Field(
        default=None,
        description=(
            "Optional physician notes on the summary. "
            "For REJECTED reviews, should explain why the summary was rejected."
        ),
    )
    corrections: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Field-level corrections made by the physician. "
            "Keys are field names from StructuredHistorySummary "
            "(e.g., 'history_narrative', 'chief_complaint'), "
            "values are the corrected text."
        ),
    )
