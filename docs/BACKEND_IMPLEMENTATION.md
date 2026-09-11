# MediKiosk — Backend Implementation

> **Status:** Phase 5 — Architecture / Contracts only. The backend currently defines the full layered architecture (API → Services → Domain → Infrastructure ports) but **no persistence, no real AI providers, and no authentication are implemented yet**. Only the health endpoint is fully functional; all other HTTP routes return a structured `501 Not Implemented` response.
>
> **Documentation date:** 2026-09-10 · **Scope:** `MediKiosk/backend/` (+ relevant frontend/tests/docs)
> **Commit documented:** `27e137a` — "feat: defined the backend architecture" (HEAD of `main`, 8 commits total)

---

## 1. Backend Overview

MediKiosk is a multilingual, self-service hospital kiosk application. The backend is an **ASGI service built with FastAPI** that will eventually orchestrate:

- Anonymous kiosk **sessions** (no login; a kiosk terminal starts a session)
- **Patient identification** using masked identifiers only (never full Aadhaar)
- **Visits** and clinical **history taking** (voice/ASR-assisted, AI-rephrased questions)
- **Document uploads** with OCR extraction and entity extraction (AI)
- **AI-generated structured summaries** that always start as drafts and carry a mandatory disclaimer
- **Doctor review** workflow (accept / edit / reject)

### Phase 5 reality (verified against the code)

- The backend is **contract-only**: domain models, API schemas, service classes, repository ABCs, and provider Protocols are all defined.
- **Only `GET /api/health` is functional.**
- Service methods that would need a real database or AI provider raise `NotImplementedYetError` → **HTTP 501**. Read-only/creation service methods are **implemented as thin delegates** to the repository ports — but since no concrete repository exists yet, they cannot run end-to-end.
- There is **no database**, **no authentication**, and **no concrete AI/OCR/ASR/ABDM implementation**.
- This matches the design in [`docs/backend-architecture.md`](backend-architecture.md) and the rules in [`AGENTS.md`](../AGENTS.md).

### Core design invariants (enforced by tests)

| Invariant | Where enforced |
|---|---|
| Sessions are anonymous; no patient PII on the session object | `KioskSession` model + `test_session_is_anonymous` |
| Patient identifiers never hold a full Aadhaar number | `PatientIdentifier.masked_id` + `test_patient_identifier_never_holds_full_aadhaar` |
| A visit always begins in `history_in_progress` | `Visit` model + `test_visit_begins_in_history_in_progress` |
| Summaries are born as `AI_DRAFT` with a non-empty disclaimer | `StructuredHistorySummary` + 2 tests |
| A doctor review always requires an explicit action | `DoctorReview` + `test_doctor_review_requires_action` |
| Errors map to stable HTTP status codes | `MediKioskError` hierarchy + `test_error_hierarchy_maps_to_http_status` |
| Phase 5 boundary is signalled with 501 | `NotImplementedYetError` + `test_not_implemented_error_signal_phase5_boundary` |
| PII is redacted in logs | `sanitize_for_log()` + 2 tests |

---

## 2. Folder Structure

```
MediKiosk/
├── AGENTS.md                        # Project rules (14 rules: secrets, layering, AI, clinical safety, testing, ABDM deferred)
├── README.md                        # Project overview
├── backend/
│   ├── .env.example                 # Template for environment variables
│   ├── README.md                    # Backend quick-start
│   ├── requirements.txt             # ⚠️ Pinned freeze, UTF-16 encoded (see Known Issues)
│   ├── requirements-dev.txt         # Top-level dev dependencies (readable)
│   ├── .venv/                       # Local virtual environment (not committed)
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI app factory, lifespan, exception handlers
│       ├── config.py                # Pydantic-settings Settings
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py            # api_router: health (unversioned) + /v1 sessions
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── health.py        # GET /api/health (functional)
│       │       └── sessions.py      # POST/GET /api/v1/sessions (501 stubs)
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models/              # Pure Pydantic domain entities
│       │   │   ├── session.py       # KioskSession, SessionStatus
│       │   │   ├── patient.py       # PatientIdentifier, IdentificationMethod, Gender
│       │   │   ├── visit.py         # Visit, VisitType, VisitStatus
│       │   │   ├── history.py       # ClinicalHistory, ChiefComplaint, HistoryAnswer, InputMethod
│       │   │   ├── document.py      # MedicalDocument, DocumentExtraction, ExtractedEntity, ...
│       │   │   └── review.py        # StructuredHistorySummary, DoctorReview, SummaryStatus, ...
│       │   └── schemas/             # HTTP request/response contracts
│       │       ├── common.py        # ErrorResponse, SuccessResponse[T], PaginatedResponse[T]
│       │       ├── session.py
│       │       ├── patient.py
│       │       ├── visit.py
│       │       ├── history.py
│       │       ├── document.py
│       │       └── summary.py       # SummaryResponse (mandatory ai_disclaimer)
│       ├── services/                # Use-case orchestration (many methods raise NotImplementedYetError)
│       │   ├── base.py              # not_implemented(service_name, method_name) helper
│       │   ├── session_service.py
│       │   ├── patient_service.py
│       │   ├── visit_service.py
│       │   ├── history_service.py
│       │   ├── document_service.py
│       │   ├── summary_service.py
│       │   └── review_service.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   └── base.py          # 7 repository ABCs (ports)
│       │   └── integrations/        # External provider Protocols (ports)
│       │       ├── __init__.py
│       │       ├── ai.py            # LLMProvider Protocol
│       │       ├── ocr.py           # OCRProvider Protocol + OCRResult
│       │       ├── asr.py           # ASRProvider Protocol + TranscriptionResult
│       │       └── abdm.py          # ABDMGateway Protocol (deferred by rule)
│       └── utils/
│           ├── __init__.py
│           ├── errors.py            # MediKioskError hierarchy → HTTP codes
│           └── logging.py           # get_logger, sanitize_for_log, configure_logging
├── tests/
│   ├── conftest.py                  # sys.path setup + TestClient fixture
│   ├── README.md                    # How to run tests
│   └── backend/
│       ├── __init__.py
│       ├── test_health.py           # 3 tests
│       ├── test_architecture.py     # 11 tests (invariants)
│       └── test_stub_routes.py      # 3 tests (501 stubs)
├── docs/
│   ├── README.md
│   ├── backend-architecture.md      # Phase 5 architecture design (350 lines)
│   └── BACKEND_IMPLEMENTATION.md    # ⬅ This document
├── ai/README.md                     # "Not yet initialized" — planned only
├── database/README.md               # "Not yet initialized" — planned only
├── scripts/README.md                # "Not yet initialized" — planned only
└── frontend/                        # React + Vite kiosk UI (see §11)
```

