from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    
    # Add relationship to bookings
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan") 