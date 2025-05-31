import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.booking import Booking

@pytest.fixture
def booking_repo(db_session):
    return BookingRepository(db_session)

@pytest.fixture
def test_booking_data():
    return {
        "device_id": 1,
        "description": "Test booking",
        "time_slot": datetime.now() + timedelta(days=1),
        "address": "123 Test St"
    }

def test_create_booking(booking_repo, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_repo.create_booking(booking_create, user_id=1)
    
    assert booking.id is not None
    assert booking.device_id == test_booking_data["device_id"]
    assert booking.user_id == 1
    assert booking.description == test_booking_data["description"]
    assert booking.time_slot == test_booking_data["time_slot"]
    assert booking.address == test_booking_data["address"]

def test_create_booking_time_slot_conflict(booking_repo, test_booking_data):
    # Create first booking
    booking_create = BookingCreate(**test_booking_data)
    booking_repo.create_booking(booking_create, user_id=1)
    
    # Try to create another booking for same time slot
    with pytest.raises(ValueError) as exc_info:
        booking_repo.create_booking(booking_create, user_id=2)
    assert "time slot is already booked" in str(exc_info.value)

def test_get_booking(booking_repo, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    created_booking = booking_repo.create_booking(booking_create, user_id=1)
    
    # Get the booking
    retrieved_booking = booking_repo.get_booking(created_booking.id)
    assert retrieved_booking is not None
    assert retrieved_booking.id == created_booking.id
    assert retrieved_booking.device_id == test_booking_data["device_id"]
    
    # Try to get non-existent booking
    assert booking_repo.get_booking(999) is None

def test_get_user_bookings(booking_repo, test_booking_data):
    # Create bookings for different users with different time slots
    booking_create1 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"]})
    booking_create2 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=1)})
    booking_create3 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=2)})
    
    booking_repo.create_booking(booking_create1, user_id=1)
    booking_repo.create_booking(booking_create2, user_id=1)
    booking_repo.create_booking(booking_create3, user_id=2)  # Using a different time slot for user 2
    
    # Get bookings for user 1
    user_bookings = booking_repo.get_user_bookings(user_id=1)
    assert len(user_bookings) == 2
    assert all(booking.user_id == 1 for booking in user_bookings)
    
    # Get bookings for user 2
    user2_bookings = booking_repo.get_user_bookings(user_id=2)
    assert len(user2_bookings) == 1
    assert all(booking.user_id == 2 for booking in user2_bookings)

def test_get_device_bookings(booking_repo, test_booking_data):
    # Create bookings for different devices with different time slots
    booking_create1 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"]})
    booking_create2 = BookingCreate(**{**test_booking_data, "time_slot": test_booking_data["time_slot"] + timedelta(hours=1)})
    booking_repo.create_booking(booking_create1, user_id=1)
    booking_repo.create_booking(booking_create2, user_id=2)
    
    # Create booking for different device
    other_booking = BookingCreate(**{**test_booking_data, "device_id": 2, "time_slot": test_booking_data["time_slot"] + timedelta(hours=2)})
    booking_repo.create_booking(other_booking, user_id=1)
    
    # Get bookings for device 1
    device_bookings = booking_repo.get_device_bookings(device_id=1)
    assert len(device_bookings) == 2
    assert all(booking.device_id == 1 for booking in device_bookings)

def test_update_booking(booking_repo, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_repo.create_booking(booking_create, user_id=1)
    
    # Update the booking
    update_data = BookingUpdate(description="Updated description")
    updated_booking = booking_repo.update_booking(booking.id, update_data)
    
    assert updated_booking is not None
    assert updated_booking.description == "Updated description"
    assert updated_booking.device_id == test_booking_data["device_id"]  # unchanged
    
    # Try to update non-existent booking
    assert booking_repo.update_booking(999, update_data) is None

def test_update_booking_time_slot_conflict(booking_repo, test_booking_data):
    # Create two bookings
    booking_create = BookingCreate(**test_booking_data)
    booking1 = booking_repo.create_booking(booking_create, user_id=1)
    
    # Create second booking with different time slot
    other_time = test_booking_data["time_slot"] + timedelta(hours=1)
    booking2 = booking_repo.create_booking(
        BookingCreate(**{**test_booking_data, "time_slot": other_time}),
        user_id=2
    )
    
    # Try to update first booking to conflict with second
    update_data = BookingUpdate(time_slot=other_time)
    with pytest.raises(ValueError) as exc_info:
        booking_repo.update_booking(booking1.id, update_data)
    assert "time slot is already booked" in str(exc_info.value)

def test_delete_booking(booking_repo, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking = booking_repo.create_booking(booking_create, user_id=1)
    
    # Delete the booking
    assert booking_repo.delete_booking(booking.id) is True
    assert booking_repo.get_booking(booking.id) is None
    
    # Try to delete non-existent booking
    assert booking_repo.delete_booking(999) is False

def test_check_time_slot_availability(booking_repo, test_booking_data):
    # Create a booking
    booking_create = BookingCreate(**test_booking_data)
    booking_repo.create_booking(booking_create, user_id=1)
    
    # Check same time slot
    assert not booking_repo.check_time_slot_availability(
        test_booking_data["device_id"],
        test_booking_data["time_slot"]
    )
    
    # Check different time slot
    other_time = test_booking_data["time_slot"] + timedelta(hours=1)
    assert booking_repo.check_time_slot_availability(
        test_booking_data["device_id"],
        other_time
    ) 