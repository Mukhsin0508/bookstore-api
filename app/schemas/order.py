from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    OrderStatus,
    Book,
    User
)


class OrderItemBase(BaseModel):
    book_id: int
    quantity: int = Field(1, gt=0)


class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    price: Decimal
    book: Book


class OrderBase(BaseModel):
    items: List[OrderItemCreate]


class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    payment_card_number: Optional[str]

    items: List[OrderItem]
    user: User

    created_at: datetime
    updated_at: datetime


class OrderList(BaseModel):
    orders: List[Order]
    total: int
    page: int
    per_page: int
    pages: int
