---

## 3. Setup & Dependencies

### Declared dependencies

**`backend/requirements-dev.txt`** (top-level, readable):

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
pytest
httpx
```

**`backend/requirements.txt`** — a pinned freeze. ⚠️ **The file is UTF-16 encoded** (this is a known issue, see §17). After normalizing the encoding, the pinned versions are:

| Package | Version |
|---|---|
| `fastapi` | 0.141.1 |
| `uvicorn` | 0.52.4 |
| `pydantic` | 2.13.5 |
| `pydantic-settings` | 2.15.0 |
| `python-dotenv` | (present) |
| `pytest` | 9.1.1 |
| `httpx` | 0.28.1 |
| (plus transitive pinned deps) | — |

### Environment

- A local virtual environment exists at `backend/.venv/`.
- Tests are run with the venv's pytest (see §13 and [`tests/README.md`](../tests/README.md)).

### Setup steps (as implied by the repo)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements-dev.txt
pip install -r requirements.txt  # ⚠️ may need UTF-16 conversion first, see §17
copy .env.example .env           # then edit values as needed
```

> There is no lockfile/poetry/uv config; plain pip + requirements files only.

---

## 4. Entry Point

### `backend/app/main.py`

The application is built by a factory `create_app()`:

- **App metadata:** `title="MediKiosk"`, `version="0.1.0"`.
- **Docs:** `/docs` (Swagger UI) and `/redoc` are enabled **only when `settings.debug` is True**. In production (`debug=False`) the interactive docs are disabled.
- **Middleware:** `CORSMiddleware` is registered (see §9).
- **Exception handlers** (see §10):
  1. `MediKioskError` → JSON `{error_code, message, detail?}`
  2. `HTTPException` → `{error_code: "HTTP_ERROR", message, status_code}`
  3. Generic `Exception` → `{error_code: "INTERNAL_ERROR"}` with HTTP 500
- **Router:** `app.include_router(api_router, prefix="/api")` (see §5).
- **Lifespan:** on startup calls `configure_logging()` and logs startup; logs shutdown on exit.
- A **module-level `app = create_app()`** exists so `uvicorn app.main:app` works directly.

### `backend/app/config.py`

`Settings(BaseSettings)` loads from environment variables (and a `.env` file via `env_file=".env"`):

| Field | Default |
|---|---|
| `app_name` | `"MediKiosk"` |
| `app_version` | `"0.1.0"` |
| `app_env` | `"development"` |
| `debug` | `True` |
| `host` | `"0.0.0.0"` |
| `port` | `8000` |
| `cors_origins` | `"http://localhost:5173,http://127.0.0.1:5173"` |

- `cors_origins_list` — a `@property` that splits the comma-separated string into a list for the CORS middleware.
- `get_settings()` — returns a **fresh** `Settings()` on each call (no caching). Modules that need stable values capture it at import time (e.g. `health.py` does `settings = get_settings()` at module level).

> No secret/credential fields exist in config yet (no API keys, no DB URLs). `DATABASE_URL` appears only as a commented-out example in `.env.example`.

---

## 5. API Documentation

Router mounting in [`backend/app/api/router.py`](backend/app/api/router.py):

- `health.router` is included **without a version prefix** → routes appear at `/api/...`
- `sessions.router` is included with `prefix="/v1"` → routes appear at `/api/v1/...`

### 5.1 `GET /api/health` — ✅ Functional

Defined in [`backend/app/api/v1/health.py`](backend/app/api/v1/health.py).

Response model `HealthResponse`:

```json
{
  "status": "healthy",
  "app_name": "MediKiosk",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-09-10T05:00:00Z"
}
```

- `timestamp` is generated with `datetime.now(timezone.utc).isoformat()` (ISO-8601 UTC).

### 5.2 `POST /api/v1/sessions` — ⚠️ Stub (501)

Defined in [`backend/app/api/v1/sessions.py`](backend/app/api/v1/sessions.py).

Request body: `CreateSessionRequest` — `{ "terminal_id": "string | null" }`.

Behavior: the route **directly** raises `not_implemented("SessionService", "create_session")` → HTTP **501**. It does **not** instantiate or call `SessionService` — Phase 5 keeps the router as a pure interface contract (the service class itself does contain a working `create_session`, but it needs a repository implementation that does not exist yet).

Response (the structured error body all stubs share):

```json
{
  "error_code": "NOT_IMPLEMENTED",
  "message": "SessionService.create_session is not implemented yet (Phase 5 boundary).",
  "detail": null
}
```

### 5.3 `GET /api/v1/sessions/{session_id}` — ⚠️ Stub (501)

Same file. Path parameter `session_id: str`. Also raises `not_implemented("SessionService", "get_session")` directly → **501** with `NOT_IMPLEMENTED`.

### 5.4 Planned but not yet routed endpoints

The architecture doc and service/schema layers define future endpoints (session consent/terminate, patient identify, visit create, history interview, documents, summary generate/review). **None of these are mounted in `router.py` yet.** See [`docs/backend-architecture.md`](backend-architecture.md) for the future API surface table.

