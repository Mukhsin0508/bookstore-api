from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.core import get_password_hash, verify_password


class UserService:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: EmailStr) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by id"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_create.password)

        user = User(
            email = user_create.email,
            username = user_create.username,
            full_name = user_create.full_name,
            hashed_password = hashed_password,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
        """Update user"""
        update_data = user_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def ban(db: AsyncSession, user: User) -> Optional[User]:
        """Ban user"""
        user.is_banned = True # TODO: In future, add ban_counts, and implement incremental logic
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def unban(db: AsyncSession, user: User) -> Optional[User]:
        """Unban user"""
        user.is_banned = False
        await db.commit()
        await db.refresh(user)
        return user










