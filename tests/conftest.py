"""
Pytest configuration and shared fixtures for MediKiosk.

Provides two test client fixtures:
  - client: Original Phase 5 fixture (sync, for backward compatibility)
  - db_client: Phase 6 fixture with in-memory SQLite database

The db_client fixture uses the application's async database infrastructure
with an in-memory SQLite database (via aiosqlite). The FastAPI TestClient
handles the async-to-sync bridge transparently.
"""

import sys
from pathlib import Path
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client fixture for making requests to FastAPI app."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_client() -> Generator[TestClient, None, None]:
    """
    Test client with in-memory SQLite database.

    Overrides DATABASE_URL to use in-memory SQLite (via aiosqlite),
    ensuring each test gets a fresh database with all tables created
    via the application's normal lifespan handler.
    """
    import os

    # Override env to use in-memory SQLite
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
    os.environ["APP_ENV"] = "development"

    # Clear settings cache so new env vars are picked up
    from app.config import Settings
    app = create_app()

    with TestClient(app) as test_client:
        yield test_client

    # Restore
    os.environ.pop("DATABASE_URL", None)
