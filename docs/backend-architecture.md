> **Phase 6 — Database + API Implementation**
> Phase 5 established the architectural contracts. Phase 6 makes them real
> with SQLAlchemy persistence, Alembic migrations, and live REST APIs.

---

## Overview

MediKiosk is an AI-assisted patient history elicitation system for OPD settings.
The backend is a **FastAPI** application with a layered architecture designed so that:

- The database can be added without touching the API layer
- AI services can be added without touching the domain layer
- OCR providers can be swapped without touching the service layer
- The frontend communicates only through stable API contracts

---

## Layer Architecture

```
┌──────────────────────────────────────────────────────┐
│                    API Layer                         │
│  FastAPI routers — request/response validation       │
│  /api/health, /api/v1/*                              │
└──────────────────────┬───────────────────────────────┘
                       │ calls
┌──────────────────────▼───────────────────────────────┐
│                 Service Layer                        │
│  Business logic, clinical workflow, error handling   │
│  services/{session,history,documents,summary,review} │
└────────┬─────────────┬──────────────┬────────────────┘
         │             │              │
    Domain Schemas   Errors        Utils
    (Pydantic only)  (errors.py)   (logging.py)
         │
┌────────▼───────────────────────────────────────────┐
│              Infrastructure Layer                  │
│  database.py     — SQLAlchemy engine + session     │
│  repositories/   — database access via ORM         │
│  integrations/   — OCR, LLM, ABDM (Phase 7+)      │
└────────────────────────────────────────────────────┘
         │
┌────────▼───────────────────────────────────────────┐
│          Database (PostgreSQL / SQLite)             │
│  Alembic-managed schema migrations                 │
└────────────────────────────────────────────────────┘
```

### API Layer (`app/api/`)
- Handles HTTP request/response concerns
- Validates inputs via Pydantic schema request models
- Maps domain errors to HTTP status codes
- Never contains business logic
- Never accesses the database or AI services directly

### Service Layer (`app/services/`)
- Contains all business logic and clinical workflow
- Defined as Python **Protocols** (typed interfaces)
- Concrete implementations in `services/*/impl.py`
- Enforces consent requirements before any clinical data operation
- Enforces physician review requirements for AI summaries

### Domain Layer (`app/domain/schemas/`)
- Pure Pydantic schemas — no ORM, no I/O
- These are the data contracts used across all layers
- Define the structure of every MediKiosk concept
- Safety-critical invariants are encoded at the schema level

### ORM Models (`app/domain/models/`)
- SQLAlchemy 2.x ORM models — separate from Pydantic schemas
- Mapped columns use `Mapped`, `mapped_column` (modern API)
- Repositories handle ORM ↔ domain mapping
- All models inherit from shared `Base` (DeclarativeBase)

### Infrastructure Layer (`app/infrastructure/`)
- `database.py` — async engine, session factory, FastAPI dependency
- `repositories/` — implements persistence via SQLAlchemy ORM
- `integrations/` — wraps external APIs (OCR, LLM, ABDM) behind clean interfaces (Phase 7+)

---

## Phase 6: Database Architecture

### Database Support

| Driver | URL Pattern | Purpose |
|---|---|---|
| PostgreSQL + asyncpg | `postgresql+asyncpg://user:pass@host:5432/medikiosk` | Production |
| SQLite + aiosqlite | `sqlite+aiosqlite:///./medikiosk_dev.db` | Development |
| SQLite + aiosqlite (in-memory) | `sqlite+aiosqlite://` | Testing |

The `DATABASE_URL` environment variable controls which database is used.
Default is SQLite for zero-config local development.

### ORM Model Catalogue