### 5.5 Error body shape

All errors use `ErrorResponse` (see [`domain/schemas/common.py`](backend/app/domain/schemas/common.py)):

```json
{
  "error_code": "string",
  "message": "string",
  "detail": "string | null"
}
```

---

## 6. Authentication

**Not implemented. There is no authentication or authorization layer of any kind.**

- No OAuth, JWT, API keys, sessions tokens, or login endpoints exist.
- The kiosk model is intentionally **anonymous**: a `KioskSession` is tied to a `terminal_id`, not to a person.
- **ABDM / ABHA integration is explicitly deferred** (AGENTS.md rule 14; see [`backend/app/infrastructure/integrations/abdm.py`](backend/app/infrastructure/integrations/abdm.py)) — it exists only as a `Protocol` with placeholder method bodies.
- Consent recording is modelled (schema `RecordConsentRequest`, service `record_consent`) but not implemented; consent scopes are part of the future ABHA flow.

---

## 7. Database

**No database exists.** There is:

- **No ORM** (no SQLAlchemy), **no migrations** (no Alembic), **no connection layer**.
- [`database/README.md`](../database/README.md) states the database is **"not yet initialized — planned only"**.
- `.env.example` contains only a **commented-out** `DATABASE_URL` example.

### The persistence port (what will be implemented)

[`backend/app/infrastructure/repositories/base.py`](backend/app/infrastructure/repositories/base.py) defines **7 abstract repository interfaces** (all `async`, all domain-model based) that a future Phase 6 persistence layer must implement:

| ABC | Methods (all `async`) |
|---|---|
| `SessionRepository` | `create`, `get`, `update`, `delete` |
| `PatientRepository` | `create`, `get`, `get_by_session` |
| `VisitRepository` | `create`, `get`, `get_by_session`, `update_status` |
| `HistoryRepository` | `create`, `get_by_visit`, `save_answer`, `save_chief_complaint`, `complete` |
| `DocumentRepository` | `create`, `get`, `list_by_visit`, `update_status`, `save_extraction` |
| `SummaryRepository` | `create`, `get_by_visit`, `update_status` |
| `ReviewRepository` | `create`, `get`, `list_by_visit` |

These are **ports only** — no in-memory, SQLite, or Postgres implementation exists yet.

---

## 8. AI Integration

All AI integrations are **Protocols (structural typing ports) — no concrete providers, no API keys, no model wiring** exist.

### 8.1 `LLMProvider` — [`backend/app/infrastructure/integrations/ai.py`](backend/app/infrastructure/integrations/ai.py)

| Method | Purpose |
|---|---|
| `rephrase_question(question_text, language_code)` | Rephrase a clinical question for patient comprehension |
| `extract_history_structure(history)` | Structure free-form history answers |
| `extract_document_entities(raw_text)` | Extract `ExtractedEntity` list from OCR text |
| `generate_summary(...)` | Generate a structured summary (returns `StructuredHistorySummary`) |

All method bodies are `...` (Ellipsis) placeholders.

### 8.2 `OCRProvider` — [`backend/app/infrastructure/integrations/ocr.py`](backend/app/infrastructure/integrations/ocr.py)

- `OCRResult` — frozen dataclass: `{ text: str, provider: str, confidence: float }`.
- `OCRProvider` Protocol — single method: `async def extract_text(storage_ref: str) -> OCRResult`.

### 8.3 `ASRProvider` — [`backend/app/infrastructure/integrations/asr.py`](backend/app/infrastructure/integrations/asr.py)

- `TranscriptionResult` — frozen dataclass: `{ text: str, provider: str, confidence: float, language_code: str }`.
- `ASRProvider` Protocol — single method: `async def transcribe(audio_ref: str, language_code: str) -> TranscriptionResult`.

### 8.4 `ABDMGateway` — [`backend/app/infrastructure/integrations/abdm.py`](backend/app/infrastructure/integrations/abdm.py)

**Explicitly deferred** (AGENTS.md rule 14). Exists only as a `Protocol` with placeholder bodies:

| Method | Purpose |
|---|---|
| `verify_abha_otp(transaction_id, otp)` | Verify ABHA OTP during consent flow |
| `create_abha_health_id(masked_aadhaar_ref)` | Create ABHA health ID from masked Aadhaar reference |
| `fetch_fhir_record(abha_address)` | Fetch FHIR records for an ABHA address |

### 8.5 Clinical AI safety boundaries (enforced by domain models)

- **No autonomous diagnosis** — the AI only structures/rephrases/extracts; the system never renders a diagnosis.
- Summaries are **born as `AI_DRAFT`** (`SummaryStatus.AI_DRAFT`) and only a physician can move them through `PHYSICIAN_REVIEWING` to `PHYSICIAN_CONFIRMED` / `PHYSICIAN_EDITED` / `PHYSICIAN_REJECTED` (via `ReviewAction` = `CONFIRM` / `EDIT` / `REJECT`).
- Every `StructuredHistorySummary` carries `ai_disclaimer` whose default is the constant **`AI_DRAFT_DISCLAIMER`**; the field has a `min_length` validation so it can never be empty.
- Red-flag detection (`HistoryService._check_red_flags`) is intended to be **deterministic rule-based** logic, not AI-driven — currently stubbed.

---

## 9. Middleware

The **only middleware** registered is **CORS** (in [`backend/app/main.py`](backend/app/main.py) via `CORSMiddleware`):

| Setting | Value |
|---|---|
| `allow_origins` | `settings.cors_origins_list` (default: `http://localhost:5173`, `http://127.0.0.1:5173`) |
| `allow_credentials` | `True` |
| `allow_methods` | `["*"]` |
| `allow_headers` | `["*"]` |

