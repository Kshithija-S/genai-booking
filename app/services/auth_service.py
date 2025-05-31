from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.services.user_service import UserService
from app.schemas.auth import LoginRequest, Token
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.user_service = UserService(db)

    def authenticate_user(self, login_data: LoginRequest) -> Token:
        """
        Authenticate a user and return a JWT token
        """
        user = self.user_service.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer") 