| Model | Table | Description |
|---|---|---|
| `SessionModel` | `kiosk_sessions` | Patient interaction lifecycle (active → completed/abandoned) |
| `PatientIdentifierModel` | `patient_identifiers` | Privacy-preserving patient reference (hashed, never raw Aadhaar) |
| `ConsentModel` | `consents` | Two-factor informed consent record |
| `VisitModel` | `visits` | Clinical encounter with chief complaint |
| `HistoryAnswerModel` | `history_answers` | Individual Q&A from kiosk conversation |
| `DocumentModel` | `medical_documents` | Document metadata only (file storage Phase 8) |

### Transaction Boundaries

- Each FastAPI request gets its own `AsyncSession`
- Successful operations: auto-committed at the end of `get_db_session()`
- Failed operations: auto-rolled back via exception handler
- Multi-write operations (e.g., consent + session update): both in same transaction
- Repositories use `flush()` (not `commit()`) to stay within the request transaction

### Repository Pattern

```
API  →  Service  →  Repository  →  SQLAlchemy ORM  →  Database
                                         ↕
                               ORM ↔ Domain mapping
```

Each repository:
- Receives `AsyncSession` via constructor injection
- Handles CRUD and ORM ↔ Pydantic mapping
- Never contains business rules (those belong in services)
- Uses `flush()` to persist within the current transaction

| Repository | Domain Object |
|---|---|
| `SQLAlchemySessionRepository` | `KioskSession` |
| `SQLAlchemyConsentRepository` | `Consent` |
| `SQLAlchemyVisitRepository` | `Visit` |
| `SQLAlchemyHistoryRepository` | `HistoryAnswer` |
| `SQLAlchemyDocumentRepository` | `MedicalDocument` |

### Service Layer

| Service | Status | Notes |
|---|---|---|
| `SessionServiceImpl` | ✅ Implemented | Session lifecycle + consent recording |
| `HistoryServiceImpl` | ✅ Implemented | Answer recording + structured history assembly |
| `DocumentServiceImpl` | ✅ Implemented | Metadata registration + document limits |
| `SummaryServiceImpl` | ⏸ Stub | Returns 501 — AI deferred to Phase 7 |
| `ReviewServiceImpl` | ⏸ Stub | Returns 501 — requires summaries (Phase 7) |

### Alembic Migrations

```
backend/
├── alembic.ini                             ← Configuration
└── alembic/
    ├── env.py                              ← Async-aware migration runner
    ├── script.py.mako                      ← Template
    └── versions/
        └── 001_initial_schema.py           ← Phase 6 tables
```

**Running migrations:**
```bash
cd backend

# Apply all migrations
alembic upgrade head

# Rollback
alembic downgrade base

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description"
```

The migration system reads `DATABASE_URL` from environment variables.
For development, the default targets the local SQLite file.

---

## API Endpoints (Phase 6 — All Live)

### Sessions
```
POST /api/v1/sessions                      → 201 Created
GET  /api/v1/sessions/{session_id}         → 200 / 404
POST /api/v1/sessions/{session_id}/consent → 200 / 403 / 404
POST /api/v1/sessions/{session_id}/complete → 200 / 404 / 422
POST /api/v1/sessions/{session_id}/abandon  → 200 / 404 / 422
```

### Visits
```
POST /api/v1/sessions/{session_id}/visits  → 201 / 403 / 404
GET  /api/v1/visits/{visit_id}             → 200 / 404
```

### History
```
POST /api/v1/visits/{visit_id}/answers     → 201 / 403 / 404
GET  /api/v1/visits/{visit_id}/history     → 200 / 404
```

### Documents
```
POST /api/v1/sessions/{session_id}/documents → 201 / 403 / 404 / 422
GET  /api/v1/sessions/{session_id}/documents → 200 / 404
GET  /api/v1/documents/{document_id}         → 200 / 404
```

### Health
```
GET  /api/health                           → 200
```

---

## Domain Concepts

