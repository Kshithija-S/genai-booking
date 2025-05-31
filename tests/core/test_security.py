import pytest
from datetime import datetime, timedelta, UTC
from jose import jwt
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash
)
from app.core.config import settings

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    
    # Verify the password matches
    assert verify_password(password, hashed_password)
    # Verify wrong password doesn't match
    assert not verify_password("wrongpassword", hashed_password)

def test_create_access_token():
    """Test JWT token creation"""
    email = "test@example.com"
    token = create_access_token(email)
    
    # Decode the token
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    
    # Verify token contents
    assert decoded["sub"] == email
    assert "exp" in decoded

def test_create_access_token_with_expires_delta():
    """Test JWT token creation with custom expiration"""
    email = "test@example.com"
    expires_delta = timedelta(minutes=15)
    
    # Record the time before token creation and normalize microseconds
    before_token = datetime.now(UTC).replace(microsecond=0)
    token = create_access_token(email, expires_delta=expires_delta)
    after_token = datetime.now(UTC).replace(microsecond=0)
    
    # Decode the token
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    
    # Get the expiration time from the token
    token_exp = datetime.fromtimestamp(decoded["exp"], UTC)
    
    # Calculate the expected expiration time range
    min_expected_exp = before_token + expires_delta
    max_expected_exp = after_token + expires_delta
    
    # Verify the token expiration is within the expected range
    assert min_expected_exp <= token_exp <= max_expected_exp 