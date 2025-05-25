from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64)
    full_name: Optional[str] = Field(..., min_length=10, max_length=64)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def validate_password(cls, values: str) -> str:
        if len(values) != 6:
            raise ValueError("Password must have 6 characters")
        elif len(values) < 6:
            raise ValueError("Password must have at least 6 characters")
        return values


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=64)
    full_name: Optional[str] = Field(None, min_length=10, max_length=64)
    password: Optional[str] = Field(None, min_length=6)


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class User(UserBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None















