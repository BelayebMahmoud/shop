"""Accounts, administration, dashboard and audit API tests.

Cases TA-01, TA-02, TA-10, TA-17, TA-21 to TA-24, TA-31 of docs/cahier-de-test.md.
"""

import pytest
from sqlalchemy import func, select

from app.core.db import SessionLocal
from app.models import AuditLog, User
from tests.datasets import ct50_dataset
from tests.db_fixtures import PASSWORD


def login(client, email: str, password: str):
    return client.post("/api/auth/login", data={"username": email, "password": password})


def audit_count(action: str) -> int:
    with SessionLocal() as s:
        return s.scalar(select(func.count()).where(AuditLog.action == action))


@pytest.mark.req("FR-01")
@pytest.mark.parametrize("email", [pytest.param("Ana@Example.COM", id="TA-01")])
def test_register_then_login(client, email):
    r = client.post("/api/auth/register", json={"email": email, "password": "8chars!!"})
    assert r.status_code == 201
    assert (r.json()["email"], r.json()["role"]) == ("ana@example.com", "CUSTOMER")
    token = login(client, email, "8chars!!")
    assert token.status_code == 200 and token.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token.json()['access_token']}"})
    assert me.status_code == 200 and me.json()["email"] == "ana@example.com"
    with SessionLocal() as s:
        assert s.scalar(select(User.email).where(User.id == r.json()["id"])) == "ana@example.com"


@pytest.mark.req("FR-01", "FR-11")
@pytest.mark.parametrize("password", [pytest.param("wrong-password", id="TA-02")])
def test_wrong_password(client, make, password):
    ana = make.user(email="ana@example.com")
    r = login(client, ana.user.email, password)
    assert r.status_code == 401
    assert "access_token" not in r.json()
    assert audit_count("LOGIN_FAILURE") == 1


@pytest.mark.req("BR-07")
@pytest.mark.parametrize("other_case", [pytest.param("ANA@Example.com", id="TA-10")])
def test_duplicate_email_other_case(client, other_case):
    assert client.post("/api/auth/register", json={"email": "ana@example.com", "password": "8chars!!"}).status_code == 201
    r = client.post("/api/auth/register", json={"email": other_case, "password": "8chars!!"})
    assert r.status_code == 409 and r.json()["detail"]["code"] == "DUPLICATE"
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).where(func.lower(User.email) == "ana@example.com")) == 1


@pytest.mark.req("FR-09")
@pytest.mark.parametrize("dataset", [pytest.param("IT-11", id="TA-17")])
def test_dashboard_rights_and_values(client, make, dataset):
    p = ct50_dataset(make)
    sam, ana = make.user("STAFF"), make.user()
    r = client.get("/api/dashboard", headers=sam.headers)
    assert r.status_code == 200
    d = r.json()
    assert d["revenue_cents"] == 16_400
    assert d["orders_by_status"] == {"PLACED": 1, "PAID": 1, "SHIPPED": 1, "DELIVERED": 1, "CANCELLED": 1}
    assert p["low"].id in [x["id"] for x in d["low_stock"]]
    assert client.get("/api/dashboard", headers=ana.headers).status_code == 403


@pytest.mark.req("FR-05", "FR-11", "BR-11")
@pytest.mark.parametrize("new_role", [pytest.param("STAFF", id="TA-21")])
def test_admin_changes_roles(client, make, new_role):
    alice, bob, zoe = make.user("ADMIN"), make.user(), make.user("ADMIN")
    r = client.patch(f"/api/users/{bob.id}/role", json={"role": new_role}, headers=alice.headers)
    assert r.status_code == 200 and r.json()["role"] == "STAFF"
    assert client.get("/api/dashboard", headers=bob.headers).status_code == 200  # role read from the database
    assert audit_count("ROLE_CHANGED") == 1
    # SC-BR-11-1: with two active ADMINs, one may be demoted
    assert client.patch(f"/api/users/{zoe.id}/role", json={"role": "STAFF"}, headers=alice.headers).status_code == 200


@pytest.mark.req("FR-05")
@pytest.mark.parametrize("target", [pytest.param("bob", id="TA-22")])
def test_deactivated_account(client, make, target):
    alice, bob = make.user("ADMIN"), make.user()
    assert client.patch(f"/api/users/{bob.id}/deactivate", headers=alice.headers).status_code == 200
    assert login(client, bob.user.email, PASSWORD).status_code == 401
    assert client.get("/api/auth/me", headers=bob.headers).status_code == 401  # token issued before (Q-08)


@pytest.mark.req("FR-11")
@pytest.mark.parametrize("method", [pytest.param("PUT", id="TA-23-put"), pytest.param("DELETE", id="TA-23-delete")])
def test_audit_log_cannot_be_changed(client, make, method):
    alice = make.user("ADMIN")
    login(client, "demo@example.com", "demo1234")  # creates an audit entry
    entries = client.get("/api/audit", headers=alice.headers).json()
    r = client.request(method, f"/api/audit/{entries[0]['id']}", json={}, headers=alice.headers)
    assert r.status_code == 405
    assert client.get("/api/audit", headers=alice.headers).json() == entries


@pytest.mark.req("FR-11")
@pytest.mark.parametrize("reader", [pytest.param("admin-and-staff", id="TA-24")])
def test_audit_log_reading_rights(client, make, reader):
    alice, sam = make.user("ADMIN"), make.user("STAFF")
    login(client, "demo@example.com", "demo1234")
    r = client.get("/api/audit", headers=alice.headers)
    assert r.status_code == 200 and r.json()[0]["action"] == "LOGIN_SUCCESS"
    assert client.get("/api/audit", headers=sam.headers).status_code == 403  # decision Q-11


@pytest.mark.req("BR-11")
@pytest.mark.parametrize("admin", [pytest.param("admin@example.com", id="TA-31")])
def test_last_admin_cannot_disappear(client, admin):
    token = login(client, admin, "admin1234").json()["access_token"]  # the only ADMIN seeded by migration 003
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/auth/me", headers=headers).json()
    r1 = client.patch(f"/api/users/{me['id']}/role", json={"role": "CUSTOMER"}, headers=headers)
    r2 = client.patch(f"/api/users/{me['id']}/deactivate", headers=headers)
    assert (r1.status_code, r2.status_code) == (409, 409)
    assert r1.json()["detail"]["code"] == r2.json()["detail"]["code"] == "LAST_ADMIN"
    after = client.get("/api/auth/me", headers=headers).json()
    assert (after["role"], after["is_active"]) == ("ADMIN", True)
