# MediKiosk Tests

Test suites for backend, AI services, and integration testing.

## Status

Backend test suite initialized with pytest and FastAPI TestClient.

## Structure

```
tests/
├── backend/
│   ├── __init__.py
│   └── test_health.py      # Health endpoint & CORS unit tests
├── conftest.py             # Shared pytest fixtures (TestClient)
└── README.md               # This file
```

## Running Tests

```bash
# Run all tests using backend virtualenv
backend\.venv\Scripts\pytest.exe tests/ -v
```
