"""Order rules without a database.

BR-03 bounds: CT-01 to CT-09. BR-01 stock: CT-44 to CT-46. BR-02 catalogue price: CT-47.
Expected results come from docs/cahier-de-test.md.
"""

import pytest

from app.services.errors import Conflict, InvalidInput
from app.services.order_rules import Line, check_stock, merge_lines, price_lines, subtotal_cents, validate_lines

P1, P2 = 1, 2


def lines_of(count: int, quantity: int = 1) -> list[Line]:
    return [Line(product_id=i + 1, quantity=quantity) for i in range(count)]


# ---------------------------------------------------------------- BR-03
@pytest.mark.req("BR-03")
@pytest.mark.parametrize(
    "lines",
    [
        pytest.param([Line(P1, 1)], id="CT-02"),
        pytest.param([Line(P1, 99)], id="CT-03"),
        pytest.param(lines_of(1), id="CT-07"),
        pytest.param(lines_of(50), id="CT-08"),
    ],
)
def test_valid_order_shape_is_accepted(lines):
    validate_lines(lines)  # Assert: no exception


@pytest.mark.req("BR-03")
@pytest.mark.parametrize(
    ("lines", "code"),
    [
        pytest.param([Line(P1, 0)], "QUANTITY_RANGE", id="CT-01"),
        pytest.param([Line(P1, 100)], "QUANTITY_RANGE", id="CT-04"),
        pytest.param([Line(P1, -1)], "QUANTITY_RANGE", id="CT-05"),
        pytest.param([], "LINE_COUNT", id="CT-06"),
        pytest.param(lines_of(51), "LINE_COUNT", id="CT-09"),
    ],
)
def test_invalid_order_shape_is_refused(lines, code):
    with pytest.raises(InvalidInput) as err:
        validate_lines(lines)
    assert err.value.code == code


@pytest.mark.req("BR-03")
@pytest.mark.parametrize("lines", [pytest.param([Line(P1, 99), Line(P1, 99)], id="CT-51")])
def test_bounds_apply_to_lines_as_sent_then_lines_merge(lines):
    """Decision Q-01: two lines of 99 for the same product are valid, then merged into one quantity."""
    validate_lines(lines)
    assert merge_lines(lines) == {P1: 198}


# ---------------------------------------------------------------- BR-01
@pytest.mark.req("BR-01")
@pytest.mark.parametrize(("wanted", "stock"), [pytest.param({P2: 3}, {P2: 3}, id="CT-44")])
def test_quantity_equal_to_stock_is_accepted(wanted, stock):
    check_stock(wanted, stock)  # Assert: no OUT_OF_STOCK; the remaining stock (0) is checked in TA/IT tests


@pytest.mark.req("BR-01")
@pytest.mark.parametrize(
    ("wanted", "stock", "short"),
    [
        pytest.param({P2: 4}, {P2: 3}, [P2], id="CT-45"),
        pytest.param({P1: 2, P2: 4}, {P1: 10, P2: 3}, [P2], id="CT-46"),
    ],
)
def test_quantity_above_stock_refuses_the_whole_order(wanted, stock, short):
    before = dict(stock)
    with pytest.raises(Conflict) as err:
        check_stock(wanted, stock)
    assert err.value.code == "OUT_OF_STOCK"
    assert err.value.extra["product_ids"] == short
    assert stock == before  # nothing changes


# ---------------------------------------------------------------- BR-02
@pytest.mark.req("BR-02")
@pytest.mark.parametrize("catalogue_price", [pytest.param(4_000, id="CT-47")])
def test_client_price_is_ignored(catalogue_price):
    """A service order line carries no price at all, so a client price cannot reach pricing (API side: TA-07)."""
    # Arrange: one line of P1; the catalogue says 40.00 EUR
    assert {f for f in Line.__dataclass_fields__} == {"product_id", "quantity"}
    # Act
    priced = price_lines(merge_lines([Line(P1, 1)]), {P1: catalogue_price})
    # Assert: unit price and subtotal are the catalogue's 40.00 EUR
    assert priced[0].unit_price_cents == 4_000
    assert subtotal_cents(priced) == 4_000
