import pytest
from pydantic import EmailStr, ValidationError
from app.schemas.auth import LoginRequest, Token, TokenData

def test_login_request_valid():
    """Test valid login request data"""
    data = {
        "email": "test@example.com",
        "password": "validpassword123"
    }
    login_request = LoginRequest(**data)
    assert login_request.email == "test@example.com"
    assert login_request.password == "validpassword123"

def test_login_request_invalid_email():
    """Test login request with invalid email"""
    data = {
        "email": "invalid-email",
        "password": "validpassword123"
    }
    with pytest.raises(ValidationError):
        LoginRequest(**data)

def test_token_valid():
    """Test valid token data"""
    data = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    }
    token = Token(**data)
    assert token.access_token == data["access_token"]
    assert token.token_type == "bearer"

def test_token_data_valid():
    """Test valid token data"""
    data = {"email": "test@example.com"}
    token_data = TokenData(**data)
    assert token_data.email == "test@example.com"

def test_token_data_empty():
    """Test token data with no email"""
    token_data = TokenData()
    assert token_data.email is None 