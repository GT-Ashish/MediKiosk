"""
Visit API Endpoints.

POST /api/v1/sessions/{session_id}/visits — Create a visit
GET  /api/v1/visits/{visit_id}            — Get visit details
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_session_service, get_visit_service
from app.api.v1.api_schemas import CreateVisitRequest, VisitResponse, ErrorResponse
from app.infrastructure.repositories.visit_repo import SQLAlchemyVisitRepository
from app.services.session.impl import SessionServiceImpl
from app.utils.errors import SessionNotFoundError

router = APIRouter()


@router.post(
    "/sessions/{session_id}/visits",
    response_model=VisitResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Create a clinical visit",
)
async def create_visit(
    session_id: uuid.UUID,
    body: CreateVisitRequest,
    session_service: SessionServiceImpl = Depends(get_session_service),
    visit_repo: SQLAlchemyVisitRepository = Depends(get_visit_service),
) -> VisitResponse:
    """Create a new clinical visit within a session."""
    session = await session_service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    if not session.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required before creating a visit.",
        )

    visit = await visit_repo.create(
        session_id=session_id,
        chief_complaint=body.chief_complaint,
        department=body.department,
    )
    return VisitResponse(
        visit_id=visit.visit_id,
        session_id=visit.session_id,
        chief_complaint=visit.chief_complaint,
        department=visit.department,
    )


@router.get(
    "/visits/{visit_id}",
    response_model=VisitResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get visit details",
)
async def get_visit(
    visit_id: uuid.UUID,
    visit_repo: SQLAlchemyVisitRepository = Depends(get_visit_service),
) -> VisitResponse:
    """Retrieve a clinical visit by ID."""
    visit = await visit_repo.get(visit_id)
    if visit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found.",
        )
    return VisitResponse(
        visit_id=visit.visit_id,
        session_id=visit.session_id,
        chief_complaint=visit.chief_complaint,
        department=visit.department,
    )
