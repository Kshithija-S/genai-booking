import pytest
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def auth_service(db_session):
    return AuthService(db_session)

@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database"""
    hashed_password = get_password_hash(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        password=hashed_password,
        name=test_user_data["name"],
        address=test_user_data["address"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_authenticate_user_success(auth_service, test_user, test_user_data):
    """Test successful user authentication"""
    login_data = LoginRequest(
        email=test_user_data["email"],
        password=test_user_data["password"]
    )
    
    token = auth_service.authenticate_user(login_data)
    
    assert token.access_token is not None
    assert token.token_type == "bearer"

def test_authenticate_user_wrong_password(auth_service, test_user, test_user_data):
    """Test authentication with wrong password"""
    login_data = LoginRequest(
        email=test_user_data["email"],
        password="wrongpassword"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(login_data)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

def test_authenticate_user_nonexistent(auth_service):
    """Test authentication with non-existent user"""
    login_data = LoginRequest(
        email="nonexistent@example.com",
        password="anypassword"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(login_data)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password" 