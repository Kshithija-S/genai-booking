import pytest

def test_list_devices_empty(client):
    response = client.get("/api/v1/devices/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_list_devices(client):
    # Create a device
    resp = client.post("/api/v1/devices/", json={"name": "API Device"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["name"] == "API Device"

    # Create another device
    resp2 = client.post("/api/v1/devices/", json={"name": "API Device 2"})
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["name"] == "API Device 2"

    # List all
    list_resp = client.get("/api/v1/devices/")
    assert list_resp.status_code == 200
    names = {d["name"] for d in list_resp.json()}
    assert names == {"API Device", "API Device 2"} 