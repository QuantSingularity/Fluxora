"""Tests for data, analytics, predictions, and system endpoints."""

from fastapi.testclient import TestClient

# ===========================================================================
# System
# ===========================================================================


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_docs_endpoint_accessible(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200


# ===========================================================================
# Data – Create
# ===========================================================================


def test_create_record(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 42.5, "cost_usd": 4.25, "temperature_c": 21.0},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["consumption_kwh"] == 42.5
    assert data["cost_usd"] == 4.25
    assert "id" in data
    assert "timestamp" in data
    assert "user_id" in data


def test_create_record_minimal(client: TestClient, auth_headers: dict):
    """Only required field (consumption_kwh) should succeed."""
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0},
    )
    assert response.status_code == 201
    assert response.json()["consumption_kwh"] == 10.0


def test_create_record_with_all_fields(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={
            "consumption_kwh": 55.0,
            "generation_kwh": 10.0,
            "cost_usd": 5.50,
            "temperature_c": 18.5,
            "humidity_percent": 65.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["generation_kwh"] == 10.0
    assert data["humidity_percent"] == 65.0


def test_create_record_negative_consumption_rejected(
    client: TestClient, auth_headers: dict
):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": -5.0},
    )
    assert response.status_code == 422


def test_create_record_invalid_humidity_rejected(
    client: TestClient, auth_headers: dict
):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0, "humidity_percent": 150.0},
    )
    assert response.status_code == 422


def test_create_record_unauthenticated(client: TestClient):
    response = client.post("/v1/data/", json={"consumption_kwh": 42.5})
    assert response.status_code == 401


def test_create_record_missing_consumption_kwh(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"cost_usd": 5.0},
    )
    assert response.status_code == 422


# ===========================================================================
# Data – Read List
# ===========================================================================


def test_read_records_empty(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_read_records_returns_only_own(
    client: TestClient, auth_headers: dict, db_session
):
    """User should only see their own records, not another user's."""
    from backend.security import get_password_hash
    from models.user import User

    other = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpass123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    from datetime import datetime

    from models.data import EnergyData

    record = EnergyData(
        user_id=other.id, consumption_kwh=99.9, timestamp=datetime.utcnow()
    )
    db_session.add(record)
    db_session.commit()

    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_read_records(client: TestClient, auth_headers: dict):
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 10.0})
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 20.0})

    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_records_pagination(client: TestClient, auth_headers: dict):
    for i in range(5):
        client.post(
            "/v1/data/", headers=auth_headers, json={"consumption_kwh": float(i)}
        )

    response = client.get("/v1/data/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_records_invalid_limit(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?limit=0", headers=auth_headers)
    assert response.status_code == 422