There is **no** authentication middleware, no request-logging middleware, no rate limiting, and no custom ASGI middleware. Error normalization is handled by exception handlers instead (see §10). The Vite dev proxy (frontend side) forwards `/api` to `http://localhost:8000` (see §11).

---

## 10. Validation & Error Handling

### 10.1 Request validation

- All request/response contracts are **Pydantic v2 models** in [`backend/app/domain/schemas/`](backend/app/domain/schemas/).
- FastAPI validates request bodies/params automatically; a failed validation yields the standard FastAPI `422` (with the global `HTTPException` handler formatting the body).
- Notable validations: `SummaryResponse.ai_disclaimer` has `min_length=1`; session/patient schemas use optional fields with defaults; `PaginatedResponse[T]` is a generic wrapper.

### 10.2 Error hierarchy — [`backend/app/utils/errors.py`](backend/app/utils/errors.py)

`MediKioskError(message, *, detail=None)` is the base class. Subclasses carry a fixed `status_code` and `error_code`:

| Exception | HTTP | `error_code` | When raised |
|---|---|---|---|
| `MediKioskError` (base) | 500 | `INTERNAL_ERROR` | Unknown application error |
| `SessionNotFoundError` | 404 | `SESSION_NOT_FOUND` | Session lookup failed |
| `SessionExpiredError` | 410 | `SESSION_EXPIRED` | Session past its expiry |
| `ConsentRequiredError` | 403 | `CONSENT_REQUIRED` | Operation needs patient consent (e.g. `VisitService.create_visit` gate) |
| `InvalidStateError` | 409 | `INVALID_STATE` | Workflow transition not allowed in current state |
| `DocumentNotFoundError` | 404 | `DOCUMENT_NOT_FOUND` | Document lookup failed |
| `DocumentProcessingError` | 422 | `DOCUMENT_PROCESSING_ERROR` | OCR/extraction failed |
| `AIProcessingError` | 503 | `AI_PROCESSING_ERROR` | AI provider unavailable/failed |
| `SummaryNotReadyError` | 409 | `SUMMARY_NOT_READY` | Summary requested before generation |
| `ReviewNotFoundError` | 404 | `REVIEW_NOT_FOUND` | Review lookup failed |
| `NotImplementedYetError` | 501 | `NOT_IMPLEMENTED` | Phase 5 boundary — method not yet implemented |

### 10.3 Exception handlers (in `create_app()`)

1. **`MediKioskError`** → `JSONResponse(status_code=exc.status_code)` with `{error_code, message, detail}`; when `settings.debug` is True the handler adds a `debug` key with `exception_type` and `exception_repr`.
2. **`HTTPException`** → `{error_code: "HTTP_ERROR", message: exc.detail, status_code}`.
3. **Generic `Exception`** → HTTP 500 `{error_code: "INTERNAL_ERROR", message: "Internal server error"}`. (Logging of unexpected exceptions is expected via the lifespan logger.)

---

## 11. Frontend Communication

The frontend (`frontend/`) is a **React 18 + TypeScript + Vite** SPA. Backend communication is currently limited to the health check; everything else is **mocked client-side** (see [`frontend/src/data/mockData.ts`](../frontend/src/data/mockData.ts)).

### 11.1 API base URL — [`frontend/src/config.ts`](../frontend/src/config.ts)

```ts
apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? ''
```

- In development the Vite proxy forwards `/api` to the backend, so `VITE_API_BASE_URL` is usually empty.

### 11.2 Dev proxy — [`frontend/vite.config.ts`](../frontend/vite.config.ts)

```ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

Dev server port: **5173**. The kiosk frontend talks to the backend through the proxy at the same origin.

### 11.3 Health check call — [`frontend/src/services/api.ts`](../frontend/src/services/api.ts)

```ts
fetchHealthStatus()  // GET `${apiBaseUrl}/api/health`
```

- Returns a typed `HealthStatus` (`status`, `app_name`, `version`, `environment`, `timestamp`).
- Consumed by [`frontend/src/hooks/useHealthCheck.ts`](../frontend/src/hooks/useHealthCheck.ts) (polling/refresh logic) and rendered by [`frontend/src/components/HealthStatus.tsx`](../frontend/src/components/HealthStatus.tsx) (success/error/loading states).
- [`frontend/src/App.tsx`](../frontend/src/App.tsx) wires the kiosk flow (language → identification → consent → complaint → history → documents → review) plus a `/dev/doctor` dashboard route.

### 11.4 Contract alignment

- The frontend's `HealthStatus` interface matches `HealthResponse` exactly (same field names/types).
- All other frontend flows (sessions, patient, visit, history, documents, summary) currently operate on local mock data and **do not call the backend yet** — the future `/api/v1/...` endpoints (see §5.4) will replace them.
- The `ai_disclaimer` requirement in `SummaryResponse` and the `AI_DRAFT_DISCLAIMER` constant are backend-side contracts the frontend review page will need to display.

---

## 12. Environment Variables

Source of truth: [`backend/app/config.py`](backend/app/config.py) (loaded via `pydantic-settings`, `env_file=".env"`). Template: [`backend/.env.example`](backend/.env.example).

| Variable | Type | Default | Used by |
|---|---|---|---|
| `APP_NAME` | str | `MediKiosk` | app metadata, health response |
| `APP_VERSION` | str | `0.1.0` | app metadata, health response |
| `APP_ENV` | str | `development` | health response `environment` |
| `DEBUG` | bool | `True` | enables `/docs`, `/redoc`, rich error debug info |
| `HOST` | str | `0.0.0.0` | uvicorn binding |
| `PORT` | int | `8000` | uvicorn binding |
| `CORS_ORIGINS` | str (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` | CORS `allow_origins` |

Notes:

