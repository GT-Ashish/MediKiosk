"""
MediKiosk API v1 Router.

Central router for all /api/v1/* endpoints.

This is the stable registration point for all versioned API endpoints.
Adding a new feature requires only:
    1. Creating the endpoint module in api/v1/<feature>.py
    2. Including its router here with an appropriate prefix and tags.

No endpoint modules are mounted yet — they will be added in Phase 6
when database-backed implementations are available.

Planned v1 endpoints (Phase 6):
    /api/v1/sessions    — KioskSession lifecycle
    /api/v1/visits      — Visit and chief complaint
    /api/v1/history     — Clinical history answers
    /api/v1/documents   — Document upload and retrieval
    /api/v1/summaries   — AI-generated summaries
    /api/v1/reviews     — Doctor reviews
"""

from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")

# ── Future endpoint registrations (Phase 6) ───────────────────────────────────
# from app.api.v1 import sessions, visits, history, documents, summaries, reviews
# v1_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
# v1_router.include_router(visits.router, prefix="/visits", tags=["visits"])
# v1_router.include_router(history.router, prefix="/history", tags=["history"])
# v1_router.include_router(documents.router, prefix="/documents", tags=["documents"])
# v1_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
# v1_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