| Schema | Description |
|---|---|
| `KioskSession` | Top-level container for one patient interaction. Lifecycle: ACTIVE → COMPLETED / ABANDONED |
| `PatientIdentifier` | Privacy-safe patient reference. Stores only hashed identifiers — never raw Aadhaar |
| `Consent` | Patient's informed consent record. Two acknowledgements required before data collection |
| `Visit` | A single clinical encounter. Contains the chief complaint and links to ClinicalHistory |
| `ClinicalHistory` | SOCRATES-structured history. Progressively built from HistoryAnswers |
| `HistoryAnswer` | Single Q&A exchange from the kiosk conversation |
| `MedicalDocument` | Uploaded document metadata. File content managed separately |
| `DocumentExtraction` | OCR + NER result for a document (Phase 7+) |
| `MedicalEntity` | A single extracted clinical entity (medication, diagnosis, etc.) |
| `StructuredHistorySummary` | **AI-generated draft only.** Always requires physician review |
| `DoctorReview` | Physician's sign-off on a summary. The final clinical confirmation |

---

## AI Boundary

This is the most important architectural boundary in MediKiosk.

```
Patient Speech / Text
        ↓
   ASR Engine (Web Speech API now; Bhashini/Whisper later)
        ↓
  Conversation Engine ←── Clinical State Machine
  (decides which          (determines required fields
   questions to ask)       from ClinicalHistory schema)
        ↓
  ClinicalHistory
  (structured, validated)
        ↓
      LLM ←── Phase 7+
  (generates narrative,
   extracts entities,
   summarises)
        ↓
    Validation
  (schema-checked)
        ↓
  StructuredHistorySummary
  (is_ai_generated=True, requires_physician_review=True)
        ↓
  Doctor Review (REQUIRED)
```

### What AI does
- Natural language understanding of patient responses
- Conversational phrasing of follow-up questions
- Medical entity extraction from free-text and documents
- Clinical narrative summarisation

### What AI must NOT do
- Decide what clinical information is required (the schema does this)
- Diagnose the patient
- Make autonomous clinical decisions
- Generate summaries that bypass physician review

### Safety Invariants (architecturally enforced)
```python
# These fields are frozen — they cannot be overridden
StructuredHistorySummary.is_ai_generated = True        # always
StructuredHistorySummary.requires_physician_review = True  # always
```

---

## Document Processing Pipeline

```
Image / PDF (uploaded at kiosk)
        ↓
  File Storage ──── Phase 8+ (local disk / object storage)
        ↓
  OCR Engine ─────── Phase 8+ (replaceable: Tesseract / Google Vision / Azure)
        ↓  raw_text
  NER Extraction ─── Phase 8+ (LLM-assisted medical entity recognition)
        ↓  list[MedicalEntity]
  DocumentExtraction (stored)
        ↓
  Synthesis ────────  Phase 8+ (cross-document timeline)
        ↓
  document_findings → StructuredHistorySummary
```

**Provider independence:** The OCR provider is behind an integration interface.
Swapping providers (e.g., Tesseract → Google Vision) requires only changing
the registered implementation in `infrastructure/integrations/` — the API
and service layers remain untouched.

---

## Error Handling

All domain errors inherit from `MediKioskError` and are caught by the API layer.

| Error | HTTP | When |
|---|---|---|
| `SessionNotFoundError` | 404 | Invalid/expired session ID |
| `ConsentRequiredError` | 403 | Operation attempted without consent |
| `MediKioskValidationError` | 422 | Domain validation fails |
| `DocumentProcessingError` | 500 | OCR/NER pipeline fails |
| `AIProcessingError` | 502 | LLM call fails |
| `UnsupportedOperationError` | 501 | Feature not yet implemented |

**Rule:** Internal details (stack traces, DB errors) are **never** returned to the client.
Debug details are shown only when `settings.debug = True`.

---

## Privacy & Security Architecture

### Principles
1. **No secrets in source code.** All keys and credentials in `.env` (never committed).
2. **No raw Aadhaar.** Only SHA-256 hashes of patient identifiers are stored.
3. **No PII in logs.** The `_PIISafeFilter` logging filter strips sensitive fields.
4. **Minimum necessary data.** Collect only what is needed for the clinical history.
5. **Explicit consent.** Two-factor consent required before any clinical data collection.
6. **Session termination.** Completed/abandoned sessions purge in-memory state.
7. **AI as draft.** All AI output is explicitly marked as requiring physician review.
8. **Physician sign-off.** A `DoctorReview` with `status=REVIEWED` is required before clinical use.

