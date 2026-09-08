# MediKiosk Backend

Python FastAPI backend.

## Status

Not yet initialized. This directory will contain the FastAPI application once scaffolding begins.

## Planned Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration and environment settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/             # API version 1 routes
│   │       ├── __init__.py
│   │       ├── history.py  # Clinical history endpoints
│   │       ├── documents.py # Document upload/processing endpoints
│   │       ├── summary.py  # Summary generation endpoints
│   │       └── patients.py # Patient management endpoints
│   ├── models/             # SQLAlchemy / Pydantic models
│   ├── services/           # Business logic layer
│   ├── schemas/            # Request/response schemas
│   └── utils/              # Utility functions
├── requirements.txt
└── requirements-dev.txt
```
