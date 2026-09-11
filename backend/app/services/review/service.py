"""
ReviewService — Service Protocol.

Defines the interface for physician review of AI-generated summaries.

The ReviewService is responsible for:
    - Accepting physician review submissions from the doctor dashboard
    - Retrieving review records
    - Updating the review status of a StructuredHistorySummary

Authentication note:
    reviewer_id is currently an opaque string. Full authentication and
    physician identity verification are deferred to Phase 6+.

Clinical record note:
    A submitted DoctorReview with status=REVIEWED represents the physician's
    explicit acceptance of the AI-generated history. This is the closest
    to a clinical sign-off in the current prototype.

Implementation note (Phase 6):
    Concrete implementation will be InMemoryReviewService.
"""

import uuid
from typing import Protocol

from app.domain.schemas.review import DoctorReview
from app.domain.schemas.summary import ReviewStatus


class ReviewService(Protocol):
    """
    Interface for physician review of AI-generated clinical summaries.
    """

    async def submit_review(
        self,
        summary_id: uuid.UUID,
        reviewer_id: str,
        status: ReviewStatus,
        notes: str | None = None,
        corrections: dict[str, str] | None = None,
    ) -> DoctorReview:
        """
        Submit a physician's review of an AI-generated summary.

        Updates the summary's review_status to match the submitted status.
        For REJECTED reviews, notes should explain why.
        For REVIEWED reviews with corrections, corrections dict is populated.

        Args:
            summary_id: The summary being reviewed.
            reviewer_id: Opaque physician identifier.
            status: REVIEWED (accepted) or REJECTED.
            notes: Optional physician notes.
            corrections: Optional field-level corrections (field_name → corrected_text).

        Returns:
            The created DoctorReview record.
        Raises:
            ValueError: If summary_id does not exist.
            ValueError: If status is DRAFT or UNDER_REVIEW (invalid for submission).
        """
        ...

    async def get_review(
        self,
        summary_id: uuid.UUID,
    ) -> DoctorReview | None:
        """
        Retrieve the physician review for a given summary.

        Args:
            summary_id: The summary to retrieve the review for.

        Returns:
            The DoctorReview if submitted, None otherwise.
        """
        ...
