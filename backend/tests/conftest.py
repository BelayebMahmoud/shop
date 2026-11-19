import os
from pathlib import Path

os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://shop:shop@localhost:5433/shop_test")
os.environ.setdefault("JWT_SECRET", "test-only-secret-0123456789abcdef0123456789")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, make_url, text  # noqa: E402

MIGRATIONS = sorted((Path(__file__).resolve().parents[2] / "db" / "migrations").glob("*.sql"))


def _ensure_database(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": target.database})
        if not exists:
            conn.exec_driver_sql(f'CREATE DATABASE "{target.database}"')
    admin.dispose()


_ensure_database(os.environ["DATABASE_URL"])

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    """Rebuild the schema from the same SQL files Postgres runs on first start."""
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for f in MIGRATIONS:
            conn.exec_driver_sql(f.read_text())
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    r = client.post("/api/auth/login", data={"username": "demo@example.com", "password": "demo1234"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
