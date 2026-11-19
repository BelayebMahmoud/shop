"""Integration tests IT-01 to IT-14 (docs/cahier-de-test.md §2): one success and one error per interface of
docs/conception.md §4, on the real PostgreSQL test database. Expected values come from the cahier.
"""

from datetime import UTC, date, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.models import AuditLog, Order, OrderItem, Product
from app.services import audit, catalog, dashboard, orders, search
from app.services.catalog import ProductData
from app.services.errors import Conflict, InvalidInput
from app.services.order_rules import Line
from tests.datasets import ct50_dataset


def count(model) -> int:
    with SessionLocal() as s:
        return s.scalar(select(func.count()).select_from(model))


def stock_of(product_id: int) -> int:
    with SessionLocal() as s:
        return s.get(Product, product_id).stock


# ---------------------------------------------------------------- I-1 routes -> security
@pytest.mark.req("FR-01")
@pytest.mark.parametrize("role", [pytest.param("STAFF", id="IT-01")])
def test_valid_token_identifies_user_and_role(make, db, role):
    sam = make.user(role)
    user = get_current_user(token=create_access_token(sam.id), db=db)
    assert (user.id, user.role) == (sam.id, "STAFF")


@pytest.mark.req("FR-01")
@pytest.mark.parametrize("kind", [pytest.param("expired", id="IT-02-expired"), pytest.param("forged", id="IT-02-forged")])
def test_expired_or_forged_token_is_refused(make, db, kind):
    sam = make.user("STAFF")
    past = datetime.now(UTC) - timedelta(minutes=1)
    key = settings.jwt_secret if kind == "expired" else "another-key-0123456789abcdef0123456789"
    exp = past if kind == "expired" else past + timedelta(hours=1)
    token = jwt.encode({"sub": str(sam.id), "exp": exp}, key, algorithm=settings.jwt_algorithm)
    with pytest.raises(HTTPException) as err:
        get_current_user(token=token, db=db)
    assert err.value.status_code == 401


# ---------------------------------------------------------------- I-2 orders -> catalogue (stock, lock)
@pytest.mark.req("BR-01")
@pytest.mark.parametrize("quantity", [pytest.param(3, id="IT-03")])
def test_order_decrements_stock_in_database(make, quantity):
    ana, p1 = make.user(), make.product(4_000, 10)
    orders.place_order(make.db, ana.user, [Line(p1.id, quantity)])
    assert stock_of(p1.id) == 7
    assert (count(Order), count(OrderItem)) == (1, 1)


@pytest.mark.req("BR-01", "QR-RE-02")
@pytest.mark.parametrize("quantity", [pytest.param(3, id="IT-04")])
def test_failure_on_second_write_writes_nothing(make, monkeypatch, quantity):
    ana, p1 = make.user(), make.product(4_000, 10)

    def failing_write(*args, **kwargs):  # stub: the audit write (after order, lines and stock) fails
        raise RuntimeError("stub: second write fails")

    monkeypatch.setattr(audit, "record", failing_write)
    with pytest.raises(RuntimeError):  # the error reaches the caller
        orders.place_order(make.db, ana.user, [Line(p1.id, quantity)])
    make.db.rollback()
    assert count(Order) == 0
    assert stock_of(p1.id) == 10


# ---------------------------------------------------------------- I-3 orders -> pricing
@pytest.mark.req("BR-02")
@pytest.mark.parametrize("new_price", [pytest.param(4_500, id="IT-05")])
def test_price_comes_from_catalogue_and_is_frozen(make, new_price):
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(4_000, 10)
    order = orders.place_order(make.db, ana.user, [Line(p1.id, 1)])
    data = ProductData(p1.sku, p1.name, "", new_price, p1.stock, p1.category_id)
    catalog.update_product(make.db, sam.user, p1.id, data)
    with SessionLocal() as s:
        assert s.get(Order, order.id).items[0].unit_price_cents == 4_000


