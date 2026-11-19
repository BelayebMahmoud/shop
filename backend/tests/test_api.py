from sqlalchemy import text

from app.db import engine


def stock_of(product_id: int) -> int:
    with engine.connect() as conn:
        return conn.scalar(text("SELECT stock FROM products WHERE id = :id"), {"id": product_id})


def test_list_and_search_products(client):
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json()["total"] == 8
    r = client.get("/api/products", params={"q": "mug"})
    assert [p["sku"] for p in r.json()["items"]] == ["MUG-001"]


def test_product_detail_and_404(client):
    assert client.get("/api/products/1").json()["name"] == "Ceramic Mug"
    assert client.get("/api/products/9999").status_code == 404


def test_register_login_me(client):
    r = client.post("/api/auth/register", json={"email": "Ana@Example.com", "password": "s3cret-pass"})
    assert r.status_code == 201 and r.json()["email"] == "ana@example.com"
    assert client.post("/api/auth/register", json={"email": "ana@example.com", "password": "s3cret-pass"}).status_code == 409
    token = client.post("/api/auth/login", data={"username": "ana@example.com", "password": "s3cret-pass"}).json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "ana@example.com"


def test_login_rejects_wrong_password(client):
    r = client.post("/api/auth/login", data={"username": "demo@example.com", "password": "wrong-pass"})
    assert r.status_code == 401


def test_checkout_requires_token(client):
    r = client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 1}]})
    assert r.status_code == 401
    r = client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 1}]},
                    headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401


def test_checkout_prices_on_server_and_decrements_stock(client, auth_headers):
    before = stock_of(1)
    body = {"items": [{"product_id": 1, "quantity": 2}, {"product_id": 4, "quantity": 1}, {"product_id": 1, "quantity": 1}]}
    r = client.post("/api/orders", json=body, headers=auth_headers)
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["total_cents"] == 3 * 1200 + 900
    assert {i["product_id"]: i["quantity"] for i in order["items"]} == {1: 3, 4: 1}
    assert stock_of(1) == before - 3
    assert [o["id"] for o in client.get("/api/orders", headers=auth_headers).json()] == [order["id"]]


def test_out_of_stock_changes_nothing(client, auth_headers):
    r = client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 1}, {"product_id": 8, "quantity": 4}]},
                    headers=auth_headers)
    assert r.status_code == 409
    assert r.json()["detail"] == {"code": "OUT_OF_STOCK", "product_ids": [8]}
    assert stock_of(1) == 50 and stock_of(8) == 3
    assert client.get("/api/orders", headers=auth_headers).json() == []


def test_order_validation(client, auth_headers):
    assert client.post("/api/orders", json={"items": []}, headers=auth_headers).status_code == 422
    assert client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 0}]}, headers=auth_headers).status_code == 422
    r = client.post("/api/orders", json={"items": [{"product_id": 999, "quantity": 1}]}, headers=auth_headers)
    assert r.status_code == 404
