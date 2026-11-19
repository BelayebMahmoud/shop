"""BR-04: discount on the order subtotal. Amounts are integer cents, never floats."""

from dataclasses import dataclass

from app.services.errors import InvalidInput

TIER_5_FROM_CENTS = 10_000  # 100.00 EUR
TIER_10_FROM_CENTS = 20_000  # 200.00 EUR


@dataclass(frozen=True)
class Totals:
    subtotal_cents: int
    discount_cents: int
    total_cents: int


def discount_percent(subtotal_cents: int) -> int:
    """< 100.00 -> 0 %; 100.00..199.99 -> 5 %; >= 200.00 -> 10 %."""
    if subtotal_cents < 0:
        raise InvalidInput("NEGATIVE_SUBTOTAL", subtotal_cents=subtotal_cents)
    if subtotal_cents >= TIER_10_FROM_CENTS:
        return 10
    if subtotal_cents >= TIER_5_FROM_CENTS:
        return 5
    return 0


def compute_totals(subtotal_cents: int) -> Totals:
    """Discount rounded half-up to the cent; total = subtotal - discount."""
    percent = discount_percent(subtotal_cents)
    discount = (subtotal_cents * percent + 50) // 100  # half-up on a non-negative value
    return Totals(subtotal_cents, discount, subtotal_cents - discount)
