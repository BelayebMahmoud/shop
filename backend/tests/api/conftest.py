"""API suite: every test runs on a freshly rebuilt shop_test database (fixtures in tests/db_fixtures.py)."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_database(fresh_db):
    yield


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    """Seeded demo customer, logged in through the real login route (used by the MVP regression tests)."""
    r = client.post("/api/auth/login", data={"username": "demo@example.com", "password": "demo1234"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