- `DATABASE_URL` exists only as a **commented-out** example in `.env.example` — not read by config.
- **No API keys, tokens, or secrets are configured anywhere.** Any future provider keys (AI/OCR/ASR/ABDM) must be added via `Settings` and must never be committed (see AGENTS.md rule on secrets).
- Frontend variable: `VITE_API_BASE_URL` (see §11.1, template [`frontend/.env.example`](../frontend/.env.example)).

---

## 13. Tests

Location: [`tests/`](../tests/). Runner: `backend\.venv\Scripts\pytest.exe tests/ -v` (from repo root, per [`tests/README.md`](../tests/README.md)).

### 13.1 Harness — [`tests/conftest.py`](../tests/conftest.py)

- Adds the `backend/` directory to `sys.path` so `app.*` imports resolve.
- `client` fixture: builds `create_app()` and wraps it in FastAPI's `TestClient`.

### 13.2 `tests/backend/test_health.py` — 3 tests

1. `test_health_check_returns_200_and_expected_fields` — status 200, body has `status`, `app_name`, `version`, `environment`, `timestamp`.
2. `test_health_check_cors_headers` — CORS header present on the response.
3. `test_not_found_returns_error_json` — unknown route returns JSON error body (not HTML).

### 13.3 `tests/backend/test_architecture.py` — 11 tests (domain invariants)

1. `test_session_is_anonymous` — session model has no patient PII fields.
2. `test_patient_identifier_never_holds_full_aadhaar` — masked ID only.
3. `test_visit_begins_in_history_in_progress` — default visit status.
4. `test_summary_always_starts_as_ai_draft` — default `SummaryStatus.AI_DRAFT`.
5. `test_summary_disclaimer_cannot_be_empty` — `AI_DRAFT_DISCLAIMER` non-empty + validation.
6. `test_doctor_review_requires_action` — `ReviewAction` is required.
7. `test_error_hierarchy_maps_to_http_status` — each error has expected HTTP code.
8. `test_errors_are_medi_kiosk_errors` — all exceptions subclass `MediKioskError`.
9. `test_not_implemented_error_signal_phase5_boundary` — 501 + `NOT_IMPLEMENTED`.
10. `test_sanitize_for_log_redacts_pii` — sensitive field values replaced with `[REDACTED]`.
11. `test_sanitize_is_case_insensitive` — redaction matches field names case-insensitively.

### 13.4 `tests/backend/test_stub_routes.py` — 3 tests

1. `test_sessions_create_returns_501_stub`
2. `test_sessions_get_returns_501_stub`
3. `test_health_still_works_after_stub_routes`

### 13.5 Coverage note

Tests cover the **contracts and invariants only** — there is no persistence or AI behavior to test yet. CI config is not present in the repo.

---

## 14. Security

### 14.1 Privacy by design (verified in code + tests)

- **No full Aadhaar anywhere.** `PatientIdentifier.masked_id` holds a masked reference (format like `XXXX-XXXX-1234`); `test_patient_identifier_never_holds_full_aadhaar` enforces this.
- **No government-ID primary keys.** All entities use UUID-style string IDs (`new_uuid()` helper in [`backend/app/services/__init__.py`](backend/app/services/__init__.py)).
- **Anonymous sessions.** `KioskSession` stores only `terminal_id`/workflow state, never patient identity.
- **Minimum necessary data.** Schemas and models only carry the fields the flow needs.
- **ABHA only with explicit consent.** `link_abha` requires `consented_at`; consent scopes are recorded via `RecordConsentRequest`.
- **Privacy-safe logging.** [`backend/app/utils/logging.py`](backend/app/utils/logging.py) defines `_SENSITIVE_FIELD_NAMES` (e.g. aadhaar, phone, name, address, abha) and `sanitize_for_log()` replaces their values with `[REDACTED]` (case-insensitive); `get_logger()` returns a logger, `configure_logging(debug)` sets formatting/handlers.

### 14.2 What does NOT exist yet

- No authentication/authorization (see §6).
- No encryption at rest or in transit config (TLS is a deployment concern; no certs in repo).
- No rate limiting / brute-force protection on consent or identification endpoints.
- No audit logging beyond the logger scaffold.
- No secrets in config — but also **no secret management** yet.

### 14.3 Clinical safety

- No autonomous diagnosis (see §8.5).
- AI output is always a draft with disclaimer; final sign-off is human (`DoctorReview` with explicit `ReviewAction`).

---

## 15. Request Flows

### 15.1 Health check (the only fully implemented flow)

```
Frontend (useHealthCheck)  →  GET /api/health   (via Vite proxy :5173 → :8000)
                                  │
                                  ▼
                    health_check() → HealthResponse
                    (status, app_name, version, environment, timestamp)
```

### 15.2 Stubbed flow — create session (shows the intended path)

```
POST /api/v1/sessions  (CreateSessionRequest)
   │
   ▼
sessions.create_session()            [api/v1/sessions.py]
   │   └─ raises not_implemented("SessionService","create_session")
   ▼
MediKioskError handler → 501 {"error_code":"NOT_IMPLEMENTED", ...}
```

> Note: the router raises the 501 directly and does **not** call `SessionService`. The service class itself already contains a working `create_session()` (builds a `KioskSession` and calls `SessionRepository.create`), but no concrete repository exists to back it.

### 15.3 Designed (future) flow — full visit pipeline

The service layer already encodes the intended sequence (DB/AI steps that need a real repository/provider raise 501 today; the rest are thin port delegates awaiting Phase 6 persistence):

