import pytest
from fastapi import status

def test_register_user_success(client, test_user_data):
    response = client.post("/api/v1/users/register", json=test_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["name"] == test_user_data["name"]
    assert data["address"] == test_user_data["address"]
    assert "id" in data
    assert "password" not in data  # Ensure password is not returned

def test_register_user_duplicate_email(client, test_user_data):
    # First registration
    client.post("/api/v1/users/register", json=test_user_data)
    
    # Try to register with same email
    response = client.post("/api/v1/users/register", json=test_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email already registered" in response.json()["detail"].lower()

def test_register_user_invalid_email(client, test_user_data):
    invalid_data = test_user_data.copy()
    invalid_data["email"] = "invalid-email"
    response = client.post("/api/v1/users/register", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_short_password(client, test_user_data):
    invalid_data = test_user_data.copy()
    invalid_data["password"] = "short"
    response = client.post("/api/v1/users/register", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_missing_fields(client):
    # Missing required fields
    response = client.post("/api/v1/users/register", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any(error["loc"][1] == "email" for error in errors)
    assert any(error["loc"][1] == "password" for error in errors)
    assert any(error["loc"][1] == "name" for error in errors) 