### Sensitive Fields (Never Log)
```python
# app/utils/logging.py — _SENSITIVE_FIELDS
"aadhaar", "abha_id", "identifier_hash",
"answer_text", "raw_text", "patient_name",
"display_name", "history_narrative",
"mobile", "phone", "corrections"
```

### ABDM Note
ABDM/ABHA integration is **deferred to Phase 9+** per AGENTS.md Rule 14.
Its architecture must be reviewed for compliance before implementation.

---

## Configuration (`app/config.py`)

All settings are environment-variable driven. Defaults are for local development only.

| Setting | Env Var | Default | Purpose |
|---|---|---|---|
| `app_env` | `APP_ENV` | `development` | Environment name |
| `debug` | `DEBUG` | `true` | Enable debug mode (docs, stack traces) |
| `database_url` | `DATABASE_URL` | `sqlite+aiosqlite:///./medikiosk_dev.db` | Database connection URL |
| `cors_origins` | `CORS_ORIGINS` | localhost:5173 | Allowed frontend origins |
| `session_ttl_minutes` | `SESSION_TTL_MINUTES` | `60` | Session expiry (minutes) |
| `max_documents_per_session` | `MAX_DOCUMENTS_PER_SESSION` | `10` | Upload limit per session |
| `ai_enabled` | `AI_ENABLED` | `false` | Enable LLM features |
| `log_level` | `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Testing Strategy

### SQLite Test Suite (default)
- All tests use in-memory async SQLite (`sqlite+aiosqlite://`)
- No PostgreSQL required to run the test suite
- Each test gets a fresh database via the `db_client` fixture
- Tables created automatically via `Base.metadata.create_all()`

### Running Tests
```bash
cd backend
python -m pytest ../tests/ -v
```

### Test Coverage
- **Session tests**: create, get, consent, complete, abandon, state transitions, patient identifier
- **Visit tests**: create, get, consent enforcement, optional department
- **History tests**: record answer, retrieve history, consent enforcement, multiple answers
- **Document tests**: register, get, list, consent enforcement, limit enforcement
- **Schema tests**: Pydantic domain schema validation
- **Health tests**: API health check

---

## Local Development Setup

```bash
# 1. Install dependencies
cd backend
pip install -r requirements-dev.txt

# 2. Configure environment (optional — defaults work out of the box)
cp .env.example .env

# 3. Run migrations
alembic upgrade head

# 4. Start the development server
uvicorn app.main:app --reload --port 8000

# 5. Run tests
python -m pytest ../tests/ -v
```

**Environment Variables:**
```
DATABASE_URL=sqlite+aiosqlite:///./medikiosk_dev.db   # default
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/medikiosk  # production
APP_ENV=development
DEBUG=true
```

---

## What Is Intentionally NOT Implemented

| Feature | Phase | Reason Deferred |
|---|---|---|
| LLM / AI conversation engine | Phase 7 | Requires AI provider selection |
| Bhashini / AI4Bharat ASR/TTS | Phase 7 | Frontend Web Speech API is sufficient for now |
| Actual file storage | Phase 8 | Needs storage strategy decision |
| OCR / handwritten prescription recognition | Phase 8 | Needs provider selection |
| Medical entity extraction | Phase 8 | Needs OCR + LLM pipeline |
| ABDM / FHIR integration | Phase 9 | Compliance review required first |
| Real Aadhaar / e-KYC | Phase 9 | Requires ABDM |
| Production authentication | Phase 6+ | Doctor dashboard auth before production |

---

## Directory Map

