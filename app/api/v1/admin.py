from typing import Any, Dict, List, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_db
from app.schemas import OrderList, User
from app.models import User as UserModel
from app.services import OrderService, UserService
from app.api.deps import get_current_active_superuser

router = APIRouter()


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)) -> Dict[str, Any]:
    """Get admin statistics"""
    # === Get order stats ===
    order_stats = await OrderService.get_statistics(db=db)

    # === Get user stats ===
    total_users_result = await db.execute(
        select(func.count(UserModel.id))
    )
    total_users = total_users_result.scalar_one()

    active_users_result = await db.execute(
        select(func.count(UserModel.id)).where(UserModel.is_active == True)
    )
    active_users = active_users_result.scalar_one()

    banned_users_result = await db.execute(
        select(func.count(UserModel.id)).where(func.count(UserModel.is_banned == True))
    )
    banned_users = banned_users_result.scalar_one()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "banned": banned_users,
        },
        "orders": order_stats
    }


@router.get("/users", response_model=List[User])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Sequence[User]:
    """Get all users (admin only)"""
    result = await db.execute(
        select(UserModel).offset(skip).limit(limit).order_by(UserModel.created_at.desc())
    )
    users = result.scalars().all()
    return users


@router.post("/users/{user_id}/ban", response_model=User)
async def admin_ban_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser), # TODO: why are we not checking superuser or using
    # this current user even?
) -> Any:
    """Band user (admin only)"""
    user = await UserService.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot band superusers",
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already banned",
        )

    user = await UserService.ban(db, user)
    return user

@router.post("/users/{user_id}/unban", response_model=User)
async def admin_unban_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Unban user (admin only)"""
    user = await UserService.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not banned",
        )
    user = await UserService.ban(db, user)
    return user


@router.post("/orders", response_model=OrderList)
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """Get all orders"""
    orders = await OrderService.get_all_orders(db=db, skip=skip, limit=limit)
    total = await OrderService.get_total_count(db)

    return {
        "orders": orders,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "pages": (total + limit - 1) // limit,
    }



