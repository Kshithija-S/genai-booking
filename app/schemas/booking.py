from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class BookingBase(BaseModel):
    device_id: int
    description: str = Field(..., min_length=1)
    time_slot: datetime
    address: str = Field(..., min_length=1)

    @field_validator('time_slot')
    def validate_time_slot(cls, v):
        if v < datetime.now():
            raise ValueError("Cannot book a time slot in the past")
        return v

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    time_slot: Optional[datetime] = None
    address: Optional[str] = Field(None, min_length=1)

    @field_validator('time_slot')
    def validate_time_slot(cls, v):
        if v is not None and v < datetime.now():
            raise ValueError("Cannot book a time slot in the past")
        return v

class BookingResponse(BookingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 