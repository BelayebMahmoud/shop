"""FR-06 / FR-07 / FR-08: placing, reading and moving orders through the workflow, in one transaction each."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Product, User
from app.services import audit
from app.services.errors import NotFound
from app.services.order_rules import Line, check_stock, merge_lines, price_lines, subtotal_cents, validate_lines
from app.services.pricing import compute_totals
from app.services.workflow import BACK_OFFICE, CANCELLED, cancel_restock, check_transition


def _lock_products(db: Session, product_ids: list[int]) -> dict[int, Product]:
    # Lock rows in id order so concurrent checkouts cannot oversell or deadlock (BR-01, QR-RE-02).
    stmt = select(Product).where(Product.id.in_(product_ids)).order_by(Product.id).with_for_update()
    return {p.id: p for p in db.scalars(stmt).all()}


def place_order(db: Session, user: User, lines: list[Line]) -> Order:
    validate_lines(lines)  # BR-03
    wanted = merge_lines(lines)
    products = _lock_products(db, list(wanted))
    missing = sorted(set(wanted) - set(products))
    if missing:
        raise NotFound("PRODUCT_NOT_FOUND", product_ids=missing)
    check_stock(wanted, {pid: p.stock for pid, p in products.items()})  # BR-01
    priced = price_lines(wanted, {pid: p.price_cents for pid, p in products.items()})  # BR-02
    totals = compute_totals(subtotal_cents(priced))  # BR-04

    order = Order(
        user_id=user.id,
        subtotal_cents=totals.subtotal_cents,
        discount_cents=totals.discount_cents,
        total_cents=totals.total_cents,
    )
    for line in priced:
        products[line.product_id].stock -= line.quantity
        order.items.append(OrderItem(product_id=line.product_id, quantity=line.quantity, unit_price_cents=line.unit_price_cents))
    db.add(order)
    db.flush()
    audit.record(db, user.id, audit.ORDER_CREATED, "order", order.id, total_cents=order.total_cents)
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session, user: User) -> list[Order]:
    stmt = select(Order).order_by(Order.id.desc())
    if user.role not in BACK_OFFICE:
        stmt = stmt.where(Order.user_id == user.id)
    return list(db.scalars(stmt).all())


def get_order(db: Session, user: User, order_id: int, lock: bool = False) -> Order:
    """BR-08: another user's order is reported as not found to a CUSTOMER."""
    stmt = select(Order).where(Order.id == order_id)
    if lock:
        stmt = stmt.with_for_update()
    order = db.scalar(stmt)
    if order is None or (user.role not in BACK_OFFICE and order.user_id != user.id):
        raise NotFound("NOT_FOUND")
    return order


def change_status(db: Session, user: User, order_id: int, target: str) -> Order:
    order = get_order(db, user, order_id, lock=True)
    previous = order.status
    if target == CANCELLED:  # BR-05 + BR-06: refused transitions return no stock movement
        back = cancel_restock(previous, user.role, ((item.product_id, item.quantity) for item in order.items))
        for product_id, product in _lock_products(db, list(back)).items():
            product.stock += back[product_id]
    else:
        check_transition(previous, target, user.role)  # BR-05
    order.status = target
    order.updated_at = func.now()
    action = audit.ORDER_CANCELLED if target == CANCELLED else audit.ORDER_STATUS_CHANGED
    audit.record(db, user.id, action, "order", order.id, **{"from": previous, "to": target})
    db.commit()
    db.refresh(order)
    return order
