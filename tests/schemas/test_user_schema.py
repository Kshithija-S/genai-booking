import pytest
from pydantic import ValidationError, EmailStr
from app.schemas.user import UserCreate, UserResponse

def test_user_create_valid_data():
    data = {
        "email": "test@example.com",
        "password": "validpassword123",
        "name": "Test User",
        "address": "123 Test St"
    }
    user = UserCreate(**data)
    assert user.email == data["email"]
    assert user.password == data["password"]
    assert user.name == data["name"]
    assert user.address == data["address"]

def test_user_create_invalid_email():
    data = {
        "email": "invalid-email",
        "password": "validpassword123",
        "name": "Test User",
        "address": "123 Test St"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**data)
    assert "email" in str(exc_info.value)

def test_user_create_short_password():
    data = {
        "email": "test@example.com",
        "password": "short",
        "name": "Test User",
        "address": "123 Test St"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**data)
    assert "password" in str(exc_info.value)

def test_user_create_missing_fields():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate()
    errors = exc_info.value.errors()
    assert len(errors) == 3  # email, password, and name are required
    assert any(error["loc"][0] == "email" for error in errors)
    assert any(error["loc"][0] == "password" for error in errors)
    assert any(error["loc"][0] == "name" for error in errors)

def test_user_response_schema():
    data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "address": "123 Test St"
    }
    user = UserResponse(**data)
    assert user.id == data["id"]
    assert user.email == data["email"]
    assert user.name == data["name"]
    assert user.address == data["address"]
    assert not hasattr(user, "password")  # Password should not be in response

def test_user_response_extra_fields():
    data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "address": "123 Test St",
        "password": "shouldnotbehere"  # Extra field
    }
    user = UserResponse(**data)
    assert not hasattr(user, "password")  # Extra field should be ignored 