```
backend/
├── alembic.ini                  ← Alembic migration configuration
├── alembic/
│   ├── env.py                   ← Async-aware migration runner
│   ├── script.py.mako           ← Migration template
│   └── versions/
│       └── 001_initial_schema.py ← Phase 6 initial tables
│
├── requirements.txt             ← Production dependencies (pinned)
├── requirements-dev.txt         ← Development dependencies
├── .env.example                 ← Environment variable template
│
└── app/
    ├── main.py                  ← App factory, CORS, exception handlers, lifespan
    ├── config.py                ← All settings (env-var driven)
    │
    ├── api/
    │   ├── router.py            ← Aggregates health + v1 router
    │   ├── dependencies.py      ← DI: session → repos → services
    │   └── v1/
    │       ├── router.py        ← v1 endpoint registration
    │       ├── health.py        ← GET /api/health
    │       ├── api_schemas.py   ← API request/response models
    │       ├── sessions.py      ← Session lifecycle endpoints
    │       ├── visits.py        ← Visit CRUD endpoints
    │       ├── history.py       ← History Q&A endpoints
    │       └── documents.py     ← Document metadata endpoints
    │
    ├── domain/
    │   ├── models/              ← SQLAlchemy ORM models
    │   │   ├── __init__.py      ← Registers all models with Base.metadata
    │   │   ├── base.py          ← TimestampMixin
    │   │   ├── session.py       ← SessionModel (kiosk_sessions)
    │   │   ├── patient.py       ← PatientIdentifierModel (patient_identifiers)
    │   │   ├── consent.py       ← ConsentModel (consents)
    │   │   ├── visit.py         ← VisitModel (visits)
    │   │   ├── history.py       ← HistoryAnswerModel (history_answers)
    │   │   └── document.py      ← DocumentModel (medical_documents)
    │   └── schemas/
    │       ├── session.py       ← KioskSession, SessionStatus
    │       ├── patient.py       ← PatientIdentifier, IdentifierType
    │       ├── consent.py       ← Consent
    │       ├── visit.py         ← Visit
    │       ├── history.py       ← ClinicalHistory, HistoryAnswer, AnswerSource
    │       ├── document.py      ← MedicalDocument, DocumentExtraction, MedicalEntity
    │       ├── summary.py       ← StructuredHistorySummary, ReviewStatus
    │       └── review.py        ← DoctorReview
    │
    ├── services/
    │   ├── session/
    │   │   ├── service.py       ← SessionService Protocol
    │   │   └── impl.py          ← SessionServiceImpl (Phase 6)
    │   ├── history/
    │   │   ├── service.py       ← HistoryService Protocol
    │   │   └── impl.py          ← HistoryServiceImpl (Phase 6)
    │   ├── documents/
    │   │   ├── service.py       ← DocumentService Protocol
    │   │   └── impl.py          ← DocumentServiceImpl (Phase 6)
    │   ├── summary/
    │   │   ├── service.py       ← SummaryService Protocol
    │   │   └── impl.py          ← SummaryServiceImpl (stub — Phase 7)
    │   └── review/
    │       ├── service.py       ← ReviewService Protocol
    │       └── impl.py          ← ReviewServiceImpl (stub — Phase 7)
    │
    ├── infrastructure/
    │   ├── database.py          ← Async engine, session factory, FastAPI dependency
    │   ├── repositories/
    │   │   ├── __init__.py      ← Repository exports
    │   │   ├── session_repo.py  ← SQLAlchemySessionRepository
    │   │   ├── consent_repo.py  ← SQLAlchemyConsentRepository
    │   │   ├── visit_repo.py    ← SQLAlchemyVisitRepository
    │   │   ├── history_repo.py  ← SQLAlchemyHistoryRepository
    │   │   └── document_repo.py ← SQLAlchemyDocumentRepository
    │   └── integrations/        ← OCR, LLM, ABDM (Phase 7+)
    │
    └── utils/
        ├── errors.py            ← MediKioskError hierarchy
        └── logging.py           ← PII-safe logging configuration
```


