"""Catalogue API tests: lifecycles, uniqueness, protected deletions, search on 50,000 rows.

Cases TA-08, TA-09, TA-11, TA-12, TA-18, TA-19, TA-27, TA-30 of docs/cahier-de-test.md.
"""

import pytest
from sqlalchemy import func, select, text

from app.core.db import SessionLocal
from app.models import Category, Order, Product


def product_payload(category_id: int, **over):
    return {
        "sku": "LIFE-1",
        "name": "Lifecycle",
        "description": "",
        "price_cents": 4_000,
        "stock": 5,
        "category_id": category_id,
    } | over


@pytest.mark.req("FR-03", "BR-09")
@pytest.mark.parametrize("name", [pytest.param("Test", id="TA-08")])
def test_category_lifecycle(client, make, name):
    sam = make.user("STAFF")
    r = client.post("/api/categories", json={"name": name}, headers=sam.headers)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.get(f"/api/categories/{cid}").status_code == 200
    r = client.put(f"/api/categories/{cid}", json={"name": "Test renamed"}, headers=sam.headers)
    assert r.status_code == 200 and r.json()["name"] == "Test renamed"
    assert client.delete(f"/api/categories/{cid}", headers=sam.headers).status_code == 204
    assert client.get(f"/api/categories/{cid}").status_code == 404


@pytest.mark.req("FR-04", "BR-10")
@pytest.mark.parametrize("new_price", [pytest.param(4_200, id="TA-09")])
def test_product_lifecycle(client, make, new_price):
    sam, cat = make.user("STAFF"), make.category()
    r = client.post("/api/products", json=product_payload(cat.id), headers=sam.headers)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert client.get(f"/api/products/{pid}").status_code == 200
    r = client.put(f"/api/products/{pid}", json=product_payload(cat.id, price_cents=new_price), headers=sam.headers)
    assert r.status_code == 200
    assert client.get(f"/api/products/{pid}").json()["price_cents"] == 4_200
    assert client.delete(f"/api/products/{pid}", headers=sam.headers).status_code == 204  # never ordered (SC-BR-10-1)
    assert client.get(f"/api/products/{pid}").status_code == 404


@pytest.mark.req("BR-07")
@pytest.mark.parametrize("sku", [pytest.param("p1-test", id="TA-11")])
def test_duplicate_sku_any_case(client, make, sku):
    sam = make.user("STAFF")
    p1 = make.product(4_000, 10, sku="P1-TEST")
    r = client.post("/api/products", json=product_payload(p1.category_id, sku=sku), headers=sam.headers)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "DUPLICATE"
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).where(func.lower(Product.sku) == "p1-test")) == 1


@pytest.mark.req("BR-07")
@pytest.mark.parametrize("name", [pytest.param("papeterie", id="TA-12")])
def test_duplicate_category_name_any_case(client, make, name):
    sam = make.user("STAFF")  # « Papeterie » is seeded by migration 003
    r = client.post("/api/categories", json={"name": name}, headers=sam.headers)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "DUPLICATE"
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).where(func.lower(Category.name) == "papeterie")) == 1


@pytest.mark.req("BR-09")
@pytest.mark.parametrize("category", [pytest.param("Papeterie", id="TA-27")])
def test_delete_non_empty_category(client, make, category):
    sam = make.user("STAFF")
    cat = make.category("Papeterie test")
    p1 = make.product(4_000, 10, category=cat)
    r = client.delete(f"/api/categories/{cat.id}", headers=sam.headers)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "CATEGORY_NOT_EMPTY"
    with SessionLocal() as s:
        assert s.get(Category, cat.id) is not None and s.get(Product, p1.id) is not None


@pytest.mark.req("BR-10")
@pytest.mark.parametrize("quantity", [pytest.param(1, id="TA-30")])
def test_delete_product_already_ordered(client, make, quantity):
    ana, sam, p1 = make.user(), make.user("STAFF"), make.product(4_000, 10)
    order = make.order(ana, [(p1, quantity)])
    r = client.delete(f"/api/products/{p1.id}", headers=sam.headers)
    assert r.status_code == 409 and r.json()["detail"]["code"] == "PRODUCT_IN_USE"
    with SessionLocal() as s:
        assert s.get(Product, p1.id) is not None
        kept = s.get(Order, order.id)
        assert (kept.status, kept.total_cents, len(kept.items)) == ("PLACED", 4_000, 1)


# ---------------------------------------------------------------- search (FR-10)
SEARCH_SQL = text(
    """SELECT count(*) FROM products
       WHERE lower(name) LIKE '%mug%' AND category_id = :cat AND price_cents BETWEEN 1000 AND 2000 AND stock > 0"""
)


@pytest.mark.req("FR-10")
@pytest.mark.parametrize("q", [pytest.param("mug", id="TA-18")])
def test_filtered_search_on_50000_products(client, volume_db, q):
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).select_from(Product)) >= 50_000
        kitchen = s.scalar(select(Category.id).where(Category.name == "Cuisine"))
        expected_total = s.scalar(SEARCH_SQL, {"cat": kitchen})  # control query written from the rule
    params = {"q": q, "category_id": kitchen, "min_price_cents": 1_000, "max_price_cents": 2_000, "in_stock": "true", "limit": 100}
    r = client.get("/api/products", params=params)
    assert r.status_code == 200
    page = r.json()
    assert page["total"] == expected_total > 0
    assert 0 < len(page["items"]) <= 100
    for p in page["items"]:
        assert "mug" in p["name"].lower() and p["category_id"] == kitchen
        assert 1_000 <= p["price_cents"] <= 2_000 and p["stock"] > 0


@pytest.mark.req("FR-10")
@pytest.mark.parametrize(
    "query",
    [
        pytest.param("limit=0", id="TA-19-limit0"),
        pytest.param("limit=101", id="TA-19-limit101"),
        pytest.param("min_price_cents=a", id="TA-19-price-text"),
    ],
)
def test_invalid_search_parameters_never_500(client, query):
    r = client.get(f"/api/products?{query}")
    assert r.status_code == 422
