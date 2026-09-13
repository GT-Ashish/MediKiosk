# MediKiosk — Authoritative Backend Architecture

> **Definitive Roadmap:**
> - **Phase 6 — Database + REST API** [COMPLETED]
> - **Phase 7 — AI + Voice** [PLANNED]
> - **Phase 8 — Document Intelligence** [PLANNED]
> - **Phase 9 — ABDM / FHIR** [PLANNED]
> - **Phase 10 — Full Integration + SIH Demo** [PLANNED]

---

## 1. System Overview

MediKiosk is an AI-powered clinical history software platform tailored for hospital outpatient department (OPD) triage. The backend is a high-performance **FastAPI** application structured in strict accordance with clean architecture principles.

### Key Architectural Tenets
1. **Frontend/Backend Decoupling:** The React frontend communicates with the FastAPI backend exclusively via well-typed REST and WebSocket APIs.
2. **Clinical Safety by Design:** MediKiosk assists with history elicitation and document structuring; it **never** diagnoses patients, prescribes treatment, or makes autonomous clinical decisions (AGENTS.md Rule 10). All AI outputs are marked as drafts requiring physician review (AGENTS.md Rule 9).
3. **Privacy & Data Security:** Patient identifiers are hashed (SHA-256) and raw Aadhaar/ABHA/mobile numbers are never stored in plain text or logged. Informed consent is strictly enforced prior to any clinical data collection.
4. **Modular AI & Pluggable Integrations:** External capabilities (speech recognition, LLM dialogue, OCR, ABDM) are encapsulated behind stable interface protocols in `infrastructure/integrations/`.
5. **Database-Agnostic Persistence:** Async SQLAlchemy 2.x ORM with repository patterns supports production PostgreSQL and zero-config development/testing SQLite.

---

## 2. Layered Architecture

