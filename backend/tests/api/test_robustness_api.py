"""Robustness regression tests for the defects Schemathesis found (docs/anomalies.md ANO-01 to ANO-04).

Cases TA-32 to TA-35 of docs/cahier-de-test.md. Rule: a malformed or out-of-range input is refused precisely
(4xx), never a 500 (fiche 2, robustesse; QR-CO-02).
"""

import pytest

from app.core.security import create_access_token

ADMIN_ID = 2  # admin@example.com, seeded by migration 003


def admin():
    return {"Authorization": f"Bearer {create_access_token(ADMIN_ID)}"}


@pytest.mark.req("QR-CO-02")
@pytest.mark.parametrize(
    ("method", "url", "body"),
    [
        pytest.param("GET", "/api/products/9223372036854775808", None, id="TA-32-path-above-bigint"),
        pytest.param("GET", "/api/orders/9007199254740992", None, id="TA-32-path-above-max-id"),
        pytest.param("GET", "/api/products?category_id=9223372036854775808", None, id="TA-32-query"),
        pytest.param("GET", "/api/audit?offset=9223372036854775808", None, id="TA-32-offset"),
        pytest.param("POST", "/api/orders", {"items": [{"product_id": 2**63, "quantity": 1}]}, id="TA-32-body"),
    ],
)
def test_out_of_range_numbers_are_422_not_500(client, make, method, url, body):
    headers = make.user().headers if url == "/api/orders" else admin()  # only a CUSTOMER may post an order
    r = client.request(method, url, json=body, headers=headers)
    assert r.status_code == 422


@pytest.mark.req("QR-CO-02", "FR-01")
@pytest.mark.parametrize(
    ("url", "kwargs"),
    [
        pytest.param("/api/auth/login", {"data": {"username": "a\x00b", "password": "x"}}, id="TA-33-login"),
        pytest.param("/api/auth/register", {"json": {"email": "a\x00@b.fr", "password": "8chars!!"}}, id="TA-33-register"),
        pytest.param("/api/categories", {"json": {"name": "a\x00b"}}, id="TA-33-category"),
    ],
)
def test_nul_character_is_422_not_500(client, url, kwargs):
    r = client.post(url, headers=admin(), **kwargs)
    assert r.status_code == 422


@pytest.mark.req("QR-CO-02", "FR-04", "FR-09")
@pytest.mark.parametrize(
    ("stock", "expected"),
    [
        pytest.param(False, 422, id="TA-34-bool"),
        pytest.param("5", 422, id="TA-34-string"),
        pytest.param(5.0, 201, id="TA-34-integral-float"),
    ],
)
def test_json_integer_types(client, make, stock, expected):
    cat = make.category()
    payload = {
        "sku": f"TYPE-{expected}-{type(stock).__name__}",
        "name": "n",
        "price_cents": 100,
        "stock": stock,
        "category_id": cat.id,
    }
    r = client.post("/api/products", json=payload, headers=admin())
    assert r.status_code == expected
    if expected == 201:
        assert r.json()["stock"] == 5


@pytest.mark.req("QR-CO-02", "FR-09")
@pytest.mark.parametrize("value", [pytest.param("0", id="TA-34-date-number"), pytest.param("20261120", id="TA-34-date-compact")])
def test_dashboard_dates_must_be_iso(client, value):
    assert client.get(f"/api/dashboard?date_to={value}", headers=admin()).status_code == 422
    assert client.get("/api/dashboard?date_to=2026-11-20", headers=admin()).status_code == 200


@pytest.mark.req("QR-CO-02")
@pytest.mark.parametrize(
    ("path", "allowed"),
    [
        pytest.param("/api/categories", {"GET", "POST"}, id="TA-35-collection"),
        pytest.param("/api/products/1", {"GET", "PUT", "DELETE"}, id="TA-35-item"),
        pytest.param("/api/audit/1", {"GET"}, id="TA-35-audit"),
    ],
)
def test_405_lists_every_allowed_method(client, path, allowed):
    r = client.request("PATCH", path, headers=admin())
    assert r.status_code == 405
    assert {m.strip() for m in r.headers["allow"].split(",")} == allowed
