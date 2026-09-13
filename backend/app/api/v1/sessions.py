"""
Session API Endpoints.

POST /api/v1/sessions                      — Create a new kiosk session
GET  /api/v1/sessions/{session_id}         — Get session details
POST /api/v1/sessions/{session_id}/consent — Record patient consent
POST /api/v1/sessions/{session_id}/complete — Complete a session
POST /api/v1/sessions/{session_id}/abandon  — Abandon a session
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_session_service
from app.api.v1.api_schemas import (
    CreateSessionRequest,
    ConsentRequest,
    SessionResponse,
    PatientIdentifierRequest,
    ErrorResponse,
)
from app.domain.schemas.patient import PatientIdentifier
from app.services.session.impl import SessionServiceImpl
from app.utils.errors import (
    SessionNotFoundError,
    ConsentRequiredError,
    MediKioskValidationError,
)

router = APIRouter()


def _session_to_response(session) -> SessionResponse:
    """Convert a KioskSession to a SessionResponse."""
    patient_id = None
    if session.patient_identifier is not None:
        pi = session.patient_identifier
        patient_id = PatientIdentifierRequest(
            identifier_type=pi.identifier_type,
            identifier_hash=pi.identifier_hash,
            display_name=pi.display_name,
        )
    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        language=session.language,
        status=session.status.value,
        consent_given=session.consent_given,
        patient_identifier=patient_id,
    )


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
    summary="Create a new kiosk session",
)
async def create_session(
    body: CreateSessionRequest,
    service: SessionServiceImpl = Depends(get_session_service),
) -> SessionResponse:
    """Create a new kiosk session for a patient interaction."""
    patient_id = None
    if body.patient_identifier is not None:
        patient_id = PatientIdentifier(
            identifier_type=body.patient_identifier.identifier_type,
            identifier_hash=body.patient_identifier.identifier_hash,
            display_name=body.patient_identifier.display_name,
        )

    session = await service.create_session(
        language=body.language,
        patient_identifier=patient_id,
    )
    return _session_to_response(session)


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get session details",
)
async def get_session(
    session_id: uuid.UUID,
    service: SessionServiceImpl = Depends(get_session_service),
) -> SessionResponse:
    """Retrieve an existing kiosk session by ID."""
    session = await service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    return _session_to_response(session)


@router.post(
    "/{session_id}/consent",
    response_model=SessionResponse,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Record patient consent",
)
async def record_consent(
    session_id: uuid.UUID,
    body: ConsentRequest,
    service: SessionServiceImpl = Depends(get_session_service),
) -> SessionResponse:
    """Record informed consent for a kiosk session."""
    try:
        session = await service.record_consent(
            session_id=session_id,
            data_use_acknowledged=body.data_use_acknowledged,
            ai_processing_acknowledged=body.ai_processing_acknowledged,
        )
        return _session_to_response(session)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    except ConsentRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Both data_use_acknowledged and ai_processing_acknowledged must be true.",
        )
    except MediKioskValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message,
        )


@router.post(
    "/{session_id}/complete",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Complete a session",
)
async def complete_session(
    session_id: uuid.UUID,
    service: SessionServiceImpl = Depends(get_session_service),
) -> SessionResponse:
    """Mark a session as completed (patient confirmed and exited)."""
    try:
        session = await service.complete_session(session_id)
        return _session_to_response(session)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    except MediKioskValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message,
        )


@router.post(
    "/{session_id}/abandon",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Abandon a session",
)
async def abandon_session(
    session_id: uuid.UUID,
    service: SessionServiceImpl = Depends(get_session_service),
) -> SessionResponse:
    """Mark a session as abandoned (timeout or patient left)."""
    try:
        session = await service.abandon_session(session_id)
        return _session_to_response(session)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    except MediKioskValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message,
        )