@pytest.mark.req("BR-04")
@pytest.mark.parametrize("lines", [pytest.param([(2, "P3"), (1, "P4")], id="IT-06")])
def test_data_flow_subtotal_discount_total_stock_rows(make, lines):
    ana = make.user()
    p = {"P3": make.product(7_500, 5), "P4": make.product(5_000, 5)}
    order = orders.place_order(make.db, ana.user, [Line(p[name].id, q) for q, name in lines])
    assert (order.subtotal_cents, order.discount_cents, order.total_cents) == (20_000, 2_000, 18_000)
    assert (stock_of(p["P3"].id), stock_of(p["P4"].id)) == (3, 4)
    with SessionLocal() as s:
        rows = s.execute(select(OrderItem.product_id, OrderItem.unit_price_cents).where(OrderItem.order_id == order.id))
        assert dict(rows.all()) == {p["P3"].id: 7_500, p["P4"].id: 5_000}


# ---------------------------------------------------------------- I-4 workflow -> stock
@pytest.mark.req("BR-06", "FR-08")
@pytest.mark.parametrize("actor", [pytest.param("owner", id="IT-07")])
def test_cancel_restocks_in_database(make, actor):
    ana, p1, p2 = make.user(), make.product(4_000, 10), make.product(5_000, 3)
    order = make.order(ana, [(p1, 2), (p2, 1)])
    assert (stock_of(p1.id), stock_of(p2.id)) == (8, 2)
    result = orders.change_status(make.db, ana.user, order.id, "CANCELLED")
    assert result.status == "CANCELLED"
    assert (stock_of(p1.id), stock_of(p2.id)) == (10, 3)


@pytest.mark.req("BR-06")
@pytest.mark.parametrize("status", [pytest.param("SHIPPED", id="IT-08")])
def test_cancel_after_shipping_leaves_database_unchanged(make, status):
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(4_000, 10)
    order = make.order(ana, [(p1, 2)], status=status)
    with pytest.raises(Conflict) as err:
        orders.change_status(make.db, sam.user, order.id, "CANCELLED")
    assert err.value.code == "INVALID_TRANSITION"
    make.db.rollback()
    with SessionLocal() as s:
        assert s.get(Order, order.id).status == "SHIPPED"
    assert stock_of(p1.id) == 8


# ---------------------------------------------------------------- I-5 services -> audit
@pytest.mark.req("FR-11")
@pytest.mark.parametrize("action", [pytest.param("ORDER_CREATED", id="IT-09")])
def test_action_and_audit_are_written_together(make, action):
    ana, p1 = make.user(), make.product(4_000, 10)
    order = orders.place_order(make.db, ana.user, [Line(p1.id, 1)])
    with SessionLocal() as s:
        entries = s.scalars(select(AuditLog).where(AuditLog.action == action)).all()
    assert len(entries) == 1
    assert (entries[0].actor_id, entries[0].entity_id) == (ana.id, order.id)
    assert entries[0].created_at is not None


@pytest.mark.req("FR-11")
@pytest.mark.parametrize("quantity", [pytest.param(4, id="IT-10")])
def test_failed_action_leaves_no_audit_entry(make, quantity):
    ana, p2 = make.user(), make.product(5_000, 3)
    with pytest.raises(Conflict) as err:
        orders.place_order(make.db, ana.user, [Line(p2.id, quantity)])
    assert err.value.code == "OUT_OF_STOCK"
    make.db.rollback()
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).where(AuditLog.action == "ORDER_CREATED")) == 0


# ---------------------------------------------------------------- I-6 dashboard -> database
@pytest.mark.req("FR-09")
@pytest.mark.parametrize("filters", [pytest.param({}, id="IT-11")])
def test_dashboard_indicators_on_controlled_data(make, filters):
    p = ct50_dataset(make)
    d = dashboard.compute(make.db, None, None, None)
    assert d.orders_by_status == {"PLACED": 1, "PAID": 1, "SHIPPED": 1, "DELIVERED": 1, "CANCELLED": 1}
    assert d.revenue_cents == 16_400  # decision Q-03
    assert p["low"].id in {x.id for x in d.low_stock}
    top = {pid: qty for pid, _, qty in d.top_products}
    assert top == {p["p40"].id: 3, p["p20"].id: 1, p["p30"].id: 1}  # the CANCELLED 2 x p40 is not counted
    assert d.top_products[0][0] == p["p40"].id


