from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_register_validation_error_missing_email():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "ranveer",
            "full_name": "Ranveer Mane",
            "password": "secure123"
        }
    )

    assert response.status_code == 422

    data = response.json()
    assert data["error"] == "validation_error"
    assert data["message"] == "Request validation failed"
    assert data["status_code"] == 422
    assert "details" in data

def test_register_validation_error_short_password():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "ranveer",
            "email": "ranveer@example.com",
            "full_name": "Ranveer Mane",
            "password": "123"
        }
    )

    assert response.status_code == 422

    data = response.json()
    assert data["error"] == "validation_error"
    assert data["message"] == "Request validation failed"
    assert data["status_code"] == 422
    assert "details" in data