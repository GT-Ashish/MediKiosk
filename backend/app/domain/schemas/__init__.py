"""
MediKiosk Domain Schemas.

Pydantic schema re-exports for convenient imports throughout the application.
Each module defines one or more related domain concepts.

Usage:
    from app.domain.schemas import KioskSession, ClinicalHistory, ...
"""

from app.domain.schemas.session import KioskSession, SessionStatus
from app.domain.schemas.patient import PatientIdentifier, IdentifierType
from app.domain.schemas.consent import Consent
from app.domain.schemas.visit import Visit
from app.domain.schemas.history import (
    ClinicalHistory,
    HistoryAnswer,
    AnswerSource,
)
from app.domain.schemas.document import (
    MedicalDocument,
    DocumentExtraction,
    MedicalEntity,
    DocumentStatus,
)
from app.domain.schemas.summary import StructuredHistorySummary, ReviewStatus
from app.domain.schemas.review import DoctorReview

__all__ = [
    # Session
    "KioskSession",
    "SessionStatus",
    # Patient
    "PatientIdentifier",
    "IdentifierType",
    # Consent
    "Consent",
    # Visit
    "Visit",
    # History
    "ClinicalHistory",
    "HistoryAnswer",
    "AnswerSource",
    # Document
    "MedicalDocument",
    "DocumentExtraction",
    "MedicalEntity",
    "DocumentStatus",
    # Summary
    "StructuredHistorySummary",
    "ReviewStatus",
    # Review
    "DoctorReview",
]
