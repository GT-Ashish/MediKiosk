# MediKiosk Backend

Python FastAPI backend for MediKiosk.

## Status

Foundation initialized with FastAPI application entry point, API router, configuration management, error handling, and health check endpoint.

## Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point & error handlers
│   ├── config.py           # Configuration and environment settings (pydantic-settings)
│   └── api/
│       ├── __init__.py
│       ├── router.py       # Central API router
│       └── v1/             # API version 1 routes
│           ├── __init__.py
│           └── health.py   # Health check endpoint (GET /api/health)
├── .env.example            # Environment variable template
├── requirements.txt        # Pinned dependency freeze
└── requirements-dev.txt    # Direct development dependencies
```

## Running Locally

```bash
# Create virtual environment (first time)
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Start development server (port 8000)
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `GET /api/health` — Returns status, version, environment, and timestamp.
- `GET /docs` — Swagger UI API documentation (in development mode).
