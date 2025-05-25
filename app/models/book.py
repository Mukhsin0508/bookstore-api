from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.today(), onupdate=datetime.today()
    )

    # === Relationships ===
    order_items = Mapped[List["OrderItems"]] = relationship(
        "OrderItems", back_populates="book", lazy="selectin"
    )

