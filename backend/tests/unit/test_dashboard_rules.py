"""FR-09 dashboard calculations — CT-48 to CT-50 of docs/cahier-de-test.md."""

import pytest

from app.services.dashboard_rules import is_low_stock, revenue_cents, top_products

pytestmark = pytest.mark.req("FR-09")


@pytest.mark.parametrize(("listed", "not_listed"), [pytest.param(4, 5, id="CT-48")])
def test_low_stock_threshold(listed, not_listed):
    assert is_low_stock(listed) is True
    assert is_low_stock(not_listed) is False


@pytest.mark.parametrize(
    ("sold", "expected"),
    [
        pytest.param(
            {11: 9, 12: 8, 13: 7, 14: 6, 15: 5, 16: 4},
            [(11, 9), (12, 8), (13, 7), (14, 6), (15, 5)],
            id="CT-49",
        )
    ],
)
def test_top_five_products(sold, expected):
    assert top_products(sold) == expected


@pytest.mark.parametrize(
    ("orders", "expected"),
    [
        pytest.param(
            [("PLACED", 5_000), ("PAID", 11_400), ("SHIPPED", 2_000), ("DELIVERED", 3_000), ("CANCELLED", 8_000)],
            16_400,  # 164.00 EUR, decision Q-03
            id="CT-50",
        )
    ],
)
def test_revenue_counts_paid_shipped_delivered(orders, expected):
    assert revenue_cents(orders) == expected
