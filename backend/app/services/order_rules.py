"""Pure order rules, testable without a database: BR-03 bounds, BR-01 stock check, BR-02 catalogue prices."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.services.errors import Conflict, InvalidInput

MIN_QUANTITY, MAX_QUANTITY = 1, 99
MIN_LINES, MAX_LINES = 1, 50


@dataclass(frozen=True)
class Line:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class PricedLine:
    product_id: int
    quantity: int
    unit_price_cents: int


def validate_lines(lines: list[Line]) -> None:
    """BR-03 on the lines as sent (decision Q-01): 1..50 lines, quantity 1..99 per line."""
    if not MIN_LINES <= len(lines) <= MAX_LINES:
        raise InvalidInput("LINE_COUNT", min=MIN_LINES, max=MAX_LINES, received=len(lines))
    bad = [line.product_id for line in lines if not MIN_QUANTITY <= line.quantity <= MAX_QUANTITY]
    if bad:
        raise InvalidInput("QUANTITY_RANGE", min=MIN_QUANTITY, max=MAX_QUANTITY, product_ids=bad)


def merge_lines(lines: Iterable[Line]) -> dict[int, int]:
    """Same product on several lines -> one quantity per product (decision Q-01), in first-seen order."""
    wanted: dict[int, int] = {}
    for line in lines:
        wanted[line.product_id] = wanted.get(line.product_id, 0) + line.quantity
    return wanted


def check_stock(wanted: Mapping[int, int], stock: Mapping[int, int]) -> None:
    """BR-01: refuse the whole order if any line exceeds its product's stock."""
    short = sorted(pid for pid, qty in wanted.items() if stock[pid] < qty)
    if short:
        raise Conflict("OUT_OF_STOCK", product_ids=short)


def price_lines(wanted: Mapping[int, int], catalogue_prices: Mapping[int, int]) -> list[PricedLine]:
    """BR-02: the unit price comes from the catalogue; any price sent by the client is never an input here."""
    return [PricedLine(pid, qty, catalogue_prices[pid]) for pid, qty in wanted.items()]


def subtotal_cents(lines: Iterable[PricedLine]) -> int:
    return sum(line.quantity * line.unit_price_cents for line in lines)
