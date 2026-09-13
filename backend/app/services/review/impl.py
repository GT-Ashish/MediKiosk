"""
ReviewService — Concrete Implementation (Stub).

Phase 6: Physician review depends on AI-generated summaries.
Since summary generation is deferred to Phase 7, review submission
is also deferred.
"""

import uuid

from app.domain.schemas.review import DoctorReview
from app.domain.schemas.summary import ReviewStatus
from app.utils.errors import UnsupportedOperationError


class ReviewServiceImpl:
    """
    Stub implementation of the ReviewService Protocol.

    Physician review requires summaries, which require AI (Phase 7).
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
        Submit a physician review.

        NOT IMPLEMENTED in Phase 6 — requires AI summary generation (Phase 7).
        """
        raise UnsupportedOperationError(
            "Physician review submission is not yet implemented. "
            "This feature requires AI summary generation (Phase 7)."
        )

    async def get_review(
        self,
        summary_id: uuid.UUID,
    ) -> DoctorReview | None:
        """
        Retrieve a review for a summary.

        No reviews exist in Phase 6 since submission is not implemented.
        """
        return None
