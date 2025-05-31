import pytest
from fastapi import status
from app.core.security import get_password_hash
from app.models.user import User

def test_login_success(client, db_session, test_user_data):
    """Test successful login endpoint"""
    # Create a user first
    hashed_password = get_password_hash(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        password=hashed_password,
        name=test_user_data["name"],
        address=test_user_data["address"]
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db_session, test_user_data):
    """Test login with wrong password"""
    # Create a user first
    hashed_password = get_password_hash(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        password=hashed_password,
        name=test_user_data["name"],
        address=test_user_data["address"]
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_invalid_email_format(client):
    """Test login with invalid email format"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid-email",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 