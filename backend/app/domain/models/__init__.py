"""
MediKiosk Domain Models Package.

ORM models for PostgreSQL persistence via SQLAlchemy 2.x.
All models inherit from the shared DeclarativeBase in infrastructure/database.py.

These models are SEPARATE from Pydantic domain schemas in domain/schemas/.
Repositories handle mapping between ORM models and domain schemas.

Importing this module registers all models with Base.metadata,
which is required for Alembic migration auto-generation.
"""

from app.domain.models.session import SessionModel
from app.domain.models.patient import PatientIdentifierModel
from app.domain.models.consent import ConsentModel
from app.domain.models.visit import VisitModel
from app.domain.models.history import HistoryAnswerModel
from app.domain.models.document import DocumentModel

__all__ = [
    "SessionModel",
    "PatientIdentifierModel",
    "ConsentModel",
    "VisitModel",
    "HistoryAnswerModel",
    "DocumentModel",
]
