"""
FastAPI Dependency Injection.

Wires the full stack: DB session → Repositories → Services.

This is the single place where the dependency graph is assembled.
The API layer uses these dependencies via FastAPI's Depends() system.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db_session
from app.infrastructure.repositories.session_repo import SQLAlchemySessionRepository
from app.infrastructure.repositories.consent_repo import SQLAlchemyConsentRepository
from app.infrastructure.repositories.visit_repo import SQLAlchemyVisitRepository
from app.infrastructure.repositories.history_repo import SQLAlchemyHistoryRepository
from app.infrastructure.repositories.document_repo import SQLAlchemyDocumentRepository
from app.services.session.impl import SessionServiceImpl
from app.services.history.impl import HistoryServiceImpl
from app.services.documents.impl import DocumentServiceImpl
from app.services.summary.impl import SummaryServiceImpl
from app.services.review.impl import ReviewServiceImpl


async def get_db(
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the request."""
    async for session in get_db_session():
        yield session


def get_session_service(
    db: AsyncSession = Depends(get_db),
) -> SessionServiceImpl:
    """Build a SessionServiceImpl with injected repositories."""
    session_repo = SQLAlchemySessionRepository(db)
    consent_repo = SQLAlchemyConsentRepository(db)
    return SessionServiceImpl(
        session_repo=session_repo,
        consent_repo=consent_repo,
    )


def get_history_service(
    db: AsyncSession = Depends(get_db),
) -> HistoryServiceImpl:
    """Build a HistoryServiceImpl with injected repositories."""
    session_repo = SQLAlchemySessionRepository(db)
    history_repo = SQLAlchemyHistoryRepository(db)
    visit_repo = SQLAlchemyVisitRepository(db)
    return HistoryServiceImpl(
        session_repo=session_repo,
        history_repo=history_repo,
        visit_repo=visit_repo,
    )


def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentServiceImpl:
    """Build a DocumentServiceImpl with injected repositories."""
    session_repo = SQLAlchemySessionRepository(db)
    document_repo = SQLAlchemyDocumentRepository(db)
    return DocumentServiceImpl(
        session_repo=session_repo,
        document_repo=document_repo,
    )


def get_visit_service(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyVisitRepository:
    """Build a VisitRepository for visit endpoints."""
    return SQLAlchemyVisitRepository(db)


def get_summary_service() -> SummaryServiceImpl:
    """Build a SummaryServiceImpl (stub — no repos needed in Phase 6)."""
    return SummaryServiceImpl()


def get_review_service() -> ReviewServiceImpl:
    """Build a ReviewServiceImpl (stub — no repos needed in Phase 6)."""
    return ReviewServiceImpl()
