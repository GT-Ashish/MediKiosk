"""
History API Endpoints.

POST /api/v1/visits/{visit_id}/answers — Record a clinical answer
GET  /api/v1/visits/{visit_id}/history — Get structured clinical history
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_history_service, get_visit_service
from app.api.v1.api_schemas import (
    RecordAnswerRequest,
    HistoryAnswerResponse,
    ErrorResponse,
)
from app.infrastructure.repositories.visit_repo import SQLAlchemyVisitRepository
from app.services.history.impl import HistoryServiceImpl
from app.utils.errors import SessionNotFoundError, ConsentRequiredError

router = APIRouter()


@router.post(
    "/visits/{visit_id}/answers",
    response_model=HistoryAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Record a clinical answer",
)
async def record_answer(
    visit_id: uuid.UUID,
    body: RecordAnswerRequest,
    history_service: HistoryServiceImpl = Depends(get_history_service),
    visit_repo: SQLAlchemyVisitRepository = Depends(get_visit_service),
) -> HistoryAnswerResponse:
    """Record a single Q&A exchange from the kiosk conversation."""
    # Verify visit exists
    visit = await visit_repo.get(visit_id)
    if visit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found.",
        )

    try:
        answer = await history_service.record_answer(
            session_id=body.session_id,
            question_id=body.question_id,
            question_text=body.question_text,
            answer_text=body.answer_text,
            answer_source=body.answer_source,
            confidence=body.confidence,
            visit_id=visit_id,
        )
        return HistoryAnswerResponse(
            question_id=answer.question_id,
            question_text=answer.question_text,
            answer_text=answer.answer_text,
            answer_source=answer.answer_source.value,
            confidence=answer.confidence,
            answered_at=answer.answered_at,
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    except ConsentRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required before recording clinical answers.",
        )


@router.get(
    "/visits/{visit_id}/history",
    responses={404: {"model": ErrorResponse}},
    summary="Get clinical history for a visit",
)
async def get_visit_history(
    visit_id: uuid.UUID,
    history_service: HistoryServiceImpl = Depends(get_history_service),
    visit_repo: SQLAlchemyVisitRepository = Depends(get_visit_service),
):
    """Retrieve the structured clinical history for a visit."""
    visit = await visit_repo.get(visit_id)
    if visit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found.",
        )

    history = await history_service.get_visit_history(visit_id)
    if history is None:
        return {"message": "No history answers recorded yet.", "answers": []}

    return history.model_dump()
