"""Order API tests — status + body + real effect, in the order identity -> shape -> existence -> rule.

Cases TA-03 to TA-07, TA-13 to TA-16, TA-25, TA-26, TA-29 of docs/cahier-de-test.md (decision table 0.3).
"""

import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.db import SessionLocal
from app.main import app
from app.models import AuditLog, Order, Product
from app.services import orders as orders_service


def orders_count() -> int:
    with SessionLocal() as s:
        return s.scalar(select(func.count()).select_from(Order))


def stock_of(product_id: int) -> int:
    with SessionLocal() as s:
        return s.get(Product, product_id).stock


def status_of(order_id: int) -> str:
    with SessionLocal() as s:
        return s.get(Order, order_id).status


def body(*lines):
    return {"items": [{"product_id": p.id, "quantity": q} for p, q in lines]}


# ---------------------------------------------------------------- decision table R1..R5
@pytest.mark.req("FR-01", "FR-06")
@pytest.mark.parametrize("headers", [pytest.param({}, id="TA-03")])
def test_r1_no_token(client, make, headers):
    p1 = make.product(4_000, 10)
    r = client.post("/api/orders", json=body((p1, 1)), headers=headers)
    assert r.status_code == 401
    assert orders_count() == 0 and stock_of(p1.id) == 10


@pytest.mark.req("BR-03", "FR-06")
@pytest.mark.parametrize(
    ("lines", "field"),
    [pytest.param("quantity0", "quantity", id="TA-05-quantity"), pytest.param("lines51", "items", id="TA-05-lines")],
)
def test_r2_invalid_body(client, make, lines, field):
    ana, p1 = make.user(), make.product(4_000, 10)
    payload = body((p1, 0)) if lines == "quantity0" else {"items": [{"product_id": p1.id, "quantity": 1}] * 51}
    r = client.post("/api/orders", json=payload, headers=ana.headers)
    assert r.status_code == 422
    assert any(field in err["loc"] for err in r.json()["detail"])  # the faulty field is named
    assert orders_count() == 0 and stock_of(p1.id) == 10


