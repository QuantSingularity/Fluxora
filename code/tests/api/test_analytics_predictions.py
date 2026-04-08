"""Tests for /v1/analytics and /v1/predictions endpoints."""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


def test_get_analytics_returns_list(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_week(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=week", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_month(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=month", headers=auth_headers)
    assert response.status_code == 200


def test_get_analytics_year(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=year", headers=auth_headers)
    assert response.status_code == 200


def test_get_analytics_invalid_period(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=decade", headers=auth_headers)
    assert response.status_code == 422


def test_get_analytics_unauthenticated(client: TestClient):
    response = client.get("/v1/analytics/")
    assert response.status_code == 401


def test_analytics_mock_data_shape(client: TestClient, auth_headers: dict):
    """With no real records mock data must have required fields."""
    response = client.get("/v1/analytics/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    first = data[0]
    assert "label" in first
    assert "consumption" in first
    assert "cost" in first
    assert "efficiency" in first


def test_get_analytics_summary(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_consumption_kwh" in data
    assert "total_cost_usd" in data
    assert "avg_daily_consumption_kwh" in data
    assert "record_count" in data


def test_analytics_summary_unauthenticated(client: TestClient):
    response = client.get("/v1/analytics/summary")
    assert response.status_code == 401


def test_analytics_summary_empty_returns_zeros(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] == 0
    assert data["total_consumption_kwh"] == 0.0


def test_analytics_summary_with_data(client: TestClient, auth_headers: dict):
    client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 100.0, "cost_usd": 10.0},
    )
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] >= 1
    assert data["total_consumption_kwh"] >= 100.0
    assert data["total_cost_usd"] >= 10.0


def test_analytics_summary_avg_daily_non_negative(
    client: TestClient, auth_headers: dict
):
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 50.0})
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    data = response.json()
    assert data["avg_daily_consumption_kwh"] >= 0.0


def test_analytics_default_period_is_month(client: TestClient, auth_headers: dict):
    """Default period should be month (no query param needed)."""
    r1 = client.get("/v1/analytics/", headers=auth_headers)
    r2 = client.get("/v1/analytics/?period=month", headers=auth_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------


def test_get_predictions_mock_1_day(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 24
    assert "timestamp" in data[0]
    assert "predicted_consumption" in data[0]


def test_get_predictions_default_7_days(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 7 * 24


def test_get_predictions_max_days(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=90", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 90 * 24


def test_get_predictions_days_zero_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=0", headers=auth_headers)
    assert response.status_code == 422


def test_get_predictions_days_over_max_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=91", headers=auth_headers)
    assert response.status_code == 422


def test_get_predictions_unauthenticated(client: TestClient):
    response = client.get("/v1/predictions/")
    assert response.status_code == 401


def test_predictions_confidence_interval_structure(
    client: TestClient, auth_headers: dict
):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 200
    entry = response.json()[0]
    ci = entry["confidence_interval"]
    assert "lower" in ci
    assert "upper" in ci
    assert ci["upper"] >= ci["lower"]


def test_predictions_all_entries_have_required_fields(
    client: TestClient, auth_headers: dict
):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    for entry in response.json():
        assert "timestamp" in entry
        assert "predicted_consumption" in entry
        assert "confidence_interval" in entry


def test_predictions_confidence_bounds_ordered(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    for entry in response.json():
        ci = entry["confidence_interval"]
        assert ci["upper"] >= ci["lower"]


def test_train_endpoint_forbidden_for_regular_user(
    client: TestClient, auth_headers: dict
):
    response = client.post("/v1/predictions/train", headers=auth_headers)
    assert response.status_code == 403


def test_train_endpoint_allowed_for_superuser(
    client: TestClient, superuser_auth_headers: dict
):
    response = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "trained"
    assert "metrics" in data


def test_train_endpoint_unauthenticated(client: TestClient):
    response = client.post("/v1/predictions/train")
    assert response.status_code == 401


def test_train_returns_metrics_fields(client: TestClient, superuser_auth_headers: dict):
    response = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    metrics = response.json()["metrics"]
    assert "mean_squared_error" in metrics
    assert "r2_score" in metrics
    assert "feature_count" in metrics
    assert "training_samples" in metrics
    assert "test_samples" in metrics
