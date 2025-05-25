from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token
from app.database import get_db
from app.schemas import Token, UserCreate, UserLogin, User
from app.services import UserService


router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """Register a new user."""
    # === check if user exists ===
    user = await UserService.get_by_email(db, user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user_create.email} already exists.",
        )

    user = await UserService.get_by_username(db, user_create.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username {user_create.username} already exists.",
        )

    # === Create user ===
    user = await UserService.create(db, user_create)
    return user


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)) -> Any:
    """Log in a user."""
    user = await UserService.authenticate(
        db, user_login.username, user_login.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with username {user.username} has been banned.",
        )

    # === crate access token ===
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject = user.username, expires_delta = access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}













