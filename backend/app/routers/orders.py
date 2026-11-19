from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Order, OrderItem, Product, User
from app.schemas import OrderCreate, OrderItemOut, OrderOut
from app.security import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


def to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        status=order.status,
        total_cents=order.total_cents,
        created_at=order.created_at,
        items=[
            OrderItemOut(product_id=i.product_id, name=i.product.name, quantity=i.quantity,
                         unit_price_cents=i.unit_price_cents)
            for i in order.items
        ],
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(body: OrderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderOut:
    wanted: dict[int, int] = {}
    for line in body.items:  # merge duplicate lines
        wanted[line.product_id] = wanted.get(line.product_id, 0) + line.quantity

    # Lock the rows in id order so concurrent checkouts cannot oversell or deadlock.
    products = db.scalars(
        select(Product).where(Product.id.in_(wanted)).order_by(Product.id).with_for_update()
    ).all()
    found = {p.id: p for p in products}

    missing = sorted(set(wanted) - set(found))
    if missing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, {"code": "PRODUCT_NOT_FOUND", "product_ids": missing})
    short = sorted(pid for pid, qty in wanted.items() if found[pid].stock < qty)
    if short:
        raise HTTPException(status.HTTP_409_CONFLICT, {"code": "OUT_OF_STOCK", "product_ids": short})

    order = Order(user_id=user.id, total_cents=0)
    for pid, qty in wanted.items():
        product = found[pid]
        product.stock -= qty
        order.items.append(OrderItem(product_id=pid, quantity=qty, unit_price_cents=product.price_cents))
        order.total_cents += qty * product.price_cents  # server-side price, client prices are ignored
    db.add(order)
    db.commit()
    db.refresh(order)
    return to_out(order)


@router.get("", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[OrderOut]:
    orders = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())).all()
    return [to_out(o) for o in orders]
