from app.core.database import engine, Base
from app.models.device import Device  # Import all models here
from app.core.config import settings
import os

def create_tables():
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Ensure the database directory exists
    db_path = os.path.dirname(settings.DATABASE_URL.replace('sqlite:///', ''))
    if db_path and not os.path.exists(db_path):
        os.makedirs(db_path)
    
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Verify the database file exists and has content
        db_file = settings.DATABASE_URL.replace('sqlite:///', '')
        if os.path.exists(db_file):
            print(f"Database file size: {os.path.getsize(db_file)} bytes")
        else:
            print("Warning: Database file was not created!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables() 