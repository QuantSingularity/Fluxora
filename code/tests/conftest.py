"""
Shared pytest fixtures for Fluxora test suite.
"""

import models.data  # noqa: F401
import models.user  # noqa: F401
import pytest
from backend.dependencies import get_db
from backend.security import _get_db, get_password_hash
from fastapi.testclient import TestClient
from main import app
from models.base import Base
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
    """Return a FastAPI dependency override that yields the given session."""

    def _inner():
        try:
            yield db_session
        finally:
            pass

    return _inner


@pytest.fixture()
def client(db_session):
    # Override BOTH get_db and _get_db so security.py's chain also uses
    # the test session.
    override = _override_get_db(db_session)
    app.dependency_overrides[get_db] = override
    app.dependency_overrides[_get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    from models.user import User

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
def auth_headers(client, test_user):
    response = client.post(
        "/v1/auth/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200, response.json()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