1. **Session** — `SessionService.create_session` → `record_consent` → `update_workflow_state` (consent gate: `ConsentRequiredError`).
2. **Patient** — `PatientService.identify_patient` (by masked ID) → optional `link_abha` (requires `consented_at`).
3. **Visit** — `VisitService.create_visit` **requires consent** (raises `ConsentRequiredError` otherwise); visit starts in `history_in_progress`.
4. **History** — `HistoryService.start_interview` → `next_question` (LLM rephrase) → `submit_answer` (ASR) → `submit_chief_complaint` → `complete_interview` → `_check_red_flags` (deterministic rules).
5. **Documents** — `DocumentService.register_upload` → `process_document` (OCR → LLM entity extraction → `DocumentExtraction`).
6. **Summary** — `SummaryService.generate_summary` → `StructuredHistorySummary` (born `AI_DRAFT` + disclaimer).
7. **Review** — `ReviewService.record_review` with explicit `ReviewAction` (`CONFIRM` / `EDIT` / `REJECT`; immutable audit record) → summary transitions to `PHYSICIAN_CONFIRMED` / `PHYSICIAN_EDITED` / `PHYSICIAN_REJECTED` → `SummaryService.mark_reviewed`.

### 15.4 Error flow

Any raised `MediKioskError` subclass propagates to the `MediKioskError` exception handler, which emits the `ErrorResponse` shape with the error's fixed HTTP status (see §10.2). Unknown exceptions fall through to the generic handler (500).

---

## 16. Implementation Status

### Legend

- ✅ **Done** — implemented and (where applicable) tested
- ⚠️ **Partial** — implemented as thin port delegates (need a real repository/AI provider to run end-to-end); only AI/state-machine/ABDM methods raise 501
- 🔜 **Planned** — designed in schemas/services but **not mounted** as routes
- ❌ **Absent** — not started

| Area | Status | Details |
|---|---|---|
| App factory / lifespan / config | ✅ Done | `create_app()`, logging, settings |
| `GET /api/health` | ✅ Done | Only functional endpoint |
| CORS middleware | ✅ Done | Dev origins, credentials, `*` methods/headers |
| Exception handlers (3) | ✅ Done | `MediKioskError`, `HTTPException`, `Exception` |
| Error hierarchy | ✅ Done | 10 concrete errors + base, fixed HTTP codes |
| Domain models (6 files) | ✅ Done | Session, Patient, Visit, History, Document, Review |
| API schemas (7 files) | ✅ Done | Request/response contracts incl. generics |
| Repository ABCs (7) | ✅ Done | Ports only — no implementation |
| Provider Protocols (AI/OCR/ASR/ABDM) | ⚠️ Partial | Interface + dataclasses; bodies are `...`; no concrete adapter |
| `SessionService` | ⚠️ Partial | `create_session`/`get_session`/`update_workflow_state`/`record_consent`/`terminate_session` implemented (delegate to `SessionRepository`); `expire_inactive_sessions` raises 501 |
| `PatientService` | ⚠️ Partial | `identify_patient`/`get_patient`/`get_patient_for_session` implemented; `link_abha` raises 501 (deferred, rule 14) |
| `VisitService` | ⚠️ Partial | `create_visit` (consent gate) / `get_visit` / `get_visit_for_session` implemented; `transition_status` raises 501 |
| `HistoryService` | ⚠️ Partial | `start_interview`/`get_history` implemented; `next_question`/`submit_answer`/`submit_chief_complaint`/`complete_interview`/`_check_red_flags` raise 501 |
| `DocumentService` | ⚠️ Partial | `get_document`/`list_documents` implemented; `register_upload`/`process_document`/`get_extraction` raise 501 |
| `SummaryService` | ⚠️ Partial | `get_summary` implemented; `generate_summary`/`mark_reviewed` raise 501 |
| `ReviewService` | ⚠️ Partial | `get_summary_for_review`/`list_reviews` implemented; `record_review` raises 501 |
| Sessions API routes | ⚠️ Stub | POST + GET raise 501 directly (tests assert this); they do **not** invoke `SessionService` |
| Authentication | ❌ Absent | None at all |
| Database / persistence | ❌ Absent | Ports only; `database/` is "planned only" |
| AI / OCR / ASR / ABDM providers | ❌ Absent | Protocols only; no concrete adapter |
| Frontend backend calls | ⚠️ Partial | Only health check real; rest uses `mockData.ts` |
| ABDM/ABHA integration | 🔜 Deferred | Explicitly deferred (AGENTS.md rule 14) |

### Implemented service methods (thin delegates to repository ports)

These contain working orchestration logic but cannot run end-to-end until a concrete repository (and, where relevant, an AI provider) exists in Phase 6:

- `SessionService`: `create_session`, `get_session` (raises `SessionExpiredError` on expired), `update_workflow_state`, `record_consent`, `terminate_session`
- `PatientService`: `identify_patient`, `get_patient`, `get_patient_for_session`
- `VisitService`: `create_visit` (raises `ConsentRequiredError` if no consent), `get_visit`, `get_visit_for_session`
- `HistoryService`: `start_interview`, `get_history`
- `DocumentService`: `get_document`, `list_documents`
- `SummaryService`: `get_summary`
- `ReviewService`: `get_summary_for_review`, `list_reviews`

### Stub inventory (methods raising `NotImplementedYetError` → 501)

- `SessionService`: `expire_inactive_sessions`
- `PatientService`: `link_abha`
- `VisitService`: `transition_status`
- `HistoryService`: `next_question`, `submit_answer`, `submit_chief_complaint`, `complete_interview`, `_check_red_flags`
- `DocumentService`: `register_upload`, `process_document`, `get_extraction`
- `SummaryService`: `generate_summary`, `mark_reviewed`
- `ReviewService`: `record_review`

> `not_implemented(service_name, method_name)` in [`backend/app/services/base.py`](backend/app/services/base.py) produces the standard `NotImplementedYetError` message: `"<Service>.<method>() is a Phase 5 interface contract. Implementation is deferred to Phase 6 (database + API)."` (HTTP 501, `error_code="NOT_IMPLEMENTED"`).

---

## 17. Known Issues, TODOs & Limitations

### 17.1 ⚠️ `backend/requirements.txt` is UTF-16 encoded

