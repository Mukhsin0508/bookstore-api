from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_db
from app.services import OrderService
from app.core.payment import process_payment
from app.schemas import OrderCreate, OrderList
from app.models import User, OrderStatus
from app.schemas import Order
from app.api.deps import get_current_active_user
from app.schemas.payment import PaymentRequest, PaymentResponse

router = APIRouter()


@router.get("/", response_model=OrderList)
async def read_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """Get current user's orders"""
    orders = await OrderService.get_user_orders(
        db, current_user.id, skip=skip, limit=limit
    )
    total = await OrderService.get_total_count(db, user_id=current_user.id)

    return {
        "orders": orders,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "pages": (total + limit - 1) // limit,
    }

@router.get("/{order_id}", response_model=Order)
async def read_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get order by ID"""
    order = await OrderService.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # === Check if user owns the order ===
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order",
        )
    return order

@router.post("/", response_model=Order)
async def create_order(
    order_create: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create new order"""
    if not order_create.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    order = await OrderService.create(db, current_user, order_create)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create order, check book availability",
        )

    return order


@router.post("/{order_id/pay", response_model=PaymentResponse)
async def pay_order(
    order_id: int,
    payment_request: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Pay an order"""
    # === Validate order_id in request matches path ===
    if payment_request.order_id != order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID mismatch",
        )

    # === Get Order ===
    order = await OrderService.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # === Check if user owns the order ===
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # === Check if order's already been paid ===
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order status is already paid",
        )

    # === Process the payment ===
    success, message, transaction_id = await process_payment(
        payment_request.card_number
    )

    if success:
        # === Update order status and stock ===
        order = await OrderService.process_payment_success(
            db, order, payment_request.card_number
        )
    else:
        # === Update order status to fail ===
        order = await OrderService.update_status(
            db, order, OrderStatus.FAILED, payment_request.card_number
        )

    return {
        "success": success,
        "message": message,
        "order_id": order_id,
        "transaction_id": transaction_id,
    }


@router.post("/{order_id}/cancel", response_model=Order)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Cancel an order"""
    order = await OrderService.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    # === Check if user owns the order ===
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order",
        )

    # === Check if order can be cancelled ===
    if order.status not in [OrderStatus.PENDING, OrderStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}"
        )

    # === Update order status ===
    order = await OrderService.update_status(db, order, OrderStatus.CANCELLED)
    return order


