"""Reliability tests REL-03 and REL-04 (QR-RE-02) and the 503 contract during a database outage (QR-RE-01).

REL-01 and REL-02 (restart of PostgreSQL under load, kill of the API container) run against the Docker stack:
tools/reliability.py.
"""

import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app.core.db import SessionLocal, engine
from app.main import app
from app.models import Order, OrderItem, Product
from app.services import orders as orders_service


@pytest.fixture(autouse=True)
def _isolated_database(fresh_db):
    yield


def state(product_id: int) -> tuple[int, int, int]:
    with SessionLocal() as s:
        return (
            s.scalar(select(func.count()).select_from(Order)),
            s.scalar(select(func.count()).select_from(OrderItem)),
            s.get(Product, product_id).stock,
        )


@pytest.mark.req("QR-RE-02", "BR-01")
@pytest.mark.parametrize("quantity", [pytest.param(3, id="REL-03")])
def test_database_failure_between_two_writes_rolls_everything_back(client, make, quantity):
    """A real PostgreSQL error after the order and its lines are written (trigger on the audit insert)."""
    ana, p1 = make.user(), make.product(4_000, 10)
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE FUNCTION fail_audit() RETURNS trigger LANGUAGE plpgsql AS "
            "$$ BEGIN RAISE EXCEPTION 'injected failure (REL-03)'; END; $$;"
            "CREATE TRIGGER fail_audit BEFORE INSERT ON audit_log FOR EACH ROW EXECUTE FUNCTION fail_audit();"
        )
    no_raise = TestClient(app, raise_server_exceptions=False)
    r = no_raise.post("/api/orders", json={"items": [{"product_id": p1.id, "quantity": quantity}]}, headers=ana.headers)
    assert r.status_code >= 500  # the injected fault is a server fault
    assert "injected failure" not in r.text  # no internal detail leaks
    assert state(p1.id) == (0, 0, 10)  # no order, no line, stock untouched


@pytest.mark.req("QR-RE-02", "BR-01")
@pytest.mark.parametrize("stock", [pytest.param(2, id="REL-04")])
def test_same_order_submitted_twice_at_once_never_oversells(make, monkeypatch, stock):
    ana, p5 = make.user(), make.product(1_000, stock)
    meet = threading.Barrier(2)
    real_check = orders_service.check_stock

    def check_after_meeting(wanted, available):
        try:
            meet.wait(timeout=2)  # both submissions read the stock before writing, unless the lock serialises them
        except threading.BrokenBarrierError:
            pass
        return real_check(wanted, available)

    monkeypatch.setattr(orders_service, "check_stock", check_after_meeting)
    codes: list[int] = []

    def submit():
        with TestClient(app) as c:  # the same customer, the same body, twice (double click, retry)
            codes.append(
                c.post("/api/orders", json={"items": [{"product_id": p5.id, "quantity": 2}]}, headers=ana.headers).status_code
            )

    threads = [threading.Thread(target=submit) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert sorted(codes) == [201, 409]
    assert state(p5.id) == (1, 1, 0)  # one order, stock exactly 0, never negative


@pytest.mark.req("QR-RE-01")
@pytest.mark.parametrize("route", [pytest.param("/api/products", id="REL-01-503-contract")])
def test_database_outage_answers_503_not_500(monkeypatch, route):
    """While PostgreSQL is unreachable, the API answers 503 DATABASE_UNAVAILABLE with Retry-After (REL-01 runs it for real)."""
    from app.services import search

    def unreachable(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(search, "search_products", unreachable)
    r = TestClient(app, raise_server_exceptions=False).get(route)
    assert r.status_code == 503
    assert r.json()["detail"]["code"] == "DATABASE_UNAVAILABLE"
    assert r.headers["retry-after"] == "5"
