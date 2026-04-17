from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint_returns_200():
    response = client.get("/health")

    assert response.status_code == 200

def test_health_endpoint_response_structure():
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "app" in data
    assert "version" in data
    assert "timestamp" in data

def test_health_endpoint_status_value():
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert data["app"] == "DevCollab API"