"""FR-09: dashboard indicators with date-range (inclusive, UTC — Q-04) and category filters."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import Select, exists, func, select
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Product
from app.services.dashboard_rules import LOW_STOCK_BELOW, REVENUE_STATUSES, revenue_cents, top_products
from app.services.errors import InvalidInput
from app.services.workflow import STATUSES

LOW_STOCK_LIST_LIMIT = 50


@dataclass(frozen=True)
class Dashboard:
    revenue_cents: int
    orders_by_status: dict[str, int]
    top_products: list[tuple[int, str, int]]  # (product_id, name, quantity)
    low_stock: list[Product]
    low_stock_total: int


def _filter_orders(stmt: Select, date_from: date | None, date_to: date | None, category_id: int | None) -> Select:
    if date_from is not None:
        stmt = stmt.where(Order.created_at >= datetime.combine(date_from, time.min, UTC))
    if date_to is not None:  # inclusive end date: strictly before the next day
        stmt = stmt.where(Order.created_at < datetime.combine(date_to + timedelta(days=1), time.min, UTC))
    if category_id is not None:
        in_category = (
            select(OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(OrderItem.order_id == Order.id, Product.category_id == category_id)
        )
        stmt = stmt.where(exists(in_category))
    return stmt


def _counts_and_revenue(db: Session, date_from, date_to, category_id) -> tuple[dict[str, int], int]:
    stmt = _filter_orders(select(Order.status, func.count(), func.sum(Order.total_cents)), date_from, date_to, category_id)
    by_status = db.execute(stmt.group_by(Order.status)).all()
    counts = dict.fromkeys(STATUSES, 0) | {status: n for status, n, _ in by_status}
    return counts, revenue_cents((status, int(total)) for status, _, total in by_status)


def _top_sold(db: Session, date_from, date_to, category_id) -> list[tuple[int, str, int]]:
    sold_stmt = (
        select(OrderItem.product_id, Product.name, func.sum(OrderItem.quantity))
        .join(Order, Order.id == OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .where(Order.status.in_(REVENUE_STATUSES))
        .group_by(OrderItem.product_id, Product.name)
    )
    sold_stmt = _filter_orders(sold_stmt, date_from, date_to, None)
    if category_id is not None:
        sold_stmt = sold_stmt.where(Product.category_id == category_id)
    sold = {pid: (name, int(qty)) for pid, name, qty in db.execute(sold_stmt).all()}
    return [(pid, sold[pid][0], qty) for pid, qty in top_products({pid: v[1] for pid, v in sold.items()})]


def _low_stock(db: Session, category_id) -> tuple[list[Product], int]:
    low_stmt = select(Product).where(Product.stock < LOW_STOCK_BELOW)
    if category_id is not None:
        low_stmt = low_stmt.where(Product.category_id == category_id)
    total = db.scalar(select(func.count()).select_from(low_stmt.subquery()))
    return list(db.scalars(low_stmt.order_by(Product.stock, Product.id).limit(LOW_STOCK_LIST_LIMIT)).all()), total


def compute(db: Session, date_from: date | None, date_to: date | None, category_id: int | None) -> Dashboard:
    """FR-09 indicators. Split into single-purpose helpers to keep each under complexity 10 (ANO-08)."""
    if date_from is not None and date_to is not None and date_from > date_to:
        raise InvalidInput("DATE_RANGE")
    counts, revenue = _counts_and_revenue(db, date_from, date_to, category_id)
    top = _top_sold(db, date_from, date_to, category_id)
    low, low_total = _low_stock(db, category_id)
    return Dashboard(revenue, counts, top, low, low_total)
