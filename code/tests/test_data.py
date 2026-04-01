"""Tests for data endpoints."""

from fastapi.testclient import TestClient


def test_create_record(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 42.5, "cost_usd": 4.25, "temperature_c": 21.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["consumption_kwh"] == 42.5
    assert "id" in data


def test_read_records_empty(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_read_records(client: TestClient, auth_headers: dict):
    client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0},
    )
    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_record_unauthenticated(client: TestClient):
    response = client.post(
        "/v1/data/",
        json={"consumption_kwh": 42.5},
    )
    assert response.status_code == 401


def test_get_predictions_mock(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 24
    assert "timestamp" in data[0]
    assert "predicted_consumption" in data[0]


def test_get_analytics(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_invalid_period(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=decade", headers=auth_headers)
    assert response.status_code == 400


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
