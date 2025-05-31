from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Add relationship to bookings
    bookings = relationship("Booking", back_populates="device", cascade="all, delete-orphan") 