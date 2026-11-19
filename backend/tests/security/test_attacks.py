"""Fiche 4 manual attacks, automated: SEC-01 injection, SEC-03 access control, SEC-04 session (SEC-02 XSS is in
web/e2e/securite.spec.ts because it needs a browser). Expected behaviour = the safe one (TP3 §3.2).
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import Order, Product


@pytest.fixture(autouse=True)
def _isolated_database(fresh_db):
    yield


def product_count() -> int:
    with SessionLocal() as s:
        return s.scalar(select(func.count()).select_from(Product))


@pytest.mark.req("QR-SE-02", "FR-10")
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("' OR 1=1 --", id="SEC-01-or-true"),
        pytest.param("'; DROP TABLE products; --", id="SEC-01-drop"),
        pytest.param("%' UNION SELECT email, password_hash FROM users --", id="SEC-01-union"),
    ],
)
def test_sql_injection_in_search_is_plain_text(client, payload):
    before = product_count()
    r = client.get("/api/products", params={"q": payload})
    assert r.status_code == 200
    assert r.json()["total"] == 0  # no product name contains this text: it was not interpreted as SQL
    assert product_count() == before  # table intact
    assert "password_hash" not in r.text and "$argon2" not in r.text


@pytest.mark.req("QR-SE-02", "BR-08", "FR-02")
@pytest.mark.parametrize("action", [pytest.param("read", id="SEC-03-read"), pytest.param("cancel", id="SEC-03-cancel")])
def test_access_control_with_another_customers_order_id(client, make, action):
    ana, bob, p1 = make.user(), make.user(), make.product(4_000, 10)
    orders = [make.order(ana, [(p1, 1)]) for _ in range(3)]
    for order in orders:  # Bob walks through Ana's order numbers
        if action == "read":
            r = client.get(f"/api/orders/{order.id}", headers=bob.headers)
        else:
            r = client.post(f"/api/orders/{order.id}/cancel", headers=bob.headers)
        assert r.status_code == 404
    with SessionLocal() as s:
        assert {o.status for o in s.scalars(select(Order)).all()} == {"PLACED"}


@pytest.mark.req("QR-SE-02", "FR-01")
@pytest.mark.parametrize("minutes_ago", [pytest.param(1, id="SEC-04-expired")])
def test_expired_session_requires_new_login(client, make, minutes_ago):
    sam = make.user("STAFF")
    past = datetime.now(UTC) - timedelta(minutes=settings.jwt_expire_minutes + minutes_ago)
    token = jwt.encode(
        {"sub": str(sam.id), "iat": past, "exp": past + timedelta(minutes=settings.jwt_expire_minutes)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


@pytest.mark.req("QR-SE-02", "FR-05")
@pytest.mark.parametrize("new_role", [pytest.param("CUSTOMER", id="SEC-04-role-change")])
def test_token_issued_before_a_role_change_carries_the_new_role(client, make, new_role):
    alice, bob = make.user("ADMIN"), make.user("STAFF")
    assert client.get("/api/dashboard", headers=bob.headers).status_code == 200
    assert client.patch(f"/api/users/{bob.id}/role", json={"role": new_role}, headers=alice.headers).status_code == 200
    assert client.get("/api/dashboard", headers=bob.headers).status_code == 403  # same token, current role applies
