"""
Pytest configuration and shared fixtures for MediKiosk.
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
