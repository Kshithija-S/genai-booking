from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.repositories.device_repository import DeviceRepository

class BookingService:
    def __init__(self, db: Session):
        self.booking_repository = BookingRepository(db)
        self.device_repository = DeviceRepository(db)

    def create_booking(self, booking: BookingCreate, user_id: int) -> BookingResponse:
        # Verify device exists
        device = self.device_repository.get_device(booking.device_id)
        if not device:
            raise ValueError("Device not found")

        # Check time slot availability
        if not self.booking_repository.check_time_slot_availability(booking.device_id, booking.time_slot):
            raise ValueError("This time slot is already booked for the selected device")

        db_booking = self.booking_repository.create_booking(booking, user_id)
        return BookingResponse.model_validate(db_booking)

    def get_booking(self, booking_id: int) -> Optional[BookingResponse]:
        db_booking = self.booking_repository.get_booking(booking_id)
        if not db_booking:
            return None
        return BookingResponse.model_validate(db_booking)

    def get_user_bookings(self, user_id: int) -> List[BookingResponse]:
        bookings = self.booking_repository.get_user_bookings(user_id)
        return [BookingResponse.model_validate(booking) for booking in bookings]

    def get_device_bookings(self, device_id: int) -> List[BookingResponse]:
        bookings = self.booking_repository.get_device_bookings(device_id)
        return [BookingResponse.model_validate(booking) for booking in bookings]

    def update_booking(self, booking_id: int, booking_update: BookingUpdate, user_id: int) -> Optional[BookingResponse]:
        # Verify booking exists and belongs to user
        db_booking = self.booking_repository.get_booking(booking_id)
        if not db_booking:
            return None
        if db_booking.user_id != user_id:
            raise ValueError("Not authorized to update this booking")

        updated_booking = self.booking_repository.update_booking(booking_id, booking_update)
        if not updated_booking:
            return None
        return BookingResponse.model_validate(updated_booking)

    def delete_booking(self, booking_id: int, user_id: int) -> bool:
        # Verify booking exists and belongs to user
        db_booking = self.booking_repository.get_booking(booking_id)
        if not db_booking:
            return False
        if db_booking.user_id != user_id:
            raise ValueError("Not authorized to delete this booking")

        return self.booking_repository.delete_booking(booking_id) 