from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.database import get_db
from app.services import UserService
from app.api.deps import get_current_active_user
from app.schemas import User as UserSchema, UserUpdate


router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user info"""
    return current_user


@router.get("/me", response_model=UserSchema)
async def update_user_me(
    db: AsyncSession,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)) ->  Any:
    """Update current user info"""
    # === Check if email is taken ===
    if user_update.email:
        existing_user = await UserService.get_by_email(db=db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {user_update.email} is already taken!",
            )

    # === Check if username is taken ===
    if user_update.username:
        existing_user =  await UserService.get_by_username(db=db, username=user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username {user_update.username} is already taken!",
            )

    user = await UserService.update(db=db, user=current_user, user_update=user_update)
    return user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)) -> Any:
    """Get user by ID"""
    user = await UserService.get(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found!",
        )
    return user

