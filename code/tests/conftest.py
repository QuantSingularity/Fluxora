"""
Shared pytest fixtures for the Fluxora test suite.
"""

import app.models.data  # noqa: F401 – registers EnergyData
import app.models.user  # noqa: F401 – registers User
import pytest
from app.core.security import _get_db, get_password_hash
from app.db.dependencies import get_db
from app.main import app
from app.models.base import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _override_get_db(db_session):
    def _inner():
        try:
            yield db_session
        finally:
            pass

    return _inner


@pytest.fixture()
def client(db_session):
    override = _override_get_db(db_session)
    app.dependency_overrides[get_db] = override
    app.dependency_overrides[_get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    from app.models.user import User

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def superuser(db_session):
    from app.models.user import User

    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def inactive_user(db_session):
    from app.models.user import User

    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("inactivepassword123"),
        is_active=False,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(client, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200, response.json()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def superuser_auth_headers(client, superuser):
    response = client.post(
        "/v1/auth/token",
        data={"username": "admin@example.com", "password": "adminpassword123"},
    )
    assert response.status_code == 200, response.json()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_energy_record(client, auth_headers):
    response = client.post(
        "/v1/data/",
        headers=auth_headers,
        json={
            "consumption_kwh": 42.5,
            "cost_usd": 4.25,
            "temperature_c": 21.0,
            "humidity_percent": 55.0,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def multiple_energy_records(client, auth_headers):
    """Creates 5 energy records for pagination / list tests."""
    records = []
    for i in range(1, 6):
        r = client.post(
            "/v1/data/",
            headers=auth_headers,
            json={"consumption_kwh": float(i * 10), "cost_usd": float(i)},
        )
        assert r.status_code == 201
        records.append(r.json())
    return records
