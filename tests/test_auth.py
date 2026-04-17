import uuid
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def generate_unique_user():
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique_id}",
        "email": f"user_{unique_id}@example.com",
        "full_name": "Test User",
        "password": "secure123"
    }

def test_register_success():
    user_data = generate_unique_user()

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "data" in data

    user = data["data"]
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]
    assert user["full_name"] == user_data["full_name"]
    assert user["role"] == "member"
    assert user["is_active"] is True
    assert "id" in user
    assert "created_at" in user

    # Password should never be returned
    assert "password" not in user
    assert "password_hash" not in user

def test_login_success():
    user_data = generate_unique_user()

    # First register the user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # Then login with same credentials
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 20

    def test_protected_endpoint_requires_token():
        response = client.get("/api/v1/users")

        assert response.status_code == 401

        data = response.json()
        assert data["error"] == "unauthorized"
        assert data["status_code"] == 401

def test_protected_endpoint_with_valid_token():
    user_data = generate_unique_user()

    # Register the user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Access protected endpoint with token
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "data" in data
    assert "pagination" in data

    def test_register_user_success(client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "strongpassword"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_login_user_success(client):
    # first register
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "full_name": "Login User",
                "password": "strongpassword"
            }
        )

    # login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "loginuser",
                "password": "strongpassword"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

def test_get_users_protected(client):
    # register + login
    client.post("/api/v1/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "full_name": "User One",
        "password": "strongpassword"
    })

    login = client.post("/api/v1/auth/login", data={
        "username": "user1",
        "password": "strongpassword"
    })

    token = login.json()["access_token"]

    # access protected route
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200