- Verified: the file contains UTF-16 BOM/null bytes; standard tools (`pip install -r`, most editors/`cat`) may garble or fail on it.
- **Impact:** `pip install -r requirements.txt` can mis-parse dependency names/versions.
- **Workaround:** re-save as UTF-8, or install from `requirements-dev.txt` (which is clean UTF-8).
- **TODO:** re-encode `requirements.txt` as UTF-8.

### 17.2 Phase 5 boundary — contracts + thin port delegates

- Methods that need a real database or AI provider raise `NotImplementedYetError` (501) — this is **by design**, not a bug.
- Most read/create service methods are **implemented as thin delegates** to the repository ports; they will only run end-to-end once Phase 6 provides concrete repositories (and AI providers where relevant).
- No routes exist yet for patient/visit/history/document/summary/review — only `health` and the two session stubs (which raise 501 directly without touching the service layer).

### 17.3 No persistence

- No repository implementations, no migrations, no seed data. `DATABASE_URL` is commented out. Nothing survives a restart.

### 17.4 No authentication / authorization

- Session termination, consent, doctor review endpoints will need an auth story before Phase 6 (kiosk terminal auth vs. doctor auth).

### 17.5 No concrete AI providers

- `LLMProvider`, `OCRProvider`, `ASRProvider` are Protocols only. There are no API keys, model names, prompts, or fallback logic. No evaluation harness for clinical summarization quality.

### 17.6 ABDM / ABHA deferred

- Per AGENTS.md rule 14, the ABDM gateway is placeholder-only. No sandbox credentials, no consent flow, no FHIR parsing.

### 17.7 Logging scaffold only

- `sanitize_for_log()` and `configure_logging()` exist and are tested for redaction, but there is **no request logging middleware** and no structured log emission yet in request paths.

### 17.8 Frontend is mostly mocked

- The kiosk UI flow works on `mockData.ts`; only the health check is wired to the backend. Contract drift between frontend types and backend schemas is possible until endpoints land.

### 17.9 Misc

- No CI configuration in the repo.
- `docs/backend-architecture.md` is the authoritative design; if this document and that doc ever disagree on the future API surface, the architecture doc wins.
- No `.env` file is committed (correct); `.env.example` is the template.

---

## 18. How to Run

### Backend (dev)

```bash
cd backend
.venv\Scripts\activate                 # Windows (activate the venv)
uvicorn app.main:app --reload          # default: http://localhost:8000
```

- API root: `http://localhost:8000/api`
- Interactive docs: `http://localhost:8000/docs` and `/redoc` — **only when `DEBUG=true`** (the `.env.example` default is `debug=True` for development).

### Frontend (dev)

```bash
cd frontend
npm install
npm run dev                            # http://localhost:5173
```

- The Vite dev proxy forwards `/api` → `http://localhost:8000`, so the frontend needs the backend running to show real health status.

### Tests

From the repo root (`MediKiosk/`):

```bash
backend\.venv\Scripts\pytest.exe tests/ -v
```

Expected: **17 tests pass** (3 health + 11 architecture + 3 stub routes).

