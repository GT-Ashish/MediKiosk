"""
MediKiosk Infrastructure — Repositories.

SQLAlchemy-backed repository implementations for Phase 6.
Each repository implements persistence for a domain concept and handles
mapping between ORM models and Pydantic domain schemas.

Design pattern:
    Each repository takes an AsyncSession via constructor injection.
    The FastAPI dependency system wires the session per-request.
"""

from app.infrastructure.repositories.session_repo import SQLAlchemySessionRepository
from app.infrastructure.repositories.consent_repo import SQLAlchemyConsentRepository
from app.infrastructure.repositories.visit_repo import SQLAlchemyVisitRepository
from app.infrastructure.repositories.history_repo import SQLAlchemyHistoryRepository
from app.infrastructure.repositories.document_repo import SQLAlchemyDocumentRepository

__all__ = [
    "SQLAlchemySessionRepository",
    "SQLAlchemyConsentRepository",
    "SQLAlchemyVisitRepository",
    "SQLAlchemyHistoryRepository",
    "SQLAlchemyDocumentRepository",
]
