"""FR-09 pure calculations: low stock, top products, revenue (decision Q-03)."""

from collections.abc import Iterable, Mapping

from app.services.workflow import DELIVERED, PAID, SHIPPED

LOW_STOCK_BELOW = 5
TOP_N = 5
REVENUE_STATUSES = frozenset({PAID, SHIPPED, DELIVERED})


def is_low_stock(stock: int) -> bool:
    """Low stock means strictly below 5."""
    return stock < LOW_STOCK_BELOW


def top_products(quantity_by_product: Mapping[int, int], n: int = TOP_N) -> list[tuple[int, int]]:
    """The n products with the largest sold quantity, largest first; ties broken by product id."""
    ranked = sorted(quantity_by_product.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


def revenue_cents(orders: Iterable[tuple[str, int]]) -> int:
    """Sum of totals after discount of PAID, SHIPPED and DELIVERED orders. Input: (status, total_cents)."""
    return sum(total for status, total in orders if status in REVENUE_STATUSES)
