"""
Tests for Visit API endpoints.

Tests:
    - Create visit
    - Retrieve visit
    - Visit requires consent
    - Visit not found
    - Visit with department
"""

import uuid

from fastapi.testclient import TestClient


def _create_consented_session(client: TestClient) -> str:
    """Helper: create a session and record consent."""
    session = client.post("/api/v1/sessions", json={}).json()
    session_id = session["session_id"]
    client.post(f"/api/v1/sessions/{session_id}/consent", json={
        "data_use_acknowledged": True,
        "ai_processing_acknowledged": True,
    })
    return session_id


class TestCreateVisit:
    """Tests for POST /api/v1/sessions/{session_id}/visits."""

    def test_create_visit(self, db_client: TestClient) -> None:
        """Create a visit for a consented session."""
        session_id = _create_consented_session(db_client)

        response = db_client.post(f"/api/v1/sessions/{session_id}/visits", json={
            "chief_complaint": "chest pain",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["chief_complaint"] == "chest pain"
        assert data["session_id"] == session_id
        uuid.UUID(data["visit_id"])

    def test_create_visit_with_department(self, db_client: TestClient) -> None:
        """Create a visit with a department."""
        session_id = _create_consented_session(db_client)

        response = db_client.post(f"/api/v1/sessions/{session_id}/visits", json={
            "chief_complaint": "headache",
            "department": "Neurology",
        })
        assert response.status_code == 201
        assert response.json()["department"] == "Neurology"

    def test_visit_requires_consent(self, db_client: TestClient) -> None:
        """Cannot create visit without consent."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/visits", json={
            "chief_complaint": "fatigue",
        })
        assert response.status_code == 403

    def test_visit_session_not_found(self, db_client: TestClient) -> None:
        """404 on nonexistent session."""
        fake_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/sessions/{fake_id}/visits", json={
            "chief_complaint": "dizziness",
        })
        assert response.status_code == 404


class TestGetVisit:
    """Tests for GET /api/v1/visits/{visit_id}."""

    def test_get_existing_visit(self, db_client: TestClient) -> None:
        """Retrieve a visit that exists."""
        session_id = _create_consented_session(db_client)
        visit = db_client.post(f"/api/v1/sessions/{session_id}/visits", json={
            "chief_complaint": "nausea",
        }).json()

        response = db_client.get(f"/api/v1/visits/{visit['visit_id']}")
        assert response.status_code == 200
        assert response.json()["chief_complaint"] == "nausea"

    def test_get_nonexistent_visit(self, db_client: TestClient) -> None:
        """404 on nonexistent visit."""
        fake_id = str(uuid.uuid4())
        response = db_client.get(f"/api/v1/visits/{fake_id}")
        assert response.status_code == 404
