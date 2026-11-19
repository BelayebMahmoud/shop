"""MA-02 / BR-04 property-based test (fiche 2: « la remise n'est jamais négative ni supérieure au total »).

Hypothesis generates thousands of subtotals; the three properties come from the rule, not from the code:
the discount is never negative, never above the subtotal, and never decreases when the subtotal grows.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.pricing import compute_totals

SUBTOTALS = st.integers(min_value=0, max_value=100_000_000)  # 0 to 1,000,000.00 EUR in cents


@pytest.mark.req("BR-04", "QR-MA-01")
@pytest.mark.case("MA-02")
@settings(max_examples=2_000, deadline=None)
@given(subtotal=SUBTOTALS)
def test_discount_bounds(subtotal):
    t = compute_totals(subtotal)
    assert 0 <= t.discount_cents <= t.subtotal_cents
    assert t.total_cents == t.subtotal_cents - t.discount_cents
    assert t.discount_cents <= (subtotal * 10 + 50) // 100  # never more than 10 % (rounded half-up)


@pytest.mark.req("BR-04", "QR-MA-01")
@pytest.mark.case("MA-02")
@settings(max_examples=2_000, deadline=None)
@given(a=SUBTOTALS, b=SUBTOTALS)
def test_discount_never_decreases_when_subtotal_grows(a, b):
    low, high = sorted((a, b))
    assert compute_totals(low).discount_cents <= compute_totals(high).discount_cents
