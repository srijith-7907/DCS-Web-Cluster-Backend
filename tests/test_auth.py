from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "attendee@test.com", "password": "password123", "full_name": "Test Attendee", "role": "ATTENDEE"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "attendee@test.com"
    assert "id" in data


def test_register_duplicate(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "dup@test.com", "password": "password123", "full_name": "Dup", "role": "ATTENDEE"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "dup@test.com", "password": "password123", "full_name": "Dup2", "role": "ATTENDEE"},
    )
    assert response.status_code == 409


def test_register_invalid(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "bad", "password": "123", "full_name": "", "role": "ATTENDEE"},
    )
    assert response.status_code == 422


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "login@test.com", "password": "password123", "full_name": "Login", "role": "ATTENDEE"},
    )
    response = client.post("/auth/login", data={"username": "login@test.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid(client: TestClient):
    response = client.post("/auth/login", data={"username": "nope@test.com", "password": "wrong"})
    assert response.status_code == 401


def test_auth_failure(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
