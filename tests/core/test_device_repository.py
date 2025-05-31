import pytest
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate

def test_create_and_get_all_devices(db_session):
    repo = DeviceRepository(db_session)
    # Initially empty
    assert repo.get_all_devices() == []

    # Add a device
    device_data = DeviceCreate(name="Test Device")
    device = repo.create_device(device_data)
    assert device.id is not None
    assert device.name == "Test Device"

    # Add another device
    device2 = repo.create_device(DeviceCreate(name="Another Device"))
    # List all
    devices = repo.get_all_devices()
    assert len(devices) == 2
    names = {d.name for d in devices}
    assert names == {"Test Device", "Another Device"} 