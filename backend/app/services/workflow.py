"""BR-05 / BR-06: order status workflow, who may apply each transition, and restocking on cancel."""

from collections.abc import Iterable, Mapping

from app.services.errors import Conflict, Forbidden

PLACED, PAID, SHIPPED, DELIVERED, CANCELLED = "PLACED", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"
STATUSES = (PLACED, PAID, SHIPPED, DELIVERED, CANCELLED)

CUSTOMER, STAFF, ADMIN = "CUSTOMER", "STAFF", "ADMIN"
BACK_OFFICE = frozenset({STAFF, ADMIN})

# Allowed target statuses from each status (PLACED -> PAID -> SHIPPED -> DELIVERED; PLACED or PAID -> CANCELLED).
TRANSITIONS: Mapping[str, frozenset[str]] = {
    PLACED: frozenset({PAID, CANCELLED}),
    PAID: frozenset({SHIPPED, CANCELLED}),
    SHIPPED: frozenset({DELIVERED}),
    DELIVERED: frozenset(),
    CANCELLED: frozenset(),
}


def check_transition(current: str, target: str, actor_role: str) -> None:
    """Raise Conflict(INVALID_TRANSITION) if the workflow forbids it, Forbidden if the role may not apply it.

    The caller has already checked ownership: a CUSTOMER only ever reaches this for their own order (BR-08).
    """
    if target not in TRANSITIONS.get(current, frozenset()):
        raise Conflict("INVALID_TRANSITION", current=current, target=target)
    if actor_role in BACK_OFFICE:
        return
    # A CUSTOMER may only cancel their own PLACED order (BR-05; PAID -> 403, decision Q-02).
    if not (target == CANCELLED and current == PLACED):
        raise Forbidden("FORBIDDEN", current=current, target=target)


def restock_quantities(lines: Iterable[tuple[int, int]]) -> dict[int, int]:
    """BR-06: quantity to put back in stock per product when an order is cancelled."""
    back: dict[int, int] = {}
    for product_id, quantity in lines:
        back[product_id] = back.get(product_id, 0) + quantity
    return back


def cancel_restock(current: str, actor_role: str, lines: Iterable[tuple[int, int]]) -> dict[int, int]:
    """BR-05 then BR-06: check the cancel is allowed, and only then return the stock to put back per product.

    A refused cancel (for instance after SHIPPED) raises before any quantity is computed, so no stock moves.
    """
    check_transition(current, CANCELLED, actor_role)
    return restock_quantities(lines)