@pytest.mark.req("FR-09")
@pytest.mark.parametrize("period", [pytest.param((date(2026, 11, 10), date(2026, 11, 20)), id="IT-12")])
def test_dashboard_period_and_category_filters(make, client, period):
    ana = make.user()
    cat_a, cat_b = make.category("A"), make.category("B")
    pa, pb = make.product(1_000, 50, category=cat_a), make.product(1_000, 50, category=cat_b)
    inside_a = make.order(ana, [(pa, 1)])
    last_second_a = make.order(ana, [(pa, 1)])
    before_a = make.order(ana, [(pa, 1)])
    after_a = make.order(ana, [(pa, 1)])
    inside_b = make.order(ana, [(pb, 1)])
    for order, when in [
        (inside_a, datetime(2026, 11, 15, 12, tzinfo=UTC)),
        (last_second_a, datetime(2026, 11, 20, 23, 59, 59, tzinfo=UTC)),  # inclusive end date (Q-04)
        (before_a, datetime(2026, 11, 1, 12, tzinfo=UTC)),
        (after_a, datetime(2026, 11, 21, 0, 0, 0, tzinfo=UTC)),  # first instant after the end date
        (inside_b, datetime(2026, 11, 15, 12, tzinfo=UTC)),
    ]:
        make.db.execute(update(Order).where(Order.id == order.id).values(created_at=when))
    make.db.commit()
    d = dashboard.compute(make.db, *period, cat_a.id)
    assert d.orders_by_status["PLACED"] == 2  # inside_a and last_second_a only
    with pytest.raises(InvalidInput) as err:  # start after end (Q-04)
        dashboard.compute(make.db, period[1], period[0], None)
    assert err.value.code == "DATE_RANGE"
    sam = make.user("STAFF")
    r = client.get("/api/dashboard?date_from=2026-11-20&date_to=2026-11-10", headers=sam.headers)
    assert r.status_code == 422 and r.json()["detail"]["code"] == "DATE_RANGE"


# ---------------------------------------------------------------- I-7 search -> database
@pytest.mark.req("FR-10")
@pytest.mark.parametrize("q", [pytest.param("mug", id="IT-13")])
def test_combined_search_filters(make, q):
    kitchen, other = make.category("Cuisine test"), make.category("Autre test")
    expected = {
        make.product(1_000, 5, "Mug Alpha", kitchen).id,  # price = min bound (inclusive, Q-05)
        make.product(2_000, 1, "Big MUG", kitchen).id,  # price = max bound, other case
    }
    make.product(1_500, 0, "Mug Zero", kitchen)  # out of stock
    make.product(999, 5, "Mug Cheap", kitchen)  # below min
    make.product(2_001, 5, "Mug Pricey", kitchen)  # above max
    make.product(1_500, 5, "Plate", kitchen)  # text does not match
    make.product(1_500, 5, "Mug Other", other)  # other category
    items, total = search.search_products(make.db, q, kitchen.id, 1_000, 2_000, True, 20, 0)
    assert {p.id for p in items} == expected
    assert total == 2


@pytest.mark.req("FR-10")
@pytest.mark.parametrize(
    "query",
    [
        pytest.param("limit=0", id="IT-14-limit0"),
        pytest.param("limit=101", id="IT-14-limit101"),
        pytest.param("min_price_cents=5&max_price_cents=1", id="IT-14-minmax"),
    ],
)
def test_invalid_search_parameters(client, query):
    r = client.get(f"/api/products?{query}")
    assert r.status_code == 422
