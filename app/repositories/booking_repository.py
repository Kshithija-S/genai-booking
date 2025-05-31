from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate, user_id: int) -> Booking:
        db_booking = Booking(
            device_id=booking.device_id,
            user_id=user_id,
            description=booking.description,
            time_slot=booking.time_slot,
            address=booking.address
        )
        try:
            self.db.add(db_booking)
            self.db.commit()
            self.db.refresh(db_booking)
            return db_booking
        except IntegrityError:
            self.db.rollback()
            raise ValueError("This time slot is already booked for the selected device")

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def get_user_bookings(self, user_id: int) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_device_bookings(self, device_id: int) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.device_id == device_id).all()

    def update_booking(self, booking_id: int, booking_update: BookingUpdate) -> Optional[Booking]:
        db_booking = self.get_booking(booking_id)
        if not db_booking:
            return None

        update_data = booking_update.model_dump(exclude_unset=True)
        
        # Check for time slot conflicts if updating time slot
        if 'time_slot' in update_data:
            existing_booking = self.db.query(Booking).filter(
                Booking.device_id == db_booking.device_id,
                Booking.time_slot == update_data['time_slot'],
                Booking.id != booking_id
            ).first()
            if existing_booking:
                raise ValueError("This time slot is already booked for the selected device")

        for key, value in update_data.items():
            setattr(db_booking, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_booking)
            return db_booking
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to update booking")

    def delete_booking(self, booking_id: int) -> bool:
        db_booking = self.get_booking(booking_id)
        if not db_booking:
            return False
        
        self.db.delete(db_booking)
        self.db.commit()
        return True

    def check_time_slot_availability(self, device_id: int, time_slot: datetime) -> bool:
        existing_booking = self.db.query(Booking).filter(
            Booking.device_id == device_id,
            Booking.time_slot == time_slot
        ).first()
        return existing_booking is None 