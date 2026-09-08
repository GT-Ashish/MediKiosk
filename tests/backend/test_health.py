"""
Tests for the GET /api/health endpoint.
"""

from fastapi.testclient import TestClient


def test_health_check_returns_200_and_expected_fields(client: TestClient) -> None:
    """Test that /api/health responds with 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "MediKiosk"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"
    assert "timestamp" in data


def test_health_check_cors_headers(client: TestClient) -> None:
    """Test that CORS headers are returned for allowed origins."""
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_not_found_returns_error_json(client: TestClient) -> None:
    """Test that a non-existent route returns 404."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
