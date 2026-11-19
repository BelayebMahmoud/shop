"""BR-05 / BR-06 state-transition table — CT-19 to CT-43 and CT-53 to CT-56 of docs/cahier-de-test.md.

Every state x every event (table 0.4 of the cahier), the actor's rights, and the restock on cancel.
`check_transition` returning without error means the order may move to the target status; the stored status
itself is checked at integration and API level (IT-07, TA-15).
"""

import pytest

from app.services.errors import Conflict, Forbidden
from app.services.workflow import (
    ADMIN,
    CANCELLED,
    CUSTOMER,
    DELIVERED,
    PAID,
    PLACED,
    SHIPPED,
    STAFF,
    cancel_restock,
    check_transition,
)

P1, P2 = 1, 2
BR05, BR06, FR08 = pytest.mark.req("BR-05"), pytest.mark.req("BR-06"), pytest.mark.req("FR-08")


@pytest.mark.parametrize(
    ("current", "target"),
    [
        pytest.param(PLACED, PAID, id="CT-19", marks=[BR05, FR08]),
        pytest.param(PAID, SHIPPED, id="CT-20", marks=[BR05, FR08]),
        pytest.param(SHIPPED, DELIVERED, id="CT-21", marks=[BR05, FR08]),
        pytest.param(PLACED, CANCELLED, id="CT-22", marks=[BR05, BR06, FR08]),
        pytest.param(PAID, CANCELLED, id="CT-23", marks=[BR05, BR06, FR08]),
    ],
)
def test_allowed_transition_by_staff(current, target):
    check_transition(current, target, STAFF)  # Assert: no exception


@pytest.mark.parametrize(
    ("current", "target"),
    [
        pytest.param(PLACED, SHIPPED, id="CT-24", marks=BR05),
        pytest.param(PLACED, DELIVERED, id="CT-25", marks=BR05),
        pytest.param(PAID, PAID, id="CT-26", marks=BR05),
        pytest.param(PAID, DELIVERED, id="CT-27", marks=BR05),
        pytest.param(SHIPPED, PAID, id="CT-28", marks=BR05),
        pytest.param(SHIPPED, SHIPPED, id="CT-29", marks=BR05),
        pytest.param(SHIPPED, CANCELLED, id="CT-30", marks=[BR05, BR06]),
        pytest.param(DELIVERED, PAID, id="CT-31", marks=BR05),
        pytest.param(DELIVERED, SHIPPED, id="CT-32", marks=BR05),
        pytest.param(DELIVERED, DELIVERED, id="CT-33", marks=BR05),
        pytest.param(DELIVERED, CANCELLED, id="CT-34", marks=[BR05, BR06]),
        pytest.param(CANCELLED, PAID, id="CT-35", marks=BR05),
        pytest.param(CANCELLED, SHIPPED, id="CT-36", marks=BR05),
        pytest.param(CANCELLED, DELIVERED, id="CT-37", marks=BR05),
        pytest.param(CANCELLED, CANCELLED, id="CT-38", marks=BR05),
    ],
)
def test_forbidden_transition_is_refused(current, target):
    with pytest.raises(Conflict) as err:
        check_transition(current, target, STAFF)
    assert err.value.code == "INVALID_TRANSITION"


@pytest.mark.req("BR-05")
@pytest.mark.parametrize(
    ("current", "target"),
    [
        pytest.param(PLACED, PAID, id="CT-39"),  # a customer cannot pay
        pytest.param(PAID, CANCELLED, id="CT-41"),  # decision Q-02: 403
        pytest.param(PAID, SHIPPED, id="CT-54"),  # a customer cannot ship
        pytest.param(SHIPPED, DELIVERED, id="CT-55"),  # a customer cannot deliver
    ],
)
def test_customer_may_not_apply(current, target):
    with pytest.raises(Forbidden) as err:
        check_transition(current, target, CUSTOMER)
    assert err.value.code == "FORBIDDEN"


@pytest.mark.req("BR-05")
@pytest.mark.parametrize(("current", "target"), [pytest.param(PLACED, CANCELLED, id="CT-40")])
def test_customer_cancels_own_placed_order(current, target):
    check_transition(current, target, CUSTOMER)


@pytest.mark.req("BR-05")
@pytest.mark.parametrize(
    "transitions",
    [pytest.param([(PLACED, PAID), (PAID, SHIPPED), (SHIPPED, DELIVERED), (PLACED, CANCELLED), (PAID, CANCELLED)], id="CT-53")],
)
def test_admin_has_the_same_rights_as_staff(transitions):
    for current, target in transitions:
        check_transition(current, target, ADMIN)


@pytest.mark.req("BR-06")
@pytest.mark.parametrize(
    ("lines", "stock_after_order", "expected_stock"),
    [pytest.param([(P1, 2), (P2, 1)], {P1: 8, P2: 2}, {P1: 10, P2: 3}, id="CT-42")],
)
def test_cancel_puts_every_line_back_in_stock(lines, stock_after_order, expected_stock):
    back = cancel_restock(PLACED, STAFF, lines)
    assert {pid: stock_after_order[pid] + back.get(pid, 0) for pid in stock_after_order} == expected_stock


@pytest.mark.req("BR-06")
@pytest.mark.parametrize(
    ("current", "actor"),
    [
        pytest.param(SHIPPED, STAFF, id="CT-43"),
        pytest.param(SHIPPED, CUSTOMER, id="CT-56"),  # BR-06: 409 even for the owner, not 403
    ],
)
def test_no_restock_after_shipping(current, actor):
    """A refused cancel raises before any quantity is returned, so no stock movement can happen."""
    with pytest.raises(Conflict) as err:
        cancel_restock(current, actor, [(P1, 2)])
    assert err.value.code == "INVALID_TRANSITION"