The application follows a clean 5-tier layered design:

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                           │
│  FastAPI routers — request validation, response serialization│
│  /api/health (unversioned), /api/v1/* (versioned namespace) │
└──────────────────────────────┬──────────────────────────────┘
                               │ calls
┌──────────────────────────────▼──────────────────────────────┐
│                       Service Layer                         │
│  Clinical workflow logic, consent validation, orchestration │
│  services/{session,history,documents,summary,review}        │
└──────────────┬───────────────┬──────────────┬───────────────┘
               │               │              │
        Domain Schemas      Errors          Utils
        (Pydantic v2)     (errors.py)    (logging.py)
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│  database.py     — Async engine, sessionmaker, DI dependency│
│  repositories/   — Data access via SQLAlchemy ORM (Phase 6) │
│  integrations/   — AI, Speech, OCR, ABDM adapters (Phase 7+) │
└──────────────────────────────┬──────────────────────────────┘
                               │ persists
┌──────────────────────────────▼──────────────────────────────┐
│                          Database                           │
│  PostgreSQL (asyncpg) / SQLite (aiosqlite)                  │
│  Schema versioned and managed by Alembic migrations         │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

- **API Layer (`app/api/`)**:
  - Validates HTTP request payloads using Pydantic request models (`api_schemas.py`).
  - Converts domain errors into standardized HTTP JSON error responses via global exception handlers.
  - Contains no business logic and performs no direct database queries.

- **Service Layer (`app/services/`)**:
  - Implements business logic and clinical state rules defined by Python `Protocol` interfaces (`service.py`).
  - Enforces mandatory preconditions (e.g., verifying active consent prior to recording clinical answers or uploading documents).
  - Mediates between the API layer and repository persistence layer.

- **Domain Layer (`app/domain/schemas/`)**:
  - Pure Pydantic v2 domain schemas modeling core clinical concepts.
  - Encodes immutable safety invariants (e.g., `is_ai_generated=True`, `requires_physician_review=True`).
  - Completely independent of ORM, database engines, and network I/O.

- **ORM Layer (`app/domain/models/`)**:
  - SQLAlchemy 2.x Declarative models mapped to relational database tables.
  - Explicitly decoupled from domain Pydantic schemas; repositories translate between ORM entities and domain models.
  - All models inherit from a common `Base` and `TimestampMixin`.

- **Infrastructure Layer (`app/infrastructure/`)**:
  - `database.py`: Async engine lifecycle, `async_sessionmaker`, and FastAPI request-scoped session dependency (`get_db_session`).
  - `repositories/`: Concrete repositories handling transactional database queries with SQLAlchemy.
  - `integrations/`: Extensible adapter boundary for speech, OCR, LLM, and government health registries.

---

## 3. Phase 6: Database & Persistence Implementation

### 3.1 Database Support & Engine Configuration

| Environment | Driver / URL Pattern | Notes |
|---|---|---|
| **Production** | `postgresql+asyncpg://user:pass@host:5432/medikiosk` | High-throughput asynchronous PostgreSQL |
| **Development** | `sqlite+aiosqlite:///./medikiosk_dev.db` | Zero-configuration local database |
| **Testing** | `sqlite+aiosqlite://` | Fast, isolated in-memory test database per test session |

The connection is configured via `DATABASE_URL` in `app/config.py`.

### 3.2 Registered ORM Models & Table Catalog

All 6 models are registered with `Base.metadata` via `app/domain/models/__init__.py`:

| ORM Model | Table Name | Key Attributes | Cascade & Constraints |
|---|---|---|---|
| `SessionModel` | `kiosk_sessions` | `id` (UUID pk), `language`, `status`, `consent_given`, `created_at`, `updated_at` | Root entity; indexed on `status` |
| `PatientIdentifierModel` | `patient_identifiers` | `id` (UUID pk), `session_id`, `identifier_type`, `identifier_hash` (SHA-256), `display_name` | `session_id` FK (CASCADE, UNIQUE) |
| `ConsentModel` | `consents` | `id` (UUID pk), `session_id`, `consented_at`, `consent_version`, `data_use_acknowledged`, `ai_processing_acknowledged` | `session_id` FK (CASCADE, UNIQUE) |
| `VisitModel` | `visits` | `id` (UUID pk), `session_id`, `chief_complaint`, `department`, `created_at` | `session_id` FK (CASCADE) |
| `HistoryAnswerModel` | `history_answers` | `id` (UUID pk), `session_id`, `visit_id`, `question_id`, `question_text`, `answer_text`, `answer_source`, `confidence`, `answered_at` | `session_id` FK (CASCADE), `visit_id` FK (SET NULL) |
| `DocumentModel` | `medical_documents` | `id` (UUID pk), `session_id`, `filename`, `mime_type`, `uploaded_at`, `processing_status`, `file_size_bytes` | `session_id` FK (CASCADE); metadata-only in Phase 6 |

### 3.3 Transaction Management & Repository Pattern

- **Unit of Work:** FastAPI's dependency injection yields an `AsyncSession` per HTTP request.
- **Commit Boundary:** The `get_db_session()` dependency commits successful requests upon completion and automatically issues a rollback if an unhandled exception occurs.
- **Repository Isolation:** Repositories call `await self._db.flush()` rather than committing directly, allowing multiple repository operations to participate in a single atomic transaction.
- **Lazy-Load Mitigation:** Eager loading and explicit `await self._db.refresh()` ensure relationship attributes remain accessible across async contexts.

### 3.4 Alembic Migration Architecture

Schema migrations are managed by Alembic in `backend/alembic/`:
- `alembic.ini`: Configuration pointing to migration scripts and default connection.
- `alembic/env.py`: Async-native runner executing migrations via `run_async_migrations()` with `async_engine_from_config`.
- `alembic/versions/001_initial_schema.py`: Initial migration defining the 6 tables, indexes, unique constraints, and foreign key cascades.

```bash
# Apply pending migrations
alembic upgrade head

# Rollback migrations to empty baseline
alembic downgrade base

# Verify current revision
alembic current
```

---

## 4. REST API Reference (Phase 6 Live Endpoints)

All endpoints are mounted under `/api` (`/api/health` unversioned, `/api/v1/*` versioned).

### 4.1 Health Check
- `GET /api/health` — Returns application status, version, timestamp, and environment metadata (HTTP 200).

### 4.2 Kiosk Sessions
- `POST /api/v1/sessions` — Initialize a new kiosk session with language and optional hashed patient identifier (HTTP 201).
- `GET /api/v1/sessions/{session_id}` — Retrieve session state, consent status, and patient info (HTTP 200 / 404).
- `POST /api/v1/sessions/{session_id}/consent` — Record two-factor informed consent (`data_use_acknowledged` and `ai_processing_acknowledged`) (HTTP 200 / 403 / 404 / 422).
- `POST /api/v1/sessions/{session_id}/complete` — Mark session as completed (HTTP 200 / 404 / 422).
- `POST /api/v1/sessions/{session_id}/abandon` — Mark session as abandoned (HTTP 200 / 404 / 422).

### 4.3 Visits
- `POST /api/v1/sessions/{session_id}/visits` — Create a clinical visit record with chief complaint and optional department. Requires valid consent (HTTP 201 / 403 / 404).
- `GET /api/v1/visits/{visit_id}` — Retrieve clinical visit details (HTTP 200 / 404).

### 4.4 Clinical History
- `POST /api/v1/visits/{visit_id}/answers` — Record a patient Q&A answer (voice/text/button) with optional ASR confidence. Requires consent (HTTP 201 / 403 / 404 / 422).
- `GET /api/v1/visits/{visit_id}/history` — Retrieve all recorded history answers for the visit (HTTP 200 / 404).

### 4.5 Medical Documents (Metadata)
- `POST /api/v1/sessions/{session_id}/documents` — Register metadata for an uploaded document. Enforces session document limit and consent check (HTTP 201 / 403 / 404 / 422).
- `GET /api/v1/sessions/{session_id}/documents` — List all registered document records for a session (HTTP 200 / 404).
- `GET /api/v1/documents/{document_id}` — Retrieve specific document metadata (HTTP 200 / 404).

---

## 5. Voice & Speech Pipeline Architecture

```
Patient Audio Input
       │
       ├─► [Current Prototype Mechanism]: Web Speech API
       │   Browser-side speech recognition for interactive frontend prototyping
       │
       └─► [Planned Phase 7 Integration]: Bhashini / AI4Bharat ASR
           Server-side Indian-language automatic speech recognition
           (Hindi, Marathi, Bengali, Tamil, Telugu, Kannada, English, etc.)
                   │
                   ▼
           Normalized Clinical Text + Confidence Score
                   │
                   ▼
           Recorded via POST /api/v1/visits/{visit_id}/answers
```

### Current vs. Planned Voice Architecture
- **Current Prototype Mechanism (Frontend):** The browser's native **Web Speech API** provides immediate voice transcription in the frontend interface.
- **Planned Phase 7 Mechanism (Backend):** Pluggable Indian-language ASR integration powered by **Bhashini / AI4Bharat** APIs (and local Whisper fallbacks). Audio streams will be processed behind a standardized `SpeechToTextProvider` protocol in `infrastructure/integrations/speech.py`.

---

## 6. Clinical AI & Dialogue Boundary (Planned: Phase 7)

MediKiosk enforces strict boundaries around artificial intelligence:

```
Patient Answer (Voice/Text)
            │
            ▼
    Clinical State Machine
    (Deterministic rules determine which SOCRATES question is asked next)
            │
            ▼
       LLM Dialogue Engine ── Phase 7
    (Rephrases clinical questions into conversational vernacular)
            │
            ▼
   Clinical History (Structured)
            │
            ▼
    LLM Clinical Summarizer ── Phase 7
    (Generates draft clinical narrative)
            │
            ▼
  StructuredHistorySummary
  ┌────────────────────────────────────────────────────────┐
  │ is_ai_generated = True (HARDCODED FROZEN INVARIANT)    │
  │ requires_physician_review = True (FROZEN INVARIANT)    │
  │ review_status = "DRAFT"                                │
  └────────────────────────────┬───────────────────────────┘
                               │
                               ▼
                   Physician Review & Sign-Off (MANDATORY)
```

### AI Safety Rules
- **Draft Status Only:** Summaries generated by AI are permanently flagged with `is_ai_generated=True` and `requires_physician_review=True`.
- **No Autonomous Diagnosis:** The AI pipeline extracts information and drafts summaries; it **never** suggests diagnoses or prescribes treatments.
- **Physician Oversight:** Only an authenticated doctor can convert a draft summary into a finalized record via `DoctorReview`.

---

## 7. Document Intelligence Pipeline (Planned: Phase 8)

Document handling is divided across phases:

```
Phase 6 (Completed):
  Upload Trigger ──► Register Metadata (POST /sessions/{id}/documents)
                         └── File size, MIME type, status="pending"

Phase 8 (Planned Document Intelligence):
  Binary Upload  ──► Secure Storage (Local encrypted storage / MinIO / S3)
                            │
                            ▼
                     OCR & Handwriting Recognition (HTR)
                     (Tesseract / Google Cloud Vision / Azure AI Document)
                            │
                            ▼ raw_text
                     Clinical Named Entity Recognition (NER)
                     (Extract medications, lab values, dosages, dates)
                            │
                            ▼
                     Structured DocumentExtraction
```

- **Phase 6 Scope:** Metadata tracking only (`DocumentModel` in `kiosk_sessions`).
- **Phase 8 Scope:** Actual binary file persistence, OCR for printed reports, handwriting recognition for physician prescriptions, medical entity extraction, and multi-document timeline synthesis.

---

## 8. ABDM / FHIR & Identity Architecture (Planned: Phase 9)

In accordance with **AGENTS.md Rule 14**, ABDM integration is strictly deferred until its compliance architecture is fully approved:

- **Ayushman Bharat Digital Mission (ABDM):**
  - ABHA (Ayushman Bharat Health Account) creation and verification.
  - M1, M2, M3 compliance milestones for Health Information Provider (HIP) and Health Information User (HIU).
- **FHIR Standards:**
  - Serialization of clinical history into standard HL7 FHIR (Fast Healthcare Interoperability Resources) bundles (Composition, Condition, Observation, Patient).
- **Aadhaar / e-KYC Integration:**
  - Real Aadhaar verification via ABDM gateway APIs.
  - Zero raw Aadhaar storage: MediKiosk stores only irreversibly salted SHA-256 hashes for session correlation.

---

## 9. Error Handling & Security Architecture

### 9.1 Domain Error Hierarchy
All custom errors extend `MediKioskError` (`app/utils/errors.py`):

| Error Class | HTTP Code | Trigger Condition |
|---|---|---|
| `SessionNotFoundError` | 404 | Session UUID does not exist or expired |
| `ConsentRequiredError` | 403 | Attempting clinical write operations without consent |
| `MediKioskValidationError` | 422 | Schema validation failure or invalid state transition |
| `UnsupportedOperationError` | 501 | Accessing stubbed future-phase endpoints (e.g. summary/review) |
| `DocumentProcessingError` | 500 | Pipeline failure during document handling (Phase 8) |
| `AIProcessingError` | 502 | Upstream LLM/ASR service outage (Phase 7) |

### 9.2 Privacy & Logging Protection
`app/utils/logging.py` implements a `_PIISafeFilter` that intercepts all log records:
- Redacts sensitive attributes: `aadhaar`, `abha_id`, `identifier_hash`, `answer_text`, `raw_text`, `patient_name`, `display_name`, `history_narrative`, `mobile`, `phone`, `corrections`.
- Prevents leakage of personal identifiable information in server outputs and error payloads.

---

## 10. Configuration Reference (`app/config.py`)

Settings are loaded from environment variables using `pydantic-settings`:

| Setting | Env Variable | Default | Description |
|---|---|---|---|
| `app_name` | `APP_NAME` | `MediKiosk Backend` | Application title |
| `app_env` | `APP_ENV` | `development` | Environment (`development`, `testing`, `production`) |
| `debug` | `DEBUG` | `true` | Enables Swagger UI and verbose diagnostics |
| `database_url` | `DATABASE_URL` | `sqlite+aiosqlite:///./medikiosk_dev.db` | SQLAlchemy async connection string |
| `cors_origins` | `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins for frontend client |
| `session_ttl_minutes` | `SESSION_TTL_MINUTES` | `60` | Inactivity expiry period |
| `max_documents_per_session`| `MAX_DOCUMENTS_PER_SESSION`| `10` | Maximum attachments per session |
| `ai_enabled` | `AI_ENABLED` | `false` | Master toggle for Phase 7 AI capabilities |
| `log_level` | `LOG_LEVEL` | `INFO` | Console logging threshold |

---

## 11. Testing & Quality Assurance

The backend test suite (`tests/backend/`) provides comprehensive asynchronous coverage using `pytest` and `pytest-asyncio`:

- **Execution Command:**
  ```bash
  pytest tests/ -v
  ```
- **Test Categories:**
  - `test_api_sessions.py`: Session creation, language setting, hashed identifier association, consent verification, completion, abandonment.
  - `test_api_visits.py`: Visit registration under active sessions, consent checks, department assignments.
  - `test_api_history.py`: Recording voice/text answers, confidence tracking, visit history querying.
  - `test_api_documents.py`: Document metadata registration, document limits, session document listing.
  - `test_schemas.py`: Validation of pure Pydantic domain models and frozen invariants.
  - `test_health.py`: Endpoint availability and CORS headers.
- **Isolation:** Tests use isolated in-memory SQLite instances via the `db_client` fixture.

---

## 12. Local Development Guide

```bash
# 1. Activate Python virtual environment
cd backend
.\.venv\Scripts\Activate.ps1

# 2. Run database migrations to head
alembic upgrade head

# 3. Start local development server with auto-reload
uvicorn app.main:app --reload --port 8000

# 4. Run test suite
pytest ../tests/ -v
```

---

## 13. Definitive Project Roadmap

| Phase | Milestone | Scope & Deliverables | Status |
|---|---|---|---|
| **Phase 6** | **Database + REST API** | SQLAlchemy 2.x async ORM, 6 models, Alembic migrations, complete REST API endpoints for Sessions, Visits, History, Documents | **COMPLETED** |
| **Phase 7** | **AI + Voice** | Bhashini / AI4Bharat Indian-language ASR integration, clinical dialogue LLM, draft clinical summarization, summary service implementation | **PLANNED** |
| **Phase 8** | **Document Intelligence** | Binary document storage (local/S3), OCR and handwriting recognition, medical entity extraction (NER), clinical document synthesis | **PLANNED** |
| **Phase 9** | **ABDM / FHIR** | ABDM M1/M2/M3 compliance, ABHA identity verification, FHIR bundle generation and health information exchange, real Aadhaar/e-KYC | **PLANNED** |
| **Phase 10** | **Full Integration + SIH Demo**| End-to-end integration, kiosk hardware hardening, multilingual offline failover, final SIH 2026 presentation demonstration | **PLANNED** |

---

## 14. Repository Directory Map

```
backend/
├── alembic.ini                             ← Alembic migration configuration
├── alembic/
│   ├── env.py                              ← Async-aware migration runner
│   ├── script.py.mako                      ← Migration script template
│   └── versions/
│       └── 001_initial_schema.py           ← Phase 6 initial schema migration
│
├── requirements.txt                        ← Pinned production dependencies
├── requirements-dev.txt                    ← Development dependencies
├── .env.example                            ← Environment variable template
│
└── app/
    ├── main.py                             ← FastAPI app factory, CORS, error handlers, lifespan
    ├── config.py                           ← Application settings (Pydantic Settings)
    │
    ├── api/
    │   ├── router.py                       ← Aggregates health check and /v1 routers
    │   ├── dependencies.py                 ← Dependency injection: DB session -> repos -> services
    │   └── v1/
    │       ├── router.py                   ← API v1 central router
    │       ├── health.py                   ← GET /api/health endpoint
    │       ├── api_schemas.py              ← API request and response models
    │       ├── sessions.py                 ← Kiosk session lifecycle endpoints
    │       ├── visits.py                   ← Clinical visit endpoints
    │       ├── history.py                  ← History Q&A endpoints
    │       └── documents.py                ← Medical document metadata endpoints
    │
    ├── domain/
    │   ├── models/                         ← SQLAlchemy 2.x ORM models
    │   │   ├── __init__.py                 ← Base.metadata registration of all 6 models
    │   │   ├── base.py                     ← Base and TimestampMixin
    │   │   ├── session.py                  ← SessionModel (kiosk_sessions)
    │   │   ├── patient.py                  ← PatientIdentifierModel (patient_identifiers)
    │   │   ├── consent.py                  ← ConsentModel (consents)
    │   │   ├── visit.py                    ← VisitModel (visits)
    │   │   ├── history.py                  ← HistoryAnswerModel (history_answers)
    │   │   └── document.py                 ← DocumentModel (medical_documents)
    │   └── schemas/                        ← Pure Pydantic v2 domain schemas
    │       ├── session.py                  ← KioskSession, SessionStatus
    │       ├── patient.py                  ← PatientIdentifier, IdentifierType
    │       ├── consent.py                  ← Consent
    │       ├── visit.py                    ← Visit
    │       ├── history.py                  ← ClinicalHistory, HistoryAnswer, AnswerSource
    │       ├── document.py                 ← MedicalDocument, DocumentExtraction, MedicalEntity
    │       ├── summary.py                  ← StructuredHistorySummary, ReviewStatus
    │       └── review.py                   ← DoctorReview
    │
    ├── services/                           ← Business logic and workflow enforcement
    │   ├── session/
    │   │   ├── service.py                  ← SessionService Protocol
    │   │   └── impl.py                     ← SessionServiceImpl (Phase 6 complete)
    │   ├── history/
    │   │   ├── service.py                  ← HistoryService Protocol
    │   │   └── impl.py                     ← HistoryServiceImpl (Phase 6 complete)
    │   ├── documents/
    │   │   ├── service.py                  ← DocumentService Protocol
    │   │   └── impl.py                     ← DocumentServiceImpl (Phase 6 complete)
    │   ├── summary/
    │   │   ├── service.py                  ← SummaryService Protocol
    │   │   └── impl.py                     ← SummaryServiceImpl (stub for Phase 7)
    │   └── review/
    │       ├── service.py                  ← ReviewService Protocol
    │       └── impl.py                     ← ReviewServiceImpl (stub for Phase 7)
    │
    ├── infrastructure/
    │   ├── database.py                     ← Engine, sessionmaker, get_db_session dependency
    │   ├── repositories/                   ← SQLAlchemy persistence repositories
    │   │   ├── __init__.py                 ← Repository exports
    │   │   ├── session_repo.py             ← SQLAlchemySessionRepository
    │   │   ├── consent_repo.py             ← SQLAlchemyConsentRepository
    │   │   ├── visit_repo.py               ← SQLAlchemyVisitRepository
    │   │   ├── history_repo.py             ← SQLAlchemyHistoryRepository
    │   │   └── document_repo.py            ← SQLAlchemyDocumentRepository
    │   └── integrations/                   ← External adapter boundary (Phase 7+)
    │
    └── utils/
        ├── errors.py                       ← MediKioskError domain exception hierarchy
        └── logging.py                      ← PII-safe logging filter and setup
```
