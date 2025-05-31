from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user with validation and business logic
        """
        # Check if user already exists
        existing_user = self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Additional business logic can be added here
        # For example:
        # - Validate password strength
        # - Check if email domain is allowed
        # - Apply any business rules for user creation
        
        # Create user in database
        db_user = self.user_repository.create_user(user_data)
        
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            address=db_user.address
        )

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email
        """
        return self.user_repository.get_user_by_email(email) 