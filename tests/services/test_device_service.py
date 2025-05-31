import pytest
from app.services.device_service import DeviceService
from app.schemas.device import DeviceCreate

def test_create_and_get_all_devices(db_session):
    service = DeviceService(db_session)
    # Initially empty
    assert service.get_all_devices() == []

    # Add a device
    device_resp = service.create_device(DeviceCreate(name="Service Device"))
    assert device_resp.id is not None
    assert device_resp.name == "Service Device"

    # Add another device
    device_resp2 = service.create_device(DeviceCreate(name="Service Device 2"))
    # List all
    devices = service.get_all_devices()
    assert len(devices) == 2
    names = {d.name for d in devices}
    assert names == {"Service Device", "Service Device 2"} 