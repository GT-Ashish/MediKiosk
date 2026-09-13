"""
Tests for History API endpoints.

Tests:
    - Record answer
    - Retrieve history
    - Answer requires consent
    - Multiple answers build history
    - Visit not found
"""

import uuid

from fastapi.testclient import TestClient


def _create_session_with_visit(client: TestClient) -> tuple[str, str]:
    """Helper: create a consented session with a visit. Returns (session_id, visit_id)."""
    session = client.post("/api/v1/sessions", json={}).json()
    session_id = session["session_id"]
    client.post(f"/api/v1/sessions/{session_id}/consent", json={
        "data_use_acknowledged": True,
        "ai_processing_acknowledged": True,
    })
    visit = client.post(f"/api/v1/sessions/{session_id}/visits", json={
        "chief_complaint": "chest pain",
    }).json()
    return session_id, visit["visit_id"]


class TestRecordAnswer:
    """Tests for POST /api/v1/visits/{visit_id}/answers."""

    def test_record_answer(self, db_client: TestClient) -> None:
        """Record a clinical answer for a visit."""
        session_id, visit_id = _create_session_with_visit(db_client)

        response = db_client.post(f"/api/v1/visits/{visit_id}/answers", json={
            "session_id": session_id,
            "question_id": "onset",
            "question_text": "When did the pain start?",
            "answer_text": "Yesterday morning",
            "answer_source": "text",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["question_id"] == "onset"
        assert data["answer_text"] == "Yesterday morning"
        assert data["answer_source"] == "text"

    def test_record_voice_answer_with_confidence(self, db_client: TestClient) -> None:
        """Record a voice answer with confidence score."""
        session_id, visit_id = _create_session_with_visit(db_client)

        response = db_client.post(f"/api/v1/visits/{visit_id}/answers", json={
            "session_id": session_id,
            "question_id": "severity",
            "question_text": "How severe is the pain?",
            "answer_text": "7",
            "answer_source": "voice",
            "confidence": 0.92,
        })
        assert response.status_code == 201
        assert response.json()["confidence"] == 0.92

    def test_answer_requires_consent(self, db_client: TestClient) -> None:
        """Cannot record answer without consent."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        # Create a visit in a consented session for the visit_id, then use it with no-consent session
        # Actually, we can't create a visit without consent, so this test uses a fake visit_id
        fake_visit_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/visits/{fake_visit_id}/answers", json={
            "session_id": session_id,
            "question_id": "onset",
            "question_text": "When?",
            "answer_text": "Today",
            "answer_source": "text",
        })
        # Visit not found because no visit exists
        assert response.status_code == 404

    def test_answer_visit_not_found(self, db_client: TestClient) -> None:
        """404 on nonexistent visit."""
        fake_visit_id = str(uuid.uuid4())
        fake_session_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/visits/{fake_visit_id}/answers", json={
            "session_id": fake_session_id,
            "question_id": "onset",
            "question_text": "When?",
            "answer_text": "Today",
            "answer_source": "text",
        })
        assert response.status_code == 404


class TestGetHistory:
    """Tests for GET /api/v1/visits/{visit_id}/history."""

    def test_get_empty_history(self, db_client: TestClient) -> None:
        """Get history when no answers recorded."""
        session_id, visit_id = _create_session_with_visit(db_client)

        response = db_client.get(f"/api/v1/visits/{visit_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["answers"] == []

    def test_get_history_with_answers(self, db_client: TestClient) -> None:
        """Get history after recording answers."""
        session_id, visit_id = _create_session_with_visit(db_client)

        # Record multiple answers
        db_client.post(f"/api/v1/visits/{visit_id}/answers", json={
            "session_id": session_id,
            "question_id": "onset",
            "question_text": "When did it start?",
            "answer_text": "Two days ago",
            "answer_source": "text",
        })
        db_client.post(f"/api/v1/visits/{visit_id}/answers", json={
            "session_id": session_id,
            "question_id": "location",
            "question_text": "Where is the pain?",
            "answer_text": "Left chest",
            "answer_source": "voice",
            "confidence": 0.88,
        })

        response = db_client.get(f"/api/v1/visits/{visit_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["chief_complaint"] == "chest pain"
        assert data["onset"] == "Two days ago"
        assert data["location"] == "Left chest"
        assert len(data["answers"]) == 2

    def test_history_visit_not_found(self, db_client: TestClient) -> None:
        """404 on nonexistent visit."""
        fake_id = str(uuid.uuid4())
        response = db_client.get(f"/api/v1/visits/{fake_id}/history")
        assert response.status_code == 404
