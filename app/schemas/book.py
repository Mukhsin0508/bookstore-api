from decimal import Decimal
from typing import Optional, Annotated
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, condecimal


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(0, ge=0)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return round(v, 2)


class BookCreate(BookBase):
    image_url: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Annotated[Decimal, condecimal(gt=0, max_digits=10, decimal_places=2)]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None


class BookInDBBase(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime


class Book(BookInDBBase):
    pass


class BookList(BaseModel):
    books: list[Book]
    total: int
    page: int
    per_page: int
    pages: int