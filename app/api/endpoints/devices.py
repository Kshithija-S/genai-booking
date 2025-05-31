from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.services.device_service import DeviceService
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.database import get_db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    """
    List all devices
    """
    device_service = DeviceService(db)
    return device_service.get_all_devices()

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device
    """
    device_service = DeviceService(db)
    return device_service.create_device(device) 