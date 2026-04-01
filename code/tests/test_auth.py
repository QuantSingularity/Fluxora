"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/v1/auth/register",
        json={"email": "new@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


def test_register_duplicate_email(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 400
    body = response.json()
    # The error is surfaced either as {"detail": "..."} (FastAPI default)
    # or {"error": {"message": "..."}} (custom error handler).
    detail = body.get("detail") or body.get("error", {}).get("message", "")
    assert "already registered" in detail


def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client: TestClient):
    response = client.post(
        "/v1/auth/token",
        data={"username": "nobody@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401
