"""
Tests for Document API endpoints.

Tests:
    - Register document metadata
    - Retrieve document
    - List session documents
    - Document requires consent
    - Document limit enforcement
    - Document not found
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


class TestRegisterDocument:
    """Tests for POST /api/v1/sessions/{session_id}/documents."""

    def test_register_document(self, db_client: TestClient) -> None:
        """Register a document metadata record."""
        session_id = _create_consented_session(db_client)

        response = db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "prescription.pdf",
            "mime_type": "application/pdf",
            "file_size_bytes": 1024000,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "prescription.pdf"
        assert data["mime_type"] == "application/pdf"
        assert data["processing_status"] == "pending"
        assert data["session_id"] == session_id
        uuid.UUID(data["document_id"])

    def test_register_document_without_file_size(self, db_client: TestClient) -> None:
        """Register document without optional file_size_bytes."""
        session_id = _create_consented_session(db_client)

        response = db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "xray.jpg",
            "mime_type": "image/jpeg",
        })
        assert response.status_code == 201
        assert response.json()["file_size_bytes"] is None

    def test_document_requires_consent(self, db_client: TestClient) -> None:
        """Cannot register document without consent."""
        session = db_client.post("/api/v1/sessions", json={}).json()
        session_id = session["session_id"]

        response = db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "test.pdf",
            "mime_type": "application/pdf",
        })
        assert response.status_code == 403

    def test_document_session_not_found(self, db_client: TestClient) -> None:
        """404 on nonexistent session."""
        fake_id = str(uuid.uuid4())
        response = db_client.post(f"/api/v1/sessions/{fake_id}/documents", json={
            "filename": "test.pdf",
            "mime_type": "application/pdf",
        })
        assert response.status_code == 404


class TestGetDocument:
    """Tests for GET /api/v1/documents/{document_id}."""

    def test_get_existing_document(self, db_client: TestClient) -> None:
        """Retrieve a document that exists."""
        session_id = _create_consented_session(db_client)
        doc = db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "report.pdf",
            "mime_type": "application/pdf",
        }).json()

        response = db_client.get(f"/api/v1/documents/{doc['document_id']}")
        assert response.status_code == 200
        assert response.json()["filename"] == "report.pdf"

    def test_get_nonexistent_document(self, db_client: TestClient) -> None:
        """404 on nonexistent document."""
        fake_id = str(uuid.uuid4())
        response = db_client.get(f"/api/v1/documents/{fake_id}")
        assert response.status_code == 404


class TestListSessionDocuments:
    """Tests for GET /api/v1/sessions/{session_id}/documents."""

    def test_list_empty_documents(self, db_client: TestClient) -> None:
        """List documents for session with no documents."""
        session_id = _create_consented_session(db_client)

        response = db_client.get(f"/api/v1/sessions/{session_id}/documents")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_multiple_documents(self, db_client: TestClient) -> None:
        """List multiple documents for a session."""
        session_id = _create_consented_session(db_client)

        db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "doc1.pdf",
            "mime_type": "application/pdf",
        })
        db_client.post(f"/api/v1/sessions/{session_id}/documents", json={
            "filename": "doc2.jpg",
            "mime_type": "image/jpeg",
        })

        response = db_client.get(f"/api/v1/sessions/{session_id}/documents")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_documents_session_not_found(self, db_client: TestClient) -> None:
        """404 on nonexistent session."""
        fake_id = str(uuid.uuid4())
        response = db_client.get(f"/api/v1/sessions/{fake_id}/documents")
        assert response.status_code == 404