---

## Overview

MediKiosk is an AI-assisted patient history elicitation system for OPD settings.
The backend is a **FastAPI** application with a layered architecture designed so that:

- The database can be added without touching the API layer
- AI services can be added without touching the domain layer
- OCR providers can be swapped without touching the service layer
- The frontend communicates only through stable API contracts

---

## Layer Architecture

```
┌──────────────────────────────────────────────────────┐
│                    API Layer                         │
│  FastAPI routers — request/response validation       │
│  /api/health, /api/v1/*                              │
└──────────────────────┬───────────────────────────────┘
                       │ calls
┌──────────────────────▼───────────────────────────────┐
│                 Service Layer                        │
│  Business logic, clinical workflow, error handling   │
│  services/{session,history,documents,summary,review} │
└────────┬─────────────┬──────────────┬────────────────┘
         │             │              │
    Domain Schemas   Errors        Utils
    (Pydantic only)  (errors.py)   (logging.py)
         │
┌────────▼───────────────────────────────────────────┐
│              Infrastructure Layer                  │
│  repositories/ — database access (Phase 6+)        │
│  integrations/ — OCR, LLM, ABDM (Phase 7+)         │
└────────────────────────────────────────────────────┘
```

### API Layer (`app/api/`)
- Handles HTTP request/response concerns
- Validates inputs via Pydantic schema request models
- Maps domain errors to HTTP status codes
- Never contains business logic
- Never accesses the database or AI services directly

### Service Layer (`app/services/`)
- Contains all business logic and clinical workflow
- Defined as Python **Protocols** (typed interfaces)
- Concrete implementations provided by infrastructure (Phase 6+)
- Enforces consent requirements before any clinical data operation
- Enforces physician review requirements for AI summaries

### Domain Layer (`app/domain/schemas/`)
- Pure Pydantic schemas — no ORM, no I/O
- These are the data contracts used across all layers
- Define the structure of every MediKiosk concept
- Safety-critical invariants are encoded at the schema level

### Infrastructure Layer (`app/infrastructure/`)
- `repositories/` — implements service Protocols against a database (Phase 6+)
- `integrations/` — wraps external APIs (OCR, LLM, ABDM) behind clean interfaces (Phase 7+)

---

## Domain Concepts

| Schema | Description |
|---|---|
| `KioskSession` | Top-level container for one patient interaction. Lifecycle: ACTIVE → COMPLETED / ABANDONED |
| `PatientIdentifier` | Privacy-safe patient reference. Stores only hashed identifiers — never raw Aadhaar |
| `Consent` | Patient's informed consent record. Two acknowledgements required before data collection |
| `Visit` | A single clinical encounter. Contains the chief complaint and links to ClinicalHistory |
| `ClinicalHistory` | SOCRATES-structured history. Progressively built from HistoryAnswers |
| `HistoryAnswer` | Single Q&A exchange from the kiosk conversation |
| `MedicalDocument` | Uploaded document metadata. File content managed separately |
| `DocumentExtraction` | OCR + NER result for a document (Phase 7+) |
| `MedicalEntity` | A single extracted clinical entity (medication, diagnosis, etc.) |
| `StructuredHistorySummary` | **AI-generated draft only.** Always requires physician review |
| `DoctorReview` | Physician's sign-off on a summary. The final clinical confirmation |

---

## AI Boundary

This is the most important architectural boundary in MediKiosk.

```
Patient Speech / Text
        ↓
   ASR Engine (Web Speech API now; Bhashini/Whisper later)
        ↓
  Conversation Engine ←── Clinical State Machine
  (decides which          (determines required fields
   questions to ask)       from ClinicalHistory schema)
        ↓
  ClinicalHistory
  (structured, validated)
        ↓
      LLM ←── Phase 7+
  (generates narrative,
   extracts entities,
   summarises)
        ↓
    Validation
  (schema-checked)
        ↓
  StructuredHistorySummary
  (is_ai_generated=True, requires_physician_review=True)
        ↓
  Doctor Review (REQUIRED)
```

