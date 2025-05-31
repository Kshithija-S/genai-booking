from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.device import Device

def seed_devices():
    devices = [
        {"name": "MacBook Pro 16-inch"},
        {"name": "iPhone 15 Pro"},
        {"name": "Samsung Galaxy S24"},
        {"name": "Dell XPS 15"},
        {"name": "iPad Pro"},
        {"name": "Google Pixel 8"},
        {"name": "HP Spectre x360"},
        {"name": "Sony WH-1000XM5"},
        {"name": "Apple Watch Series 9"},
        {"name": "Microsoft Surface Laptop 5"}
    ]

    db = SessionLocal()
    try:
        # Clear existing devices
        db.query(Device).delete()
        db.commit()
        print("Cleared existing devices.")

        # Add devices
        for device_data in devices:
            device = Device(**device_data)
            db.add(device)
        
        db.commit()
        print("Successfully seeded devices!")
    except Exception as e:
        print(f"Error seeding devices: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_devices() 