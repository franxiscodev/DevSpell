"""
Tests para el health endpoint.
"""
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_health_endpoint_returns_200():
    """El endpoint debe retornar status code 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_structure():
    """El endpoint debe retornar la estructura correcta."""
    response = client.get("/api/v1/health")
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "timestamp" in data


def test_health_status_is_healthy():
    """El status debe ser 'healthy'."""
    response = client.get("/api/v1/health")
    data = response.json()

    assert data["status"] == "healthy"