def test_read_records_negative_skip(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?skip=-1", headers=auth_headers)
    assert response.status_code == 422


# ===========================================================================
# Data – Get Single Record
# ===========================================================================


def test_get_single_record(
    client: TestClient, auth_headers: dict, sample_energy_record: dict
):
    record_id = sample_energy_record["id"]
    response = client.get(f"/v1/data/{record_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == record_id


def test_get_nonexistent_record(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_another_users_record(client: TestClient, auth_headers: dict, db_session):
    """Getting another user's record by ID should return 404 (not 403) to avoid enumeration."""
    from datetime import datetime

    from backend.security import get_password_hash
    from models.data import EnergyData
    from models.user import User

    other = User(
        email="other2@example.com",
        hashed_password=get_password_hash("otherpass123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    record = EnergyData(
        user_id=other.id, consumption_kwh=99.9, timestamp=datetime.utcnow()
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    response = client.get(f"/v1/data/{record.id}", headers=auth_headers)
    assert response.status_code == 404


# ===========================================================================
# Data – Delete
# ===========================================================================


def test_delete_record(
    client: TestClient, auth_headers: dict, sample_energy_record: dict
):
    record_id = sample_energy_record["id"]
    response = client.delete(f"/v1/data/{record_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/v1/data/{record_id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_nonexistent_record(client: TestClient, auth_headers: dict):
    response = client.delete("/v1/data/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_record_unauthenticated(client: TestClient, sample_energy_record: dict):
    record_id = sample_energy_record["id"]
    response = client.delete(f"/v1/data/{record_id}")
    assert response.status_code == 401


# ===========================================================================
# Data – Time Range Query
# ===========================================================================


def test_query_records_by_time_range(client: TestClient, auth_headers: dict):
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 10.0})

    response = client.get(
        "/v1/data/query?start_time=2000-01-01T00:00:00&end_time=2100-01-01T00:00:00",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_query_records_no_results(client: TestClient, auth_headers: dict):
    response = client.get(
        "/v1/data/query?start_time=2000-01-01T00:00:00&end_time=2000-01-02T00:00:00",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_query_records_invalid_range(client: TestClient, auth_headers: dict):
    """end_time before start_time should be rejected."""
    response = client.get(
        "/v1/data/query?start_time=2024-06-01T00:00:00&end_time=2024-01-01T00:00:00",
        headers=auth_headers,
    )
    assert response.status_code == 422


# ===========================================================================
# Analytics
# ===========================================================================


def test_get_analytics_returns_list(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_week(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=week", headers=auth_headers)
    assert response.status_code == 200


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
    """With no real records, mock data should have required fields."""
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


# ===========================================================================
# Predictions
# ===========================================================================


def test_get_predictions_mock(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 24
    assert "timestamp" in data[0]
    assert "predicted_consumption" in data[0]


def test_get_predictions_default_days(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7 * 24


def test_get_predictions_max_days(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=90", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 90 * 24


def test_get_predictions_invalid_days_zero(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=0", headers=auth_headers)
    assert response.status_code == 422


def test_get_predictions_invalid_days_over_max(client: TestClient, auth_headers: dict):
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


def test_predictions_lower_not_negative_when_positive(
    client: TestClient, auth_headers: dict
):
    """Lower bound of confidence interval should be reasonable (not wildly negative)."""
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    data = response.json()
    for entry in data:
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
    """Superuser can trigger training (returns trained status with mock data)."""
    response = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "trained"
    assert "metrics" in data


def test_train_endpoint_unauthenticated(client: TestClient):
    response = client.post("/v1/predictions/train")
    assert response.status_code == 401


# ===========================================================================
# Feature Engineering
# ===========================================================================


class TestFeatureEngineering:
    def test_create_time_series_features(self):
        import pandas as pd
        from data.features.feature_engineering import create_time_series_features

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=5, freq="h")}
        )
        result = create_time_series_features(df)
        for col in ["hour", "day_of_week", "month", "year", "is_weekend", "quarter"]:
            assert col in result.columns

    def test_create_lag_features(self):
        import pandas as pd
        from data.features.feature_engineering import create_lag_features

        df = pd.DataFrame({"consumption_kwh": range(10)})
        result = create_lag_features(df, "consumption_kwh", lags=[1, 2])
        assert "consumption_kwh_lag_1" in result.columns
        assert "consumption_kwh_lag_2" in result.columns

    def test_create_rolling_features(self):
        import pandas as pd
        from data.features.feature_engineering import create_rolling_features

        df = pd.DataFrame({"consumption_kwh": range(20)})
        result = create_rolling_features(df, "consumption_kwh", windows=[3])
        assert "consumption_kwh_rolling_mean_3" in result.columns
        assert "consumption_kwh_rolling_std_3" in result.columns

    def test_preprocess_pipeline_drops_nan_rows(self):
        import pandas as pd
        from data.features.feature_engineering import preprocess_data_for_model

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=50, freq="h"),
                "consumption_kwh": [float(i) for i in range(50)],
                "user_id": [1] * 50,
            }
        )
        result = preprocess_data_for_model(df)
        assert not result.isnull().any().any()
        assert len(result) < len(df)

    def test_is_weekend_correct(self):
        import pandas as pd
        from data.features.feature_engineering import create_time_series_features

        # 2024-01-06 is Saturday, 2024-01-07 is Sunday
        df = pd.DataFrame(
            {"timestamp": pd.to_datetime(["2024-01-06", "2024-01-07", "2024-01-08"])}
        )
        result = create_time_series_features(df)
        assert result.loc[0, "is_weekend"] == 1
        assert result.loc[1, "is_weekend"] == 1
        assert result.loc[2, "is_weekend"] == 0


# ===========================================================================
# Temporal Features
# ===========================================================================


class TestTemporalFeatures:
    def test_cyclical_features_created(self):
        import pandas as pd
        from features.temporal_features import create_cyclical_features

        df = pd.DataFrame(
            {
                "hour": range(24),
                "day_of_week": [i % 7 for i in range(24)],
                "month": [(i % 12) + 1 for i in range(24)],
            }
        )
        result = create_cyclical_features(df)
        for col in [
            "hour_sin",
            "hour_cos",
            "day_of_week_sin",
            "day_of_week_cos",
            "month_sin",
            "month_cos",
        ]:
            assert col in result.columns

    def test_cyclical_values_in_range(self):
        import pandas as pd
        from features.temporal_features import create_cyclical_features

        df = pd.DataFrame(
            {
                "hour": range(24),
                "day_of_week": [0] * 24,
                "month": [1] * 24,
            }
        )
        result = create_cyclical_features(df)
        assert (result["hour_sin"].between(-1.0, 1.0)).all()
        assert (result["hour_cos"].between(-1.0, 1.0)).all()

    def test_calendar_features_with_timestamp_column(self):
        import pandas as pd
        from features.temporal_features import create_calendar_features

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=10, freq="D")}
        )
        result = create_calendar_features(df)
        assert "is_holiday" in result.columns
        assert "hour_sin" in result.columns


# ===========================================================================
# Model Training
# ===========================================================================


class TestModelTraining:
    def test_load_data_from_db_returns_dataframe(self):
        import pandas as pd
        from models.train import load_data_from_db

        df = load_data_from_db(db_session=None)
        assert isinstance(df, pd.DataFrame)
        assert "timestamp" in df.columns
        assert "consumption_kwh" in df.columns
        assert len(df) > 0

    def test_train_model_returns_model_and_metrics(self):
        from models.train import load_data_from_db, train_model

        df = load_data_from_db(db_session=None)
        model, metrics = train_model(df)
        assert model is not None
        assert "mean_squared_error" in metrics
        assert "r2_score" in metrics
        assert "feature_count" in metrics
        assert "training_samples" in metrics
        assert "test_samples" in metrics
        assert metrics["r2_score"] > -10  # sanity check

    def test_run_training_pipeline(self, tmp_path, monkeypatch):
        import models.train as train_mod

        monkeypatch.setattr(train_mod, "MODEL_PATH", str(tmp_path / "model.joblib"))
        metrics = train_mod.run_training_pipeline(db_session=None)
        assert isinstance(metrics, dict)
        assert "mean_squared_error" in metrics
