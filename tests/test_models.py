from typing import Any

"""
Model tests for Fluxora backend.
"""

from code.models.user import User
from datetime import datetime

import pytest


def test_user_model_creation(db_session: Any) -> Any:
    """Test user model creation and validation."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword123"
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_model_validation(db_session: Any) -> Any:
    """Test user model validation rules."""
    with pytest.raises(ValueError):
        User(
            email="invalid-email",
            username="testuser",
            hashed_password="hashedpassword123",
        )
    with pytest.raises(ValueError):
        User(email="test@example.com", username="", hashed_password="hashedpassword123")
    with pytest.raises(ValueError):
        User(email="test@example.com", username="testuser", hashed_password="")


def test_user_model_unique_constraints(db_session: Any) -> Any:
    """Test user model unique constraints."""
    user1 = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
    )
    db_session.add(user1)
    db_session.commit()
    user2 = User(
        email="test@example.com",
        username="testuser2",
        hashed_password="hashedpassword456",
    )
    db_session.add(user2)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
    user3 = User(
        email="test2@example.com",
        username="testuser",
        hashed_password="hashedpassword789",
    )
    db_session.add(user3)
    with pytest.raises(Exception):
        db_session.commit()


def test_user_model_relationships(db_session: Any) -> Any:
    """Test user model relationships."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
    )
    db_session.add(user)
    db_session.commit()
    assert user.projects == []
    assert user.tasks == []
    assert user.comments == []
