"""
MediKiosk Services Package.

Each sub-package contains a service protocol (interface) defining the
operations that layer is responsible for. Concrete implementations
are provided by in-memory stubs (Phase 6) and later by database-backed
implementations (Phase 6+).

Service packages:
    session/   — KioskSession lifecycle management
    history/   — Clinical history elicitation and retrieval
    documents/ — Medical document registration and retrieval
    summary/   — AI-generated history summary generation
    review/    — Physician review submission and retrieval
"""
