from pydantic import BaseModel, Field

class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1)

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int

    class Config:
        from_attributes = True 