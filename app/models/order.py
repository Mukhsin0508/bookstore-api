from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Datetime, Enum as SQLEnum, ForeignKey, Numeric, String

from app.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User



class OrderStatus(str, Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    DELIVERED = 'delivered'


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_card_number: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(Datetime, default=datetime.today())
    updated_at: Mapped[datetime] = mapped_column(
        Datetime, default=datetime.today(), onupdate=datetime.today()
    )

    # === Relationships ===
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="selectin")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # === Relationships ===
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    book: Mapped["Book"] = relationship("Book", back_populates="orders_items", lazy="selectin")






