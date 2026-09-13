"""
MediKiosk API v1 Router.

Central router for all /api/v1/* endpoints.

This is the stable registration point for all versioned API endpoints.
Adding a new feature requires only:
    1. Creating the endpoint module in api/v1/<feature>.py
    2. Including its router here with an appropriate prefix and tags.

Phase 6 endpoints:
    /api/v1/sessions    — KioskSession lifecycle
    /api/v1/sessions/*/visits — Visit creation
    /api/v1/visits/*    — Visit retrieval, history answers
    /api/v1/sessions/*/documents — Document registration/listing
    /api/v1/documents/* — Document retrieval
"""

from fastapi import APIRouter

from app.api.v1 import sessions, visits, history, documents

v1_router = APIRouter(prefix="/v1")

# Session lifecycle endpoints
v1_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# Visit and history endpoints — uses mixed prefixes so included at v1 root
v1_router.include_router(visits.router, tags=["visits"])
v1_router.include_router(history.router, tags=["history"])

# Document endpoints — uses mixed prefixes so included at v1 root
v1_router.include_router(documents.router, tags=["documents"])
