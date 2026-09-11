"""
MediKiosk Infrastructure Layer.

This layer is responsible for all external concerns:
    - Database access (repositories/)
    - External service integrations (integrations/)

Architecture:
    The infrastructure layer implements the repository and integration
    interfaces defined by the service layer. The service layer never
    imports directly from infrastructure — it depends on abstractions.

    API Layer
        ↓
    Service Layer  ←─ depends on abstractions (Protocols)
        ↓
    Infrastructure Layer  ←─ implements those abstractions
        ├── repositories/   ←─ database access (Phase 6+)
        └── integrations/   ←─ external services (Phase 7+)

Current status:
    Phase 5 — directories established, no implementations yet.
    Phase 6 — PostgreSQL repositories will be added here.
    Phase 7+ — OCR, LLM, ABDM integrations will be added here.
"""
