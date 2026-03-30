"""
API endpoint tests for Fluxora backend.
"""

import pytest
from typing import Any
from fastapi import status


def test_health_check(client: Any) -> Any:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_create_user(client: Any) -> Any:
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser",
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data


def test_create_user_validation(client: Any) -> Any:
    """Test user creation validation."""
    invalid_email_data = {
        "email": "invalid-email",
        "password": "testpassword123",
        "username": "testuser",
    }
    response = client.post("/api/users/", json=invalid_email_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    short_password_data = {
        "email": "test@example.com",
        "password": "short",
        "username": "testuser",
    }
    response = client.post("/api/users/", json=short_password_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    empty_username_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "",
    }
    response = client.post("/api/users/", json=empty_username_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user(client: Any) -> Any:
    """Test user retrieval endpoint."""
    user_data = {
        "email": "test2@example.com",
        "password": "testpassword123",
        "username": "testuser2",
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_get_nonexistent_user(client: Any) -> Any:
    """Test retrieving a non-existent user."""
    response = client.get("/api/users/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user(client: Any) -> Any:
    """Test user update endpoint."""
    user_data = {
        "email": "test3@example.com",
        "password": "testpassword123",
        "username": "testuser3",
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]
    update_data = {"username": "updateduser", "email": "updated@example.com"}
    response = client.put(f"/api/users/{user_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]


def test_update_nonexistent_user(client: Any) -> Any:
    """Test updating a non-existent user."""
    update_data = {"username": "updateduser", "email": "updated@example.com"}
    response = client.put("/api/users/999999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user(client: Any) -> Any:
    """Test user deletion endpoint."""
    user_data = {
        "email": "test4@example.com",
        "password": "testpassword123",
        "username": "testuser4",
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_user(client: Any) -> Any:
    """Test deleting a non-existent user."""
    response = client.delete("/api/users/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_user_workflow(client: Any) -> Any:
    """Test complete user workflow: create, update, delete."""
    user_data = {
        "email": "workflow@example.com",
        "password": "testpassword123",
        "username": "workflowuser",
    }
    create_response = client.post("/api/users/", json=user_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    user_id = create_response.json()["id"]
    update_data = {"username": "updatedworkflow", "email": "updated@example.com"}
    update_response = client.put(f"/api/users/{user_id}", json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["username"] == update_data["username"]
    delete_response = client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    final_get_response = client.get(f"/api/users/{user_id}")
    assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
