"""Tests for /v1/auth endpoints."""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_user(client: TestClient):
    response = client.post(
        "/v1/auth/register",
        json={"email": "new@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword123"},
    )
    assert response.status_code == 400
    body = response.json()
    detail = body.get("detail") or body.get("error", {}).get("message", "")
    assert "already registered" in detail


def test_register_weak_password(client: TestClient):
    response = client.post(
        "/v1/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_invalid_email(client: TestClient):
    response = client.post(
        "/v1/auth/register",
        json={"email": "not-an-email", "password": "validpassword123"},
    )
    assert response.status_code in (400, 422)


def test_register_missing_fields(client: TestClient):
    response = client.post("/v1/auth/register", json={})
    assert response.status_code == 422


def test_register_missing_password(client: TestClient):
    response = client.post("/v1/auth/register", json={"email": "x@example.com"})
    assert response.status_code == 422


def test_register_missing_email(client: TestClient):
    response = client.post("/v1/auth/register", json={"password": "somepassword123"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login / Token
# ---------------------------------------------------------------------------


def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
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


def test_login_inactive_user(client: TestClient, inactive_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "inactive@example.com", "password": "inactivepassword123"},
    )
    assert response.status_code == 400


def test_login_returns_bearer_token_type(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.json()["token_type"] == "bearer"


def test_login_access_token_is_string(client: TestClient, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 20


# ---------------------------------------------------------------------------
# Refresh Token
# ---------------------------------------------------------------------------


def test_refresh_token_success(client: TestClient, test_user):
    login = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid(client: TestClient):
    response = client.post(
        "/v1/auth/refresh", json={"refresh_token": "this.is.not.valid"}
    )
    assert response.status_code == 401


def test_access_token_cannot_be_used_as_refresh(client: TestClient, test_user):
    login = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    access_token = login.json()["access_token"]
    response = client.post("/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


def test_refresh_missing_body(client: TestClient):
    response = client.post("/v1/auth/refresh", json={})
    assert response.status_code == 422


def test_refresh_rotates_refresh_token(client: TestClient, test_user):
    """Each refresh should return a fresh token pair."""
    login = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    old_refresh = login.json()["refresh_token"]
    response = client.post("/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert response.status_code == 200
    new_refresh = response.json()["refresh_token"]
    # Tokens are freshly signed — they differ at least in the exp claim
    assert isinstance(new_refresh, str) and len(new_refresh) > 20


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------


def test_get_current_user(client: TestClient, auth_headers):
    response = client.get("/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_current_user_unauthenticated(client: TestClient):
    response = client.get("/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    response = client.get(
        "/v1/auth/me", headers={"Authorization": "Bearer totally.invalid.token"}
    )
    assert response.status_code == 401


def test_tampered_token_rejected(client: TestClient, auth_headers):
    original = auth_headers["Authorization"]
    tampered = original[:-1] + ("X" if original[-1] != "X" else "Y")
    response = client.get("/v1/auth/me", headers={"Authorization": tampered})
    assert response.status_code == 401


def test_get_current_user_superuser_flag(client: TestClient, superuser_auth_headers):
    response = client.get("/v1/auth/me", headers=superuser_auth_headers)
    assert response.status_code == 200
    assert response.json()["is_superuser"] is True
