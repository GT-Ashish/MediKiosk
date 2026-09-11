"""
MediKiosk API Router.

Central API router that aggregates all versioned route modules.

Route organisation:
    /api/health     — Health check (unversioned, always available)
    /api/v1/*       — All versioned endpoints (Phase 6+)
"""

from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1.router import v1_router

api_router = APIRouter()

# Health check — unversioned, mounted at /api/health
api_router.include_router(health.router, tags=["health"])

# Versioned API — all Phase 6+ endpoints register through v1_router
# This mounts the entire /api/v1/* namespace
api_router.include_router(v1_router)
