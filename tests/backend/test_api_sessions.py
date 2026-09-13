"""
Tests for Session API endpoints.

Tests:
    - Create session
    - Retrieve session
    - Record consent
    - Complete/abandon session
    - Session not found (404)
    - Consent validation
    - Session with patient identifier
    - State transition validation
"""

import uuid

from fastapi.testclient import TestClient


class TestCreateSession:
    """Tests for POST /api/v1/sessions."""

    def test_create_session_default(self, db_client: TestClient) -> None:
        """Create a session with default settings."""
        response = db_client.post("/api/v1/sessions", json={})
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert data["language"] == "en"
        assert data["consent_given"] is False
        assert data["patient_identifier"] is None
        # session_id should be a valid UUID
        uuid.UUID(data["session_id"])

    def test_create_session_with_language(self, db_client: TestClient) -> None:
        """Create a session with a specific language."""
        response = db_client.post("/api/v1/sessions", json={"language": "hi"})
        assert response.status_code == 201
        assert response.json()["language"] == "hi"

    def test_create_session_with_patient_identifier(self, db_client: TestClient) -> None:
        """Create a session with a patient identifier."""
        response = db_client.post("/api/v1/sessions", json={
            "language": "en",
            "patient_identifier": {
                "identifier_type": "abha_id",
                "identifier_hash": "a" * 64,
                "display_name": "Test Patient",
            },
        })
        assert response.status_code == 201
        data = response.json()
        assert data["patient_identifier"] is not None
        assert data["patient_identifier"]["identifier_type"] == "abha_id"
        assert data["patient_identifier"]["identifier_hash"] == "a" * 64

    def test_create_session_anonymous(self, db_client: TestClient) -> None:
        """Create a session with anonymous identifier."""
        response = db_client.post("/api/v1/sessions", json={
            "patient_identifier": {
                "identifier_type": "anonymous",
            },
        })
        assert response.status_code == 201
        data = response.json()
        assert data["patient_identifier"]["identifier_type"] == "anonymous"


class TestGetSession:
    """Tests for GET /api/v1/sessions/{session_id}."""

    def test_get_existing_session(self, db_client: TestClient) -> None:
        """Retrieve a session that exists."""
        create_resp = db_client.post("/api/v1/sessions", json={})
        session_id = create_resp.json()["session_id"]

        response = db_client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        assert response.json()["session_id"] == session_id

    def test_get_nonexistent_session(self, db_client: TestClient) -> None:
        """404 on a session that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = db_client.get(f"/api/v1/sessions/{fake_id}")
        assert response.status_code == 404


class TestRecordConsent:
    """Tests for POST /api/v1/sessions/{session_id}/consent."""

    def test_record_consent_success(self, db_client: TestClient) -> None:
        """Successfully record consent."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/consent", json={
            "data_use_acknowledged": True,
            "ai_processing_acknowledged": True,
        })
        assert response.status_code == 200
        assert response.json()["consent_given"] is True

    def test_consent_requires_both_acks(self, db_client: TestClient) -> None:
        """Consent fails if either ack is False."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/consent", json={
            "data_use_acknowledged": True,
            "ai_processing_acknowledged": False,
        })
        assert response.status_code == 403

    def test_consent_requires_data_use(self, db_client: TestClient) -> None:
        """Consent fails if data_use is False."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/consent", json={
            "data_use_acknowledged": False,
            "ai_processing_acknowledged": True,
        })
        assert response.status_code == 403

    def test_consent_session_not_found(self, db_client: TestClient) -> None:
        """Consent on nonexistent session returns 404."""
        fake_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/sessions/{fake_id}/consent", json={
            "data_use_acknowledged": True,
            "ai_processing_acknowledged": True,
        })
        assert response.status_code == 404


class TestCompleteSession:
    """Tests for POST /api/v1/sessions/{session_id}/complete."""

    def test_complete_session(self, db_client: TestClient) -> None:
        """Complete an active session."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_complete_already_completed_session(self, db_client: TestClient) -> None:
        """Cannot complete an already completed session."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        db_client.post(f"/api/v1/sessions/{session_id}/complete")
        response = db_client.post(f"/api/v1/sessions/{session_id}/complete")
        assert response.status_code == 422

    def test_complete_nonexistent_session(self, db_client: TestClient) -> None:
        """Cannot complete a nonexistent session."""
        fake_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/sessions/{fake_id}/complete")
        assert response.status_code == 404


class TestAbandonSession:
    """Tests for POST /api/v1/sessions/{session_id}/abandon."""

    def test_abandon_session(self, db_client: TestClient) -> None:
        """Abandon an active session."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/abandon")
        assert response.status_code == 200
        assert response.json()["status"] == "abandoned"

    def test_cannot_abandon_completed_session(self, db_client: TestClient) -> None:
        """Cannot abandon a completed session."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        db_client.post(f"/api/v1/sessions/{session_id}/complete")
        response = db_client.post(f"/api/v1/sessions/{session_id}/abandon")
        assert response.status_code == 422
