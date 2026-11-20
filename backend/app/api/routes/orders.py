"""Orders: FR-06 (customer), FR-07 (back-office), FR-08 workflow."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.api.responses import errors
from app.api.types import IdPath
from app.api.schemas import OrderCreate, OrderItemOut, OrderOut, StatusChange
from app.models import Order, User
from app.services import orders
from app.services.order_rules import Line
from app.services.workflow import ADMIN, CANCELLED, CUSTOMER, STAFF

router = APIRouter(prefix="/orders", tags=["orders"])


def to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        subtotal_cents=order.subtotal_cents,
        discount_cents=order.discount_cents,
        total_cents=order.total_cents,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemOut(product_id=i.product_id, name=i.product.name, quantity=i.quantity, unit_price_cents=i.unit_price_cents)
            for i in order.items
        ],
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED, responses=errors(400, 401, 403, 404, 409, 422))
def create_order(body: OrderCreate, user: User = Depends(require_roles(CUSTOMER)), db: Session = Depends(get_db)) -> OrderOut:
    lines = [Line(item.product_id, item.quantity) for item in body.items]
    return to_out(orders.place_order(db, user, lines))


@router.get("", response_model=list[OrderOut], responses=errors(401, 422))
def list_orders(
    status: Literal["PLACED", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"] | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, le=1_000_000_000),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderOut]:
    """A customer sees their own orders, STAFF and ADMIN all orders; most recent first, paginated."""
    return [to_out(o) for o in orders.list_orders(db, user, status, limit, offset)]


@router.get("/{order_id}", response_model=OrderOut, responses=errors(401, 404, 422))
def get_order(order_id: IdPath, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderOut:
    return to_out(orders.get_order(db, user, order_id))


@router.post("/{order_id}/cancel", response_model=OrderOut, responses=errors(401, 403, 404, 409, 422))
def cancel_order(order_id: IdPath, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderOut:
    return to_out(orders.change_status(db, user, order_id, CANCELLED))


@router.patch("/{order_id}/status", response_model=OrderOut, responses=errors(400, 401, 403, 404, 409, 422))
def change_status(
    order_id: IdPath,
    body: StatusChange,
    user: User = Depends(require_roles(STAFF, ADMIN)),
    db: Session = Depends(get_db),
) -> OrderOut:
    return to_out(orders.change_status(db, user, order_id, body.status))
