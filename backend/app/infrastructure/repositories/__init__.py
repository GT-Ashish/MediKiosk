"""
MediKiosk Infrastructure — Repositories.

Repository classes will be implemented here in Phase 6 (PostgreSQL + SQLAlchemy).

Each repository will implement a corresponding service protocol interface,
providing database-backed persistence for sessions, history, documents, etc.

Planned repositories (Phase 6):
    SessionRepository     — implements SessionService protocol
    HistoryRepository     — implements HistoryService protocol
    DocumentRepository    — implements DocumentService protocol
    SummaryRepository     — implements SummaryService protocol
    ReviewRepository      — implements ReviewService protocol

Design pattern:
    Each repository takes a database session (AsyncSession) via dependency injection.
    The FastAPI dependency system wires the session per-request.

Current status: Empty — awaiting Phase 6.
"""