### Environment

Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` and adjust `DEBUG`, `CORS_ORIGINS`, etc. No secrets are required at this phase.

---

## 19. Change History

Captured from `git log` at documentation time (branch `main`, **8 commits**, working tree clean).

| Commit | Subject | Relevance |
|---|---|---|
| `27e137a` | feat: defined the backend architecture | **HEAD** — Phase 5 backend (43 files added, +3397 lines): API, services, domain, infrastructure, tests, docs |
| (earlier commits) | frontend / project scaffolding | Kiosk UI setup, mock data, i18n, docs scaffolding |

Notes:

- The current backend state was introduced essentially in one architecture commit (`27e137a`); before it, the backend did not exist as code.
- `main` is **1 commit ahead of `origin/main`** (the architecture commit is not yet pushed).
- Working tree is **clean** at the time of writing; this documentation file is a new addition.

---

## 20. File-by-File Reference

### Entry / config

| File | What it does |
|---|---|
| [`backend/app/main.py`](backend/app/main.py) | `create_app()` factory; lifespan (logging); CORS; 3 exception handlers; mounts `api_router` under `/api`; module-level `app` |
| [`backend/app/config.py`](backend/app/config.py) | `Settings` (pydantic-settings, `.env`), `cors_origins_list`, `get_settings()` |
| [`backend/app/api/router.py`](backend/app/api/router.py) | `api_router` — health (no prefix) + sessions under `/v1` |

### API v1

| File | Routes | Status |
|---|---|---|
| [`backend/app/api/v1/health.py`](backend/app/api/v1/health.py) | `GET /health` | ✅ Functional |
| [`backend/app/api/v1/sessions.py`](backend/app/api/v1/sessions.py) | `POST ""`, `GET /{session_id}` | ⚠️ 501 stubs |

### Domain models ([`backend/app/domain/models/`](backend/app/domain/models/))

| File | Contents |
|---|---|
| `session.py` | `KioskSession` (anonymous; `terminal_id`, workflow state), `SessionStatus` |
| `patient.py` | `PatientIdentifier` (`masked_id`, `phone_masked`, `abha_address`), `IdentificationMethod`, `Gender` |
| `visit.py` | `Visit` (default status `history_in_progress`), `VisitType`, `VisitStatus` |
| `history.py` | `ClinicalHistory`, `ChiefComplaint`, `HistoryAnswer` (ASR confidence), `InputMethod` |
| `document.py` | `MedicalDocument`, `DocumentExtraction`, `ExtractedEntity`, `DocumentType`, `DocumentStatus` |
| `review.py` | `StructuredHistorySummary` (born `AI_DRAFT`, `AI_DRAFT_DISCLAIMER`), `DoctorReview`, `SummaryStatus`, `ReviewAction` |

### API schemas ([`backend/app/domain/schemas/`](backend/app/domain/schemas/))

| File | Contents |
|---|---|
| `common.py` | `ErrorResponse`, `SuccessResponse[T]`, `PaginatedResponse[T]` |
| `session.py` | `CreateSessionRequest`, `SessionResponse`, `UpdateSessionRequest`, `RecordConsentRequest`, `TerminateSessionRequest` |
| `patient.py` | `IdentifyPatientRequest` (masked), `PatientResponse` |
| `visit.py` | `CreateVisitRequest`, `VisitResponse` |
| `history.py` | `SubmitAnswerRequest`, `ChiefComplaintRequest`, `HistoryAnswerResponse`, `ClinicalHistoryResponse` |
| `document.py` | `DocumentUploadMetadata`, `DocumentResponse`, `DocumentListResponse`, `TriggerProcessingRequest` |
| `summary.py` | `GenerateSummaryRequest`, `SummaryResponse` (mandatory `ai_disclaimer`) |

### Services ([`backend/app/services/`](backend/app/services/))

| File | Implemented (thin delegates) | Stubbed (501) |
|---|---|---|
| `base.py` | `not_implemented()` helper | — |
| `session_service.py` | create_session / get_session / update_workflow_state / record_consent / terminate_session | expire_inactive_sessions |
| `patient_service.py` | identify_patient / get_patient / get_patient_for_session | link_abha |
| `visit_service.py` | create_visit (consent gate) / get_visit / get_visit_for_session | transition_status |
| `history_service.py` | start_interview / get_history | next_question / submit_answer / submit_chief_complaint / complete_interview / _check_red_flags |
| `document_service.py` | get_document / list_documents | register_upload / process_document / get_extraction |
| `summary_service.py` | get_summary | generate_summary / mark_reviewed |
| `review_service.py` | get_summary_for_review / list_reviews | record_review |

### Infrastructure

| File | Contents |
|---|---|
| [`backend/app/infrastructure/repositories/base.py`](backend/app/infrastructure/repositories/base.py) | 7 async repository ABCs (Session, Patient, Visit, History, Document, Summary, Review) |
| [`backend/app/infrastructure/integrations/ai.py`](backend/app/infrastructure/integrations/ai.py) | `LLMProvider` Protocol (4 methods, `...` bodies) |
| [`backend/app/infrastructure/integrations/ocr.py`](backend/app/infrastructure/integrations/ocr.py) | `OCRProvider` Protocol + `OCRResult` dataclass |
| [`backend/app/infrastructure/integrations/asr.py`](backend/app/infrastructure/integrations/asr.py) | `ASRProvider` Protocol + `TranscriptionResult` dataclass |
| [`backend/app/infrastructure/integrations/abdm.py`](backend/app/infrastructure/integrations/abdm.py) | `ABDMGateway` Protocol (deferred per rule 14) |

### Utils

| File | Contents |
|---|---|
| [`backend/app/utils/errors.py`](backend/app/utils/errors.py) | `MediKioskError` base + 10 concrete errors with fixed HTTP codes |
| [`backend/app/utils/logging.py`](backend/app/utils/logging.py) | `get_logger()`, `sanitize_for_log()` (PII redaction), `configure_logging()` |

### Tests ([`tests/`](../tests/))

| File | Contents |
|---|---|
| [`tests/conftest.py`](../tests/conftest.py) | `sys.path` setup; `client` fixture (TestClient over `create_app()`) |
| [`tests/backend/test_health.py`](../tests/backend/test_health.py) | 3 tests: health 200 + fields, CORS header, 404 JSON |
| [`tests/backend/test_architecture.py`](../tests/backend/test_architecture.py) | 11 tests: domain invariants + error codes + PII redaction |
| [`tests/backend/test_stub_routes.py`](../tests/backend/test_stub_routes.py) | 3 tests: session stubs return 501; health still works |
| [`tests/README.md`](../tests/README.md) | Test run instructions |

### Supporting docs

| File | Purpose |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | 14 project rules (secrets, layering, clinical safety, testing, ABDM deferred) |
| [`docs/backend-architecture.md`](backend-architecture.md) | Phase 5 architecture design (authoritative for future API surface) |
| [`backend/README.md`](backend/README.md) | Backend quick-start |
| [`backend/.env.example`](backend/.env.example) | Env var template |
| [`database/README.md`](../database/README.md) | "Not yet initialized - planned only" |
| [`ai/README.md`](../ai/README.md), [`scripts/README.md`](../scripts/README.md) | Planned only |
| [`frontend/src/services/api.ts`](../frontend/src/services/api.ts) | `fetchHealthStatus()` — the only real frontend→backend call |

---

## 21. Final Summary

### What this backend is

A **Phase 5 contract-only FastAPI backend**: a complete, tested layered skeleton (API → Services → Domain → Infrastructure ports) that defines *how* MediKiosk will work, with only the health endpoint live and everything stateful/AI-marked as `NotImplementedYetError` (501).

### What works today

- `GET /api/health` (the single functional endpoint)
- App factory, config, CORS, structured error handling (3 handlers, 11 error types)
- Full domain model + schema layer with clinical-safety invariants
- 17 passing tests covering contracts, error codes, and PII redaction

### What does not exist yet (all documented above)

- Database/persistence (repository ABCs only), authentication, concrete AI/OCR/ASR/ABDM providers, session/patient/visit/history/document/summary/review routes (only session stubs are mounted), ABDM/ABHA flow, request logging middleware, CI.

### Headline issues

1. `requirements.txt` is **UTF-16 encoded** — re-encode to UTF-8 (§17.1).
2. DB/AI-dependent methods are **501 by design** until Phase 6; most read/create service methods are implemented as thin port delegates (§17.2).
3. **No auth** before patient-facing/doctor endpoints go live (§17.4).
4. Frontend is **mock-driven** except health (§17.8).

> No secrets (API keys, tokens, passwords) appear anywhere in this document or in the inspected codebase — none exist in the repo yet.