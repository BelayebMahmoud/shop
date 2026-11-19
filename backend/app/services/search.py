"""FR-10: filtered, paginated product search (price bounds inclusive, min > max refused — Q-05)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Product
from app.services.errors import InvalidInput


def _like_pattern(text: str) -> str:
    """Contains-match on user text, with LIKE wildcards escaped so they match literally."""
    escaped = text.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def search_products(
    db: Session,
    q: str | None = None,
    category_id: int | None = None,
    min_price_cents: int | None = None,
    max_price_cents: int | None = None,
    in_stock: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Product], int]:
    if min_price_cents is not None and max_price_cents is not None and min_price_cents > max_price_cents:
        raise InvalidInput("PRICE_RANGE")
    stmt = select(Product)
    if q:
        stmt = stmt.where(func.lower(Product.name).like(_like_pattern(q), escape="\\"))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if min_price_cents is not None:
        stmt = stmt.where(Product.price_cents >= min_price_cents)
    if max_price_cents is not None:
        stmt = stmt.where(Product.price_cents <= max_price_cents)
    if in_stock:
        stmt = stmt.where(Product.stock > 0)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(Product.id).limit(limit).offset(offset)).all()
    return list(items), total
