"""BR-04 discount — cases CT-10 to CT-18 of docs/cahier-de-test.md (partitions, boundaries, half-up rounding).

Expected values are copied from the cahier (amounts in cents), never computed from the code under test.
"""

import pytest

from app.services.errors import InvalidInput
from app.services.pricing import compute_totals

pytestmark = pytest.mark.req("BR-04")


@pytest.mark.parametrize(
    ("subtotal", "discount", "total"),
    [
        pytest.param(0, 0, 0, id="CT-52"),  # lower boundary of the 0 % partition
        pytest.param(5_000, 0, 5_000, id="CT-10"),  # 0 % partition, representative
        pytest.param(9_999, 0, 9_999, id="CT-11"),  # last value before 100.00
        pytest.param(10_000, 500, 9_500, id="CT-12"),  # first value of the 5 % partition
        pytest.param(15_000, 750, 14_250, id="CT-13"),  # 5 % representative
        pytest.param(19_999, 1_000, 18_999, id="CT-14"),  # 9.9995 rounded half-up to 10.00
        pytest.param(20_000, 2_000, 18_000, id="CT-15"),  # first value of the 10 % partition
        pytest.param(30_000, 3_000, 27_000, id="CT-16"),  # 10 % representative
        pytest.param(10_010, 501, 9_509, id="CT-17"),  # 5.005 rounded half-up to 5.01
    ],
)
def test_discount(subtotal, discount, total):
    # Arrange: subtotal from the cahier. Act:
    result = compute_totals(subtotal)
    # Assert
    assert (result.subtotal_cents, result.discount_cents, result.total_cents) == (subtotal, discount, total)


@pytest.mark.parametrize("subtotal", [pytest.param(-1, id="CT-18")])
def test_negative_subtotal_is_refused(subtotal):
    with pytest.raises(InvalidInput) as err:
        compute_totals(subtotal)
    assert err.value.code == "NEGATIVE_SUBTOTAL"
    assert err.value.extra == {"subtotal_cents": subtotal}
