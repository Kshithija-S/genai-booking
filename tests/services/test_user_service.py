import pytest
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import User

def test_register_user_success(db_session, test_user_data):
    user_service = UserService(db_session)
    user_create = UserCreate(**test_user_data)
    
    user = user_service.register_user(user_create)
    
    assert user.email == test_user_data["email"]
    assert user.name == test_user_data["name"]
    assert user.address == test_user_data["address"]
    assert user.id is not None
    # Verify user was actually created in database
    db_user = db_session.query(User).filter_by(email=test_user_data["email"]).first()
    assert db_user is not None
    assert db_user.email == test_user_data["email"]

def test_register_user_duplicate_email(db_session, test_user_data):
    user_service = UserService(db_session)
    user_create = UserCreate(**test_user_data)
    
    # First registration
    user_service.register_user(user_create)
    
    # Try to register with same email
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_create)
    assert exc_info.value.status_code == 400
    assert "email already registered" in str(exc_info.value.detail).lower()

def test_register_user_password_hashing(db_session, test_user_data):
    user_service = UserService(db_session)
    user_create = UserCreate(**test_user_data)
    
    user = user_service.register_user(user_create)
    
    # Verify password was hashed
    db_user = db_session.query(User).filter_by(email=test_user_data["email"]).first()
    assert db_user.password != test_user_data["password"]
    assert db_user.password.startswith("$2b$")  # bcrypt hash format

def test_register_user_database_error(db_session, test_user_data, monkeypatch):
    user_service = UserService(db_session)
    user_create = UserCreate(**test_user_data)
    
    # Mock database session to raise IntegrityError
    def mock_commit():
        raise IntegrityError(None, None, None)
    
    monkeypatch.setattr(db_session, "commit", mock_commit)
    
    with pytest.raises(Exception):
        user_service.register_user(user_create)
    
    # Verify rollback was called 