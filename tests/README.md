# MediKiosk Tests

Test suites for backend, AI services, and integration testing.

## Status

Not yet initialized. Tests will be added alongside feature implementation.

## Planned Structure

```
tests/
├── backend/            # Backend API and service tests
├── ai/                 # AI module unit tests
├── integration/        # End-to-end integration tests
├── conftest.py         # Shared pytest fixtures
└── README.md           # This file
```

## Testing Strategy

- **Backend**: pytest + httpx (FastAPI test client)
- **AI Services**: pytest with mocked AI providers
- **Integration**: End-to-end tests covering the full patient journey
- **Frontend**: Vitest + React Testing Library (configured in frontend/)
