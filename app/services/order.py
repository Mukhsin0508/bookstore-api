from decimal import Decimal
from statistics import quantiles
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas import OrderCreate
from app.services import BookService
from app.models import User, Order, OrderItem, OrderStatus


class OrderService:
    @staticmethod
    async def get(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get order by ID with all relationships"""
        result = await db.execute(
            select(Order).where(Order.id == order_id).options(
                selectinload(Order.items).selectinload(OrderItem.book),
                selectinload(Order.user)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_orders(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders for a specific user"""
        result = await db.execute(
            select(Order).where(User.id == user_id).options(
                selectinload(Order.items).selectinload(OrderItem.book),
                selectinload(Order.user)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        return List(result.scalars().all())

    @staticmethod
    async def get_all_orders(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders (admin only)"""
        result = await db.execute(
            select(Order).options(
                selectinload(Order.items).selectinload(OrderItem.book),
                selectinload(Order.user)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_total_count(db: AsyncSession, user_id: Optional[int] = None) -> int:
        """Get a total count of orders"""
        query = select(func.count(Order.id))
        if user_id:
            query = query.where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def create(db: AsyncSession, user: User, order_create: OrderCreate) -> Optional[Order]:
        """Create a new order"""
        # === Calculate total amount and check stock first ===
        total_amount = Decimal("0.00")
        order_items = []

        for item in order_create.items:
            # == get book and check stock ===
            book = await BookService.get(db, item.book_id)
            if not book:
                return None

            if not await BookService.check_stock(db, item.book_id, item.quantity):
                return None

            # === Calculate item total ===
            item_total = book.price * item.quantity
            total_amount += item_total

            # === Create order item ===
            order_item = OrderItem(
                book_id=item.book_id,
                quantity=item.quantity,
                price=book.price,
            )
            order_items.append(order_item)

        # === Create an order ===
        order = Order(
            user_id=user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            items=order_items
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        # === Load relationships ===
        result = await db.execute(
            select(Order).where(Order.id == order.id).options(
                selectinload(Order.items).selectinload(OrderItem.book),
                selectinload(Order.user)
            )
        )
        return result.scalar_one()

    @staticmethod
    async def update_status(
        db: AsyncSession,
        order: Order,
        status: OrderStatus,
        card_number: Optional[str] = None
    ) -> Optional[Order]:
        """Update status of an order"""
        order.status = status
        if card_number:
            #  ==== Mask card number for security ===
            order.payment_card_number = f"****{card_number[-4:]}"

        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def process_payment_success(db: AsyncSession, order: Order, card_number: str) -> Order:
        """Process success payment for an order"""
        # === update order status ==
        order = await OrderService.update_status(
            db, order, OrderStatus.PAID, card_number
        )

        # === Update book stock ===
        for item in order.items:
            await BookService.update_stock(db, item.book_id, -item.quantity)

        return order

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """Get statistics for admin only"""
        # === Total Orders ==
        total_orders_result = await db.execute(select(func.count(Order.id)))
        total_orders = total_orders_result.scalar_one()

        # === Total revenue ===
        total_revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(Order.status == OrderStatus.PAID)
        )
        total_revenue = total_revenue_result.scalar_one() or Decimal("0.00")

        # === Order by status ===
        status_counts_result = await db.execute(
            select(Order.status, func.count(Order.id)).group_by(Order.status)
        )
        status_counts = {
            status: count for status, count in status_counts_result
        }

        # === Top Selling Books ===
        top_books_result = await db.execute(
            select(
                OrderItem.book_id,
                func.sum(OrderItem.quantity).label("total_quantity")
            )
            .join(Order)
            .where(Order.status == OrderStatus.PAID)
            .group_by(OrderItem.book_id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(5)
        )
        top_books = [
            {"book_id": book_id, "total_sold": quantity}
            for book_id, quantity in top_books_result
        ]

        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "order_by_status": status_counts,
            "top_books": top_books,
        }



