from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import Order

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_counts: Mapped[int] = mapped_column(String(255), nullable=False, default=0, help_text="Number of times user "
                                                                                               "got banned by other "
                                                                                              "users. Exceeds 3 times -> is_banned set to True")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.today(), onupdate=datetime.today())

    # === Relationships ===
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", lazy="selectin")


