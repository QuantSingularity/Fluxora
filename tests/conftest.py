from typing import Any

"""
Common test fixtures for Fluxora backend tests.
"""

from code.backend.dependencies import get_db
from code.backend.main import app
from code.models.base import Base

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_db_engine() -> Any:
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine: Any) -> Any:
    """Create a new database session for a test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Any) -> Any:
    """Create a test client with a test database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
