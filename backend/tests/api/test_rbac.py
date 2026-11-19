"""TA-20: the full permissions matrix of docs/rbac.yaml, one test per route x role (FR-02, QR-SE-02).

For every pair the request is valid and targets an existing resource the role could legitimately reach (its own
order for a CUSTOMER), so the only thing that changes the answer is the role.
"""

from pathlib import Path

import pytest
import yaml

from app.core.security import create_access_token
from tests.db_fixtures import PASSWORD

MATRIX = yaml.safe_load((Path(__file__).resolve().parents[3] / "docs" / "rbac.yaml").read_text(encoding="utf-8"))
CASES = [
    pytest.param(route["method"], route["path"], role, code, id=f"TA-20 {role} {route['method']} {route['path']}")
    for route in MATRIX["routes"]
    for role, code in route["expected"].items()
]


@pytest.fixture
def world(make):
    """One user per role, the customer's own PLACED order, an empty category, an unused product, a target user."""
    actors = {role: make.user(role) for role in ("CUSTOMER", "STAFF", "ADMIN")}
    category, empty = make.category("RBAC"), make.category("RBAC empty")
    product, unused = make.product(1_000, 50, category=category), make.product(1_000, 5, category=category)
    order = make.order(actors["CUSTOMER"], [(product, 1)])
    target = make.user("CUSTOMER")
    make.db.commit()
    return {
        "actors": actors,
        "category": category,
        "empty": empty,
        "product": product,
        "unused": unused,
        "order": order,
        "target": target,
    }


def build_request(method: str, path: str, role: str, w) -> tuple[str, dict]:
    """Concrete URL and body for a matrix row."""
    ids = {
        "/api/categories/{id}": w["empty"].id,
        "/api/products/{id}": w["unused"].id,
        "/api/orders/{id}": w["order"].id,
        "/api/orders/{id}/cancel": w["order"].id,
        "/api/orders/{id}/status": w["order"].id,
        "/api/users/{id}/role": w["target"].id,
        "/api/users/{id}/deactivate": w["target"].id,
    }
    url = path.replace("{id}", str(ids.get(path, 1)))  # audit entry 1 = ORDER_CREATED of `order`
    kwargs: dict = {}
    key = f"{method} {path}"
    if key == "POST /api/auth/register":
        kwargs["json"] = {"email": f"new-{role.lower()}@test.example", "password": "8chars!!"}
    elif key == "POST /api/auth/login":
        email = "demo@example.com" if role == "ANONYMOUS" else w["actors"][role].user.email
        kwargs["data"] = {"username": email, "password": "demo1234" if role == "ANONYMOUS" else PASSWORD}
    elif key in ("POST /api/categories", "PUT /api/categories/{id}"):
        kwargs["json"] = {"name": f"New {role}"}
    elif key in ("POST /api/products", "PUT /api/products/{id}"):
        kwargs["json"] = {
            "sku": f"NEW-{role}",
            "name": "New",
            "description": "",
            "price_cents": 100,
            "stock": 1,
            "category_id": w["category"].id,
        }
    elif key == "POST /api/orders":
        kwargs["json"] = {"items": [{"product_id": w["product"].id, "quantity": 1}]}
    elif key == "PATCH /api/orders/{id}/status":
        kwargs["json"] = {"status": "PAID"}
    elif key == "PATCH /api/users/{id}/role":
        kwargs["json"] = {"role": "STAFF"}
    elif key in ("PUT /api/audit/{id}", "DELETE /api/audit/{id}"):
        kwargs["json"] = {}
    return url, kwargs


@pytest.mark.req("FR-02", "QR-SE-02")
@pytest.mark.parametrize(("method", "path", "role", "expected"), CASES)
def test_permissions_matrix(client, world, method, path, role, expected):
    url, kwargs = build_request(method, path, role, world)
    headers = {} if role == "ANONYMOUS" else {"Authorization": f"Bearer {create_access_token(world['actors'][role].id)}"}
    r = client.request(method, url, headers=headers, **kwargs)
    assert r.status_code == expected, r.text
