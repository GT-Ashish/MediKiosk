"""
MediKiosk API Router.

Central API router that aggregates all versioned route modules.
"""

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()

# Health check — unversioned, mounted at /api/health
api_router.include_router(health.router, tags=["health"])
