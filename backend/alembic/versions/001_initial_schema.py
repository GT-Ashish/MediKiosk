"""001_initial_schema

Revision ID: 001_initial
Revises:
Create Date: 2026-09-13

Phase 6: Initial database schema for MediKiosk.

Creates:
  - kiosk_sessions: Patient interaction sessions
  - patient_identifiers: Privacy-preserving patient references
  - consents: Informed consent records
  - visits: Clinical encounters within sessions
  - history_answers: Q&A exchanges from kiosk conversation
  - medical_documents: Document metadata (file storage deferred to Phase 8)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the Phase 6 database schema."""

    # ── kiosk_sessions ────────────────────────────────────────────────────────
    op.create_table(
        "kiosk_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("consent_given", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kiosk_sessions_status", "kiosk_sessions", ["status"])

    # ── patient_identifiers ───────────────────────────────────────────────────
    op.create_table(
        "patient_identifiers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("identifier_type", sa.String(20), nullable=False),
        sa.Column("identifier_hash", sa.String(64), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_patient_identifiers_session_id", "patient_identifiers", ["session_id"])

    # ── consents ──────────────────────────────────────────────────────────────
    op.create_table(
        "consents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consent_version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("data_use_acknowledged", sa.Boolean(), nullable=False),
        sa.Column("ai_processing_acknowledged", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_consents_session_id", "consents", ["session_id"])

    # ── visits ────────────────────────────────────────────────────────────────
    op.create_table(
        "visits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("chief_complaint", sa.Text(), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_visits_session_id", "visits", ["session_id"])

    # ── history_answers ───────────────────────────────────────────────────────
    op.create_table(
        "history_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("visit_id", sa.Uuid(), nullable=True),
        sa.Column("question_id", sa.String(100), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("answer_source", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["visit_id"], ["visits.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_history_answers_session_id", "history_answers", ["session_id"])
    op.create_index("ix_history_answers_visit_id", "history_answers", ["visit_id"])

    # ── medical_documents ─────────────────────────────────────────────────────
    op.create_table(
        "medical_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processing_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_medical_documents_session_id", "medical_documents", ["session_id"])


def downgrade() -> None:
    """Drop all Phase 6 tables."""
    op.drop_table("medical_documents")
    op.drop_table("history_answers")
    op.drop_table("visits")
    op.drop_table("consents")
    op.drop_table("patient_identifiers")
    op.drop_table("kiosk_sessions")