@pytest.mark.req("FR-06")
@pytest.mark.parametrize("product_id", [pytest.param(999_999, id="TA-29")])
def test_r3_unknown_product(client, make, product_id):
    ana, p1 = make.user(), make.product(4_000, 10)
    r = client.post(
        "/api/orders",
        json={"items": [{"product_id": p1.id, "quantity": 1}, {"product_id": product_id, "quantity": 1}]},
        headers=ana.headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "PRODUCT_NOT_FOUND"
    assert orders_count() == 0 and stock_of(p1.id) == 10


@pytest.mark.req("BR-01", "FR-06")
@pytest.mark.parametrize("quantity", [pytest.param(4, id="TA-06")])
def test_r4_out_of_stock(client, make, quantity):
    ana, p2 = make.user(), make.product(5_000, 3)
    r = client.post("/api/orders", json=body((p2, quantity)), headers=ana.headers)
    assert r.status_code == 409
    assert r.json()["detail"] == {"code": "OUT_OF_STOCK", "product_ids": [p2.id]}
    assert orders_count() == 0 and stock_of(p2.id) == 3


@pytest.mark.req("FR-06", "BR-04", "BR-01")
@pytest.mark.parametrize("quantity", [pytest.param(3, id="TA-04")])
def test_r5_valid_order_with_discount(client, make, quantity):
    ana, p1 = make.user(), make.product(4_000, 10)
    r = client.post("/api/orders", json=body((p1, quantity)), headers=ana.headers)
    assert r.status_code == 201
    created = r.json()
    expected = {"subtotal_cents": 12_000, "discount_cents": 600, "total_cents": 11_400, "status": "PLACED"}
    assert {k: created[k] for k in expected} == expected
    assert stock_of(p1.id) == 7
    again = client.get(f"/api/orders/{created['id']}", headers=ana.headers)
    assert again.status_code == 200 and {k: again.json()[k] for k in expected} == expected


@pytest.mark.req("BR-02", "FR-06")
@pytest.mark.parametrize("client_price", [pytest.param(1, id="TA-07")])
def test_client_price_is_ignored(client, make, client_price):
    ana, p1 = make.user(), make.product(4_000, 10)
    line = {"product_id": p1.id, "quantity": 1, "unit_price": client_price, "unit_price_cents": client_price}
    r = client.post("/api/orders", json={"items": [line]}, headers=ana.headers)
    assert r.status_code == 201
    assert r.json()["items"][0]["unit_price_cents"] == 4_000
    assert r.json()["total_cents"] == 4_000


# ---------------------------------------------------------------- concurrency
@pytest.mark.req("BR-01", "QR-RE-02")
@pytest.mark.parametrize("stock", [pytest.param(2, id="TA-13")])
def test_two_simultaneous_orders_for_the_last_units(client, make, monkeypatch, stock):
    """Forces the race: each checkout waits for the other between reading the stock and writing it.

    With the row lock, the second request is blocked before it reads, the first one's wait times out, it commits,
    and the second then sees stock 0 (409). Without the lock, both read stock 2 and both would succeed.
    """
    ana, bob, p5 = make.user(), make.user(), make.product(1_000, stock)
    start, meet = threading.Barrier(2), threading.Barrier(2)
    real_check_stock = orders_service.check_stock
    statuses: list[int] = []

    def check_stock_after_meeting(wanted, available):
        try:
            meet.wait(timeout=2)  # both requests have read the stock, unless the lock keeps one out
        except threading.BrokenBarrierError:
            pass
        return real_check_stock(wanted, available)

    monkeypatch.setattr(orders_service, "check_stock", check_stock_after_meeting)

    def checkout(headers):
        start.wait()  # release both requests together
        with TestClient(app) as own_client:  # one client per thread: truly concurrent requests
            statuses.append(own_client.post("/api/orders", json=body((p5, 2)), headers=headers).status_code)

    threads = [threading.Thread(target=checkout, args=(a.headers,)) for a in (ana, bob)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert sorted(statuses) == [201, 409]
    assert stock_of(p5.id) == 0
    assert orders_count() == 1


# ---------------------------------------------------------------- workflow through the API
@pytest.mark.req("FR-06", "BR-06")
@pytest.mark.parametrize("quantity", [pytest.param(2, id="TA-14")])
def test_customer_cancels_own_order(client, make, quantity):
    ana, p1 = make.user(), make.product(4_000, 10)
    order = make.order(ana, [(p1, quantity)])
    r = client.post(f"/api/orders/{order.id}/cancel", headers=ana.headers)
    assert r.status_code == 200 and r.json()["status"] == "CANCELLED"
    assert status_of(order.id) == "CANCELLED" and stock_of(p1.id) == 10


@pytest.mark.req("FR-07", "BR-05", "FR-11")
@pytest.mark.parametrize("steps", [pytest.param(["PAID", "SHIPPED"], id="TA-15")])
def test_staff_moves_order_through_workflow(client, make, steps):
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(4_000, 10)
    order = make.order(ana, [(p1, 1)])
    codes = [client.patch(f"/api/orders/{order.id}/status", json={"status": s}, headers=sam.headers).status_code for s in steps]
    assert codes == [200, 200]
    assert status_of(order.id) == "SHIPPED"
    with SessionLocal() as s:
        changes = s.scalar(select(func.count()).where(AuditLog.action == "ORDER_STATUS_CHANGED", AuditLog.entity_id == order.id))
    assert changes == 2


@pytest.mark.req("FR-07", "BR-05", "BR-06")
@pytest.mark.parametrize("target", [pytest.param("CANCELLED", id="TA-16")])
def test_forbidden_transition_through_api(client, make, target):
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(4_000, 10)
    order = make.order(ana, [(p1, 1)], status="SHIPPED")
    r = client.patch(f"/api/orders/{order.id}/status", json={"status": target}, headers=sam.headers)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "INVALID_TRANSITION"
    assert status_of(order.id) == "SHIPPED" and stock_of(p1.id) == 9


# ---------------------------------------------------------------- isolation between customers (BR-08)
@pytest.mark.req("BR-08")
@pytest.mark.parametrize("reader", [pytest.param("bob", id="TA-25")])
def test_customer_cannot_read_another_customers_order(client, make, reader):
    ana, bob, p1 = make.user(), make.user(), make.product(4_000, 10)
    order = make.order(ana, [(p1, 1)])
    assert client.get(f"/api/orders/{order.id}", headers=bob.headers).status_code == 404
    assert order.id not in [o["id"] for o in client.get("/api/orders", headers=bob.headers).json()]


@pytest.mark.req("BR-08")
@pytest.mark.parametrize("quantity", [pytest.param(2, id="TA-26")])
def test_customer_cannot_cancel_another_customers_order(client, make, quantity):
    ana, bob, p1 = make.user(), make.user(), make.product(4_000, 10)
    order = make.order(ana, [(p1, quantity)])
    r = client.post(f"/api/orders/{order.id}/cancel", headers=bob.headers)
    assert r.status_code == 404
    assert status_of(order.id) == "PLACED" and stock_of(p1.id) == 8


@pytest.mark.req("BR-05", "BR-06")
@pytest.mark.parametrize(
    ("status", "expected", "code"),
    [
        pytest.param("PAID", 403, "FORBIDDEN", id="TA-36-paid"),  # decision Q-02
        pytest.param("SHIPPED", 409, "INVALID_TRANSITION", id="TA-36-shipped"),  # BR-06
    ],
)
def test_customer_cannot_cancel_paid_or_shipped_order(client, make, status, expected, code):
    ana, p1 = make.user(), make.product(4_000, 10)
    order = make.order(ana, [(p1, 2)], status=status)
    r = client.post(f"/api/orders/{order.id}/cancel", headers=ana.headers)
    assert r.status_code == expected and r.json()["detail"]["code"] == code
    assert status_of(order.id) == status and stock_of(p1.id) == 8


@pytest.mark.req("FR-11")
@pytest.mark.parametrize("actor_role", [pytest.param("STAFF", id="TA-37")])
def test_cancel_and_product_changes_are_audited(client, make, actor_role):
    ana, sam, cat = make.user(), make.user(actor_role), make.category()
    p1 = make.product(4_000, 10, category=cat)
    order = make.order(ana, [(p1, 1)])
    assert client.post(f"/api/orders/{order.id}/cancel", headers=ana.headers).status_code == 200
    payload = {"sku": "AUD-1", "name": "Audited", "description": "", "price_cents": 100, "stock": 1, "category_id": cat.id}
    pid = client.post("/api/products", json=payload, headers=sam.headers).json()["id"]
    assert client.put(f"/api/products/{pid}", json=payload | {"price_cents": 200}, headers=sam.headers).status_code == 200
    assert client.delete(f"/api/products/{pid}", headers=sam.headers).status_code == 204
    with SessionLocal() as s:
        rows = s.execute(select(AuditLog.action, AuditLog.actor_id, AuditLog.entity_id)).all()
    assert (audit_actions := {(a, actor, eid) for a, actor, eid in rows}) >= {
        ("ORDER_CANCELLED", ana.id, order.id),
        ("PRODUCT_CREATED", sam.id, pid),
        ("PRODUCT_UPDATED", sam.id, pid),
        ("PRODUCT_DELETED", sam.id, pid),
    }, audit_actions


@pytest.mark.req("FR-07")
@pytest.mark.parametrize("count", [pytest.param(7, id="TA-38")])
def test_back_office_order_list_is_paginated_and_filtered(client, make, count):
    """ANO-09: the list returns one page, most recent first, optionally filtered by status — never every order."""
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(1_000, 100)
    created = [make.order(ana, [(p1, 1)]) for _ in range(count)]
    make.set_status(created[0], "PAID")
    page1 = client.get("/api/orders?limit=3", headers=sam.headers).json()
    page2 = client.get("/api/orders?limit=3&offset=3", headers=sam.headers).json()
    assert [o["id"] for o in page1] == [o.id for o in reversed(created)][:3]  # most recent first
    assert [o["id"] for o in page2] == [o.id for o in reversed(created)][3:6]
    paid = client.get("/api/orders?status=PAID", headers=sam.headers).json()
    assert [o["id"] for o in paid] == [created[0].id]
    assert client.get("/api/orders?limit=201", headers=sam.headers).status_code == 422
    assert len(client.get("/api/orders", headers=ana.headers).json()) == count  # default page (50) holds them all
