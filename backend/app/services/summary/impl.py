"""
SummaryService — Concrete Implementation (Stub).

Phase 6: AI generation is not implemented. This service clearly
signals that summary generation is deferred.
"""

import uuid

from app.domain.schemas.summary import StructuredHistorySummary
from app.utils.errors import UnsupportedOperationError


class SummaryServiceImpl:
    """
    Stub implementation of the SummaryService Protocol.

    AI-generated summaries are deferred to Phase 7.
    """

    async def generate_summary(
        self,
        session_id: uuid.UUID,
    ) -> StructuredHistorySummary:
        """
        Generate an AI-assisted summary.

        NOT IMPLEMENTED in Phase 6 — requires AI integration (Phase 7).
        """
        raise UnsupportedOperationError(
            "AI summary generation is not yet implemented. "
            "This feature will be available in Phase 7."
        )

    async def get_summary(
        self,
        session_id: uuid.UUID,
    ) -> StructuredHistorySummary | None:
        """
        Retrieve a summary for a session.

        No summaries exist in Phase 6 since generation is not implemented.
        """
        return None
