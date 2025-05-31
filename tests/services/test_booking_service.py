import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.device import Device

@pytest.fixture
def booking_service(db_session):
    return BookingService(db_session)

@pytest.fixture
def test_device(db_session):
    device = Device(name="Test Device")
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device

@pytest.fixture
def test_booking_data(test_device):
    return {
        "device_id": test_device.id,
        "description": "Test booking",
        "time_slot": datetime.now() + timedelta(days=1),
        "address": "123 Test St"
    }

def test_create_booking_success(booking_service, test_booking_data):
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_service.create_booking(booking_create, user_id=1)
    
    assert booking.id is not None
    assert booking.device_id == test_booking_data["device_id"]
    assert booking.user_id == 1
    assert booking.description == test_booking_data["description"]
    assert booking.time_slot == test_booking_data["time_slot"]
    assert booking.address == test_booking_data["address"]

def test_create_booking_device_not_found(booking_service, test_booking_data):
    # Try to create booking with non-existent device
    booking_create = BookingCreate(**{**test_booking_data, "device_id": 999})
    with pytest.raises(ValueError) as exc_info:
        booking_service.create_booking(booking_create, user_id=1)
    assert "Device not found" in str(exc_info.value)

def test_create_booking_time_slot_conflict(booking_service, test_booking_data):
    # Create first booking
    booking_create = BookingCreate(**test_booking_data)
    booking_service.create_booking(booking_create, user_id=1)
    
    # Try to create another booking for same time slot
    with pytest.raises(ValueError) as exc_info:
        booking_service.create_booking(booking_create, user_id=2)
    assert "time slot is already booked" in str(exc_info.value)

def test_get_booking_success(booking_service, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    created_booking = booking_service.create_booking(booking_create, user_id=1)
    
    # Get the booking
    retrieved_booking = booking_service.get_booking(created_booking.id)
    assert retrieved_booking is not None
    assert retrieved_booking.id == created_booking.id
    assert retrieved_booking.device_id == test_booking_data["device_id"]

def test_get_booking_not_found(booking_service):
    assert booking_service.get_booking(999) is None

def test_get_user_bookings(booking_service, test_booking_data):
    # Create bookings for different users with different time slots
    booking_create1 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"]})
    booking_create2 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=1)})
    booking_create3 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=2)})
    
    booking_service.create_booking(booking_create1, user_id=1)
    booking_service.create_booking(booking_create2, user_id=1)
    booking_service.create_booking(booking_create3, user_id=2)  # Using a different time slot for user 2
    
    # Get bookings for user 1
    user_bookings = booking_service.get_user_bookings(user_id=1)
    assert len(user_bookings) == 2
    assert all(booking.user_id == 1 for booking in user_bookings)
    
    # Get bookings for user 2
    user2_bookings = booking_service.get_user_bookings(user_id=2)
    assert len(user2_bookings) == 1
    assert all(booking.user_id == 2 for booking in user2_bookings)

def test_get_device_bookings(booking_service, test_booking_data):
    # Create bookings for different devices with different time slots
    booking_create1 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"]})
    booking_create2 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=1)})
    booking_service.create_booking(booking_create1, user_id=1)
    booking_service.create_booking(booking_create2, user_id=2)
    
    # Get bookings for device
    device_bookings = booking_service.get_device_bookings(test_booking_data["device_id"])
    assert len(device_bookings) == 2
    assert all(booking.device_id == test_booking_data["device_id"] for booking in device_bookings)

def test_update_booking_success(booking_service, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_service.create_booking(booking_create, user_id=1)
    
    # Update the booking
    update_data = BookingUpdate(description="Updated description")
    updated_booking = booking_service.update_booking(booking.id, update_data, user_id=1)
    
    assert updated_booking is not None
    assert updated_booking.description == "Updated description"
    assert updated_booking.device_id == test_booking_data["device_id"]  # unchanged

def test_update_booking_not_found(booking_service):
    update_data = BookingUpdate(description="Updated description")
    assert booking_service.update_booking(999, update_data, user_id=1) is None

def test_update_booking_unauthorized(booking_service, test_booking_data):
    # Create a booking for user 1
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_service.create_booking(booking_create, user_id=1)
    
    # Try to update as user 2
    update_data = BookingUpdate(description="Updated description")
    with pytest.raises(ValueError) as exc_info:
        booking_service.update_booking(booking.id, update_data, user_id=2)
    assert "Not authorized" in str(exc_info.value)

def test_update_booking_time_slot_conflict(booking_service, test_booking_data):
    # Create two bookings
    booking_create = BookingCreate(**test_booking_data)
    booking1 = booking_service.create_booking(booking_create, user_id=1)
    
    # Create second booking with different time slot
    other_time = test_booking_data["time_slot"] + timedelta(hours=1)
    booking2 = booking_service.create_booking(
        BookingCreate(**{**test_booking_data, "time_slot": other_time}),
        user_id=2
    )
    
    # Try to update first booking to conflict with second
    update_data = BookingUpdate(time_slot=other_time)
    with pytest.raises(ValueError) as exc_info:
        booking_service.update_booking(booking1.id, update_data, user_id=1)
    assert "time slot is already booked" in str(exc_info.value)

def test_delete_booking_success(booking_service, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_service.create_booking(booking_create, user_id=1)
    
    # Delete the booking
    assert booking_service.delete_booking(booking.id, user_id=1) is True
    assert booking_service.get_booking(booking.id) is None

def test_delete_booking_not_found(booking_service):
    assert booking_service.delete_booking(999, user_id=1) is False

def test_delete_booking_unauthorized(booking_service, test_booking_data):
    # Create a booking for user 1
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_service.create_booking(booking_create, user_id=1)
    
    # Try to delete as user 2
    with pytest.raises(ValueError) as exc_info:
        booking_service.delete_booking(booking.id, user_id=2)
    assert "Not authorized" in str(exc_info.value) 