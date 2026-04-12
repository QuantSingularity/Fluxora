"""Tests for /v1/data endpoints."""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


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
    response = client.post(
        "/v1/data/", headers=auth_headers, json={"consumption_kwh": 10.0}
    )
    assert response.status_code == 201
    assert response.json()["consumption_kwh"] == 10.0


def test_create_record_all_fields(client: TestClient, auth_headers: dict):
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
        "/v1/data/", headers=auth_headers, json={"consumption_kwh": -5.0}
    )
    assert response.status_code == 422


def test_create_record_negative_cost_rejected(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0, "cost_usd": -1.0},
    )
    assert response.status_code == 422


def test_create_record_negative_generation_rejected(
    client: TestClient, auth_headers: dict
):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0, "generation_kwh": -5.0},
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


def test_create_record_invalid_temperature_rejected(
    client: TestClient, auth_headers: dict
):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 10.0, "temperature_c": 999.0},
    )
    assert response.status_code == 422


def test_create_record_unauthenticated(client: TestClient):
    response = client.post("/v1/data/", json={"consumption_kwh": 42.5})
    assert response.status_code == 401


def test_create_record_missing_consumption_kwh(client: TestClient, auth_headers: dict):
    response = client.post("/v1/data/", headers=auth_headers, json={"cost_usd": 5.0})
    assert response.status_code == 422


def test_create_record_zero_consumption_allowed(client: TestClient, auth_headers: dict):
    response = client.post(
        "/v1/data/", headers=auth_headers, json={"consumption_kwh": 0.0}
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# Read List
# ---------------------------------------------------------------------------


def test_read_records_empty(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_read_records(client: TestClient, auth_headers: dict):
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 10.0})
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 20.0})
    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_records_only_own(client: TestClient, auth_headers: dict, db_session):
    from datetime import datetime, timezone

    from app.core.security import get_password_hash
    from app.models.data import EnergyData
    from app.models.user import User

    other = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpass123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    record = EnergyData(
        user_id=other.id,
        consumption_kwh=99.9,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add(record)
    db_session.commit()

    response = client.get("/v1/data/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_read_records_pagination(
    client: TestClient, multiple_energy_records, auth_headers: dict
):
    response = client.get("/v1/data/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_records_limit_zero_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?limit=0", headers=auth_headers)
    assert response.status_code == 422


def test_read_records_negative_skip_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?skip=-1", headers=auth_headers)
    assert response.status_code == 422


def test_read_records_limit_max(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?limit=1000", headers=auth_headers)
    assert response.status_code == 200


def test_read_records_limit_over_max_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/data/?limit=1001", headers=auth_headers)
    assert response.status_code == 422


def test_read_records_unauthenticated(client: TestClient):
    response = client.get("/v1/data/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Read Single
# ---------------------------------------------------------------------------


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
    from datetime import datetime, timezone

    from app.core.security import get_password_hash
    from app.models.data import EnergyData
    from app.models.user import User

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
        user_id=other.id,
        consumption_kwh=99.9,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    response = client.get(f"/v1/data/{record.id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_record_unauthenticated(client: TestClient, sample_energy_record: dict):
    record_id = sample_energy_record["id"]
    response = client.get(f"/v1/data/{record_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Update (PATCH)
# ---------------------------------------------------------------------------


def test_update_record(
    client: TestClient, auth_headers: dict, sample_energy_record: dict
):
    record_id = sample_energy_record["id"]
    response = client.patch(
        f"/v1/data/{record_id}",
        headers=auth_headers,
        json={"consumption_kwh": 99.9},
    )
    assert response.status_code == 200
    assert response.json()["consumption_kwh"] == 99.9


def test_update_record_partial(
    client: TestClient, auth_headers: dict, sample_energy_record: dict
):
    record_id = sample_energy_record["id"]
    original_cost = sample_energy_record["cost_usd"]
    response = client.patch(
        f"/v1/data/{record_id}",
        headers=auth_headers,
        json={"temperature_c": 30.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["temperature_c"] == 30.0
    assert data["cost_usd"] == original_cost


def test_update_nonexistent_record(client: TestClient, auth_headers: dict):
    response = client.patch(
        "/v1/data/99999", headers=auth_headers, json={"consumption_kwh": 10.0}
    )
    assert response.status_code == 404


def test_update_record_invalid_value_rejected(
    client: TestClient, auth_headers: dict, sample_energy_record: dict
):
    record_id = sample_energy_record["id"]
    response = client.patch(
        f"/v1/data/{record_id}",
        headers=auth_headers,
        json={"consumption_kwh": -10.0},
    )
    assert response.status_code == 422


def test_update_record_unauthenticated(client: TestClient, sample_energy_record: dict):
    record_id = sample_energy_record["id"]
    response = client.patch(f"/v1/data/{record_id}", json={"consumption_kwh": 10.0})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


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


def test_delete_another_users_record(
    client: TestClient, auth_headers: dict, db_session
):
    from datetime import datetime, timezone

    from app.core.security import get_password_hash
    from app.models.data import EnergyData
    from app.models.user import User

    other = User(
        email="other3@example.com",
        hashed_password=get_password_hash("otherpass123"),
        is_active=True,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    record = EnergyData(
        user_id=other.id,
        consumption_kwh=50.0,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    response = client.delete(f"/v1/data/{record.id}", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Time Range Query
# ---------------------------------------------------------------------------


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
    response = client.get(
        "/v1/data/query?start_time=2024-06-01T00:00:00&end_time=2024-01-01T00:00:00",
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_query_records_unauthenticated(client: TestClient):
    response = client.get(
        "/v1/data/query?start_time=2000-01-01T00:00:00&end_time=2100-01-01T00:00:00"
    )
    assert response.status_code == 401
