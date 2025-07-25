from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.api.endpoints import users, auth, devices, bookings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend Application",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(devices.router, prefix=f"{settings.API_V1_STR}/devices", tags=["devices"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_STR}/bookings", tags=["bookings"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Backend Application"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    """
    Test endpoint to verify database connection
    """
    try:
        # Try to make a simple query using text()
        db.execute(text("SELECT 1"))
        db.commit()
        return {"message": "Database connection successful"}
    except Exception as e:
        db.rollback()
        return {"message": f"Database connection failed: {str(e)}"} 