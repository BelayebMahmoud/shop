"""Disposable PostgreSQL test database (shop_test), rebuilt from db/migrations before every test.

The environment (DATABASE_URL, JWT_SECRET) is set by tests/conftest.py before anything imports the app.
004_volume_seed.sql (50,000 products) is skipped: these tests need small, controlled data.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url, text

VOLUME_SEED = "004_volume_seed.sql"
MIGRATIONS = [f for f in sorted((Path(__file__).resolve().parents[3] / "db" / "migrations").glob("*.sql")) if f.name != VOLUME_SEED]


def _ensure_database(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": target.database})
        if not exists:
            conn.exec_driver_sql(f'CREATE DATABASE "{target.database}"')
    admin.dispose()


_ensure_database(os.environ["DATABASE_URL"])

from app.core.db import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    """Rebuild the schema from the same SQL files Postgres runs on first start."""
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for f in MIGRATIONS:
            conn.exec_driver_sql(f.read_text(encoding="utf-8"))
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    r = client.post("/api/auth/login", data={"username": "demo@example.com", "password": "demo1234"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
