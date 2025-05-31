from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate
from typing import List, Optional

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_device(self, device_id: int) -> Optional[Device]:
        return self.db.query(Device).filter(Device.id == device_id).first()

    def get_all_devices(self) -> List[Device]:
        return self.db.query(Device).all()

    def create_device(self, device: DeviceCreate) -> Device:
        db_device = Device(name=device.name)
        self.db.add(db_device)
        self.db.commit()
        self.db.refresh(db_device)
        return db_device 