### What AI does
- Natural language understanding of patient responses
- Conversational phrasing of follow-up questions
- Medical entity extraction from free-text and documents
- Clinical narrative summarisation

### What AI must NOT do
- Decide what clinical information is required (the schema does this)
- Diagnose the patient
- Make autonomous clinical decisions
- Generate summaries that bypass physician review

### Safety Invariants (architecturally enforced)
```python
# These fields are frozen — they cannot be overridden
StructuredHistorySummary.is_ai_generated = True        # always
StructuredHistorySummary.requires_physician_review = True  # always
```

---

## Document Processing Pipeline

```
Image / PDF (uploaded at kiosk)
        ↓
  File Storage ──── Phase 7+ (local disk / object storage)
        ↓
  OCR Engine ─────── Phase 7+ (replaceable: Tesseract / Google Vision / Azure)
        ↓  raw_text
  NER Extraction ─── Phase 7+ (LLM-assisted medical entity recognition)
        ↓  list[MedicalEntity]
  DocumentExtraction (stored)
        ↓
  Synthesis ────────  Phase 7+ (cross-document timeline)
        ↓
  document_findings → StructuredHistorySummary
```

**Provider independence:** The OCR provider is behind an integration interface.
Swapping providers (e.g., Tesseract → Google Vision) requires only changing
the registered implementation in `infrastructure/integrations/` — the API
and service layers remain untouched.

---

## Future API Surface

All endpoints below are **documented contracts for Phase 6 implementation**.
Only `/api/health` is currently live.

```
GET  /api/health                     — Health check (live)

POST /api/v1/sessions                — Create a new kiosk session
GET  /api/v1/sessions/{session_id}   — Get session status
POST /api/v1/sessions/{session_id}/consent    — Record patient consent
POST /api/v1/sessions/{session_id}/complete   — Complete session
POST /api/v1/sessions/{session_id}/abandon    — Abandon session

POST /api/v1/visits                  — Create a visit (chief complaint)
GET  /api/v1/visits/{visit_id}       — Get visit details

POST /api/v1/history/answers         — Record a clinical answer
GET  /api/v1/history/{session_id}    — Get clinical history for session

POST /api/v1/documents               — Register uploaded document
GET  /api/v1/documents/{document_id} — Get document metadata
GET  /api/v1/documents?session_id=   — List documents for session

POST /api/v1/summaries/{session_id}  — Generate AI summary
GET  /api/v1/summaries/{session_id}  — Get generated summary

POST /api/v1/reviews                 — Submit doctor review
GET  /api/v1/reviews/{summary_id}    — Get doctor review
```

---

## Error Handling

All domain errors inherit from `MediKioskError` and are caught by the API layer.

| Error | HTTP | When |
|---|---|---|
| `SessionNotFoundError` | 404 | Invalid/expired session ID |
| `ConsentRequiredError` | 403 | Operation attempted without consent |
| `MediKioskValidationError` | 422 | Domain validation fails |
| `DocumentProcessingError` | 500 | OCR/NER pipeline fails |
| `AIProcessingError` | 502 | LLM call fails |
| `UnsupportedOperationError` | 501 | Feature not yet implemented |

**Rule:** Internal details (stack traces, DB errors) are **never** returned to the client.
Debug details are shown only when `settings.debug = True`.

---

## Privacy & Security Architecture

### Principles
1. **No secrets in source code.** All keys and credentials in `.env` (never committed).
2. **No raw Aadhaar.** Only SHA-256 hashes of patient identifiers are stored.
3. **No PII in logs.** The `_PIISafeFilter` logging filter strips sensitive fields.
4. **Minimum necessary data.** Collect only what is needed for the clinical history.
5. **Explicit consent.** Two-factor consent required before any clinical data collection.
6. **Session termination.** Completed/abandoned sessions purge in-memory state.
7. **AI as draft.** All AI output is explicitly marked as requiring physician review.
8. **Physician sign-off.** A `DoctorReview` with `status=REVIEWED` is required before clinical use.

