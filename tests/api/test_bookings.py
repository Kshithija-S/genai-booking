import pytest
from datetime import datetime, timedelta
from fastapi import status
from app.core.security import get_password_hash
from app.models.user import User
from app.models.device import Device

@pytest.fixture
def test_device(db_session):
    device = Device(name="Test Device")
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device

@pytest.fixture
def test_user(db_session, test_user_data):
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

@pytest.fixture
def test_booking_data(test_device):
    return {
        "device_id": test_device.id,
        "description": "Test booking",
        "time_slot": (datetime.now() + timedelta(days=1)).isoformat(),
        "address": "123 Test St"
    }

@pytest.fixture
def auth_headers(client, test_user_data):
    # Register user first
    client.post(
        "/api/v1/users/register",
        json=test_user_data
    )
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_booking_success(client, auth_headers, test_booking_data):
    response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["device_id"] == test_booking_data["device_id"]
    assert data["description"] == test_booking_data["description"]
    assert data["address"] == test_booking_data["address"]
    assert "user_id" in data

def test_create_booking_unauthorized(client, test_booking_data):
    response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_booking_device_not_found(client, auth_headers, test_booking_data):
    response = client.post(
        "/api/v1/bookings/",
        json={**test_booking_data, "device_id": 999},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Device not found" in response.json()["detail"]

def test_create_booking_time_slot_conflict(client, auth_headers, test_booking_data):
    # Create first booking
    client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    
    # Try to create another booking for same time slot
    response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "time slot is already booked" in response.json()["detail"]

def test_get_booking_success(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Get the booking
    response = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == booking_id
    assert data["device_id"] == test_booking_data["device_id"]

def test_get_booking_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/bookings/999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_booking_unauthorized(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Create another user and get their token
    other_user = {
        "email": "other@example.com",
        "password": "testpass123",
        "name": "Other User",
        "address": "456 Other St"
    }
    client.post("/api/v1/users/register", json=other_user)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": other_user["email"], "password": other_user["password"]}
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to get booking as other user
    response = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=other_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_user_bookings(client, auth_headers, test_booking_data):
    # Create multiple bookings with different time slots
    first_booking = {**test_booking_data, "time_slot": (datetime.now() + timedelta(days=1)).isoformat()}
    second_booking = {**test_booking_data, "time_slot": (datetime.now() + timedelta(days=1, hours=1)).isoformat()}
    
    client.post(
        "/api/v1/bookings/",
        json=first_booking,
        headers=auth_headers
    )
    client.post(
        "/api/v1/bookings/",
        json=second_booking,
        headers=auth_headers
    )
    
    # Get user's bookings
    response = client.get(
        "/api/v1/bookings/user/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(booking["device_id"] == test_booking_data["device_id"] for booking in data)

def test_get_device_bookings(client, auth_headers, test_booking_data):
    # Create multiple bookings for the device with different time slots
    first_booking = {**test_booking_data, "time_slot": (datetime.now() + timedelta(days=1)).isoformat()}
    second_booking = {**test_booking_data, "time_slot": (datetime.now() + timedelta(days=1, hours=1)).isoformat()}
    
    client.post(
        "/api/v1/bookings/",
        json=first_booking,
        headers=auth_headers
    )
    client.post(
        "/api/v1/bookings/",
        json=second_booking,
        headers=auth_headers
    )
    
    # Get device's bookings
    response = client.get(
        f"/api/v1/bookings/device/{test_booking_data['device_id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(booking["device_id"] == test_booking_data["device_id"] for booking in data)

def test_update_booking_success(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Update the booking
    update_data = {"description": "Updated description"}
    response = client.patch(
        f"/api/v1/bookings/{booking_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["device_id"] == test_booking_data["device_id"]  # unchanged

def test_update_booking_not_found(client, auth_headers):
    response = client.patch(
        "/api/v1/bookings/999",
        json={"description": "Updated description"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_booking_unauthorized(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Create another user and get their token
    other_user = {
        "email": "other@example.com",
        "password": "testpass123",
        "name": "Other User",
        "address": "456 Other St"
    }
    client.post("/api/v1/users/register", json=other_user)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": other_user["email"], "password": other_user["password"]}
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to update booking as other user
    response = client.patch(
        f"/api/v1/bookings/{booking_id}",
        json={"description": "Updated description"},
        headers=other_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not authorized" in response.json()["detail"]

def test_update_booking_time_slot_conflict(client, auth_headers, test_booking_data):
    # Create two bookings
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Create second booking with different time slot
    other_time = (datetime.now() + timedelta(days=2)).isoformat()
    client.post(
        "/api/v1/bookings/",
        json={**test_booking_data, "time_slot": other_time},
        headers=auth_headers
    )
    
    # Try to update first booking to conflict with second
    response = client.patch(
        f"/api/v1/bookings/{booking_id}",
        json={"time_slot": other_time},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "time slot is already booked" in response.json()["detail"]

def test_delete_booking_success(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Delete the booking
    response = client.delete(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify booking is deleted
    get_response = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_booking_not_found(client, auth_headers):
    response = client.delete(
        "/api/v1/bookings/999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_booking_unauthorized(client, auth_headers, test_booking_data):
    # Create a booking
    create_response = client.post(
        "/api/v1/bookings/",
        json=test_booking_data,
        headers=auth_headers
    )
    booking_id = create_response.json()["id"]
    
    # Create another user and get their token
    other_user = {
        "email": "other@example.com",
        "password": "testpass123",
        "name": "Other User",
        "address": "456 Other St"
    }
    client.post("/api/v1/users/register", json=other_user)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": other_user["email"], "password": other_user["password"]}
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to delete booking as other user
    response = client.delete(
        f"/api/v1/bookings/{booking_id}",
        headers=other_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not authorized" in response.json()["detail"] 