from sqlalchemy.orm import Session
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse
from typing import List

class DeviceService:
    def __init__(self, db: Session):
        self.device_repository = DeviceRepository(db)

    def get_all_devices(self) -> List[DeviceResponse]:
        """
        Get all devices
        """
        devices = self.device_repository.get_all_devices()
        return [DeviceResponse(id=device.id, name=device.name) for device in devices]

    def create_device(self, device_data: DeviceCreate) -> DeviceResponse:
        """
        Create a new device
        """
        db_device = self.device_repository.create_device(device_data)
        return DeviceResponse(id=db_device.id, name=db_device.name) 