### Sensitive Fields (Never Log)
```python
# app/utils/logging.py — _SENSITIVE_FIELDS
"aadhaar", "abha_id", "identifier_hash",
"answer_text", "raw_text", "patient_name",
"display_name", "history_narrative",
"mobile", "phone", "corrections"
```

### ABDM Note
ABDM/ABHA integration is **deferred to Phase 8+** per AGENTS.md Rule 14.
Its architecture must be reviewed for compliance before implementation.

---

## Configuration (`app/config.py`)

All settings are environment-variable driven. Defaults are for local development only.

| Setting | Env Var | Default | Purpose |
|---|---|---|---|
| `app_env` | `APP_ENV` | `development` | Environment name |
| `debug` | `DEBUG` | `true` | Enable debug mode (docs, stack traces) |
| `cors_origins` | `CORS_ORIGINS` | localhost:5173 | Allowed frontend origins |
| `session_ttl_minutes` | `SESSION_TTL_MINUTES` | `60` | Session expiry (minutes) |
| `max_documents_per_session` | `MAX_DOCUMENTS_PER_SESSION` | `10` | Upload limit per session |
| `ai_enabled` | `AI_ENABLED` | `false` | Enable LLM features |
| `log_level` | `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## What Is Intentionally NOT Implemented in Phase 5

| Feature | Reason Deferred |
|---|---|
| PostgreSQL / SQLAlchemy | Phase 6 — adds DB without breaking API contracts |
| Session / Visit / History APIs | Phase 6 — needs DB for persistence |
| Document file storage | Phase 7 — needs storage strategy decision |
| LLM integration | Phase 7+ — needs AI_ENABLED=true and provider selection |
| OCR integration | Phase 7+ — needs provider selection |
| ASR backend | Phase 7+ — frontend Web Speech API is sufficient for now |
| ABDM / FHIR integration | Phase 8+ — compliance review required first |
| Authentication | Phase 6+ — doctor dashboard auth before production |
| Real patient identity verification | Phase 8+ — requires ABDM |

---

## Directory Map

```
backend/
└── app/
    ├── main.py              ← App factory, CORS, exception handlers, lifespan
    ├── config.py            ← All settings (env-var driven)
    │
    ├── api/
    │   ├── router.py        ← Aggregates health + v1 router
    │   └── v1/
    │       ├── health.py    ← GET /api/health (the only live endpoint)
    │       └── router.py    ← Stable registration point for Phase 6+ endpoints
    │
    ├── domain/
    │   ├── models/          ← Reserved for ORM models (Phase 6+)
    │   └── schemas/
    │       ├── session.py   ← KioskSession, SessionStatus
    │       ├── patient.py   ← PatientIdentifier, IdentifierType
    │       ├── consent.py   ← Consent
    │       ├── visit.py     ← Visit
    │       ├── history.py   ← ClinicalHistory, HistoryAnswer, AnswerSource
    │       ├── document.py  ← MedicalDocument, DocumentExtraction, MedicalEntity
    │       ├── summary.py   ← StructuredHistorySummary, ReviewStatus
    │       └── review.py    ← DoctorReview
    │
    ├── services/
    │   ├── session/service.py   ← SessionService Protocol
    │   ├── history/service.py   ← HistoryService Protocol
    │   ├── documents/service.py ← DocumentService Protocol
    │   ├── summary/service.py   ← SummaryService Protocol
    │   └── review/service.py    ← ReviewService Protocol
    │
    ├── infrastructure/
    │   ├── repositories/    ← DB repositories (Phase 6+)
    │   └── integrations/    ← OCR, LLM, ABDM (Phase 7+)
    │
    └── utils/
        ├── errors.py        ← MediKioskError hierarchy
        └── logging.py       ← PII-safe logging configuration
```
