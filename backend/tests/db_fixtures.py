"""Database fixtures shared by the integration and API suites (loaded as a plugin by tests/conftest.py).

Nothing here touches the database at import time, so unit tests still run without one. A suite opts in with an
autouse fixture that requests `fresh_db` (see tests/api/conftest.py and tests/integration/conftest.py).
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, update
from sqlalchemy.orm import Session

from app.api import route_table
from app.core.db import SessionLocal, engine
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import Category, Order, Product, User
from app.services import orders
from app.services.order_rules import Line

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "db" / "migrations"
VOLUME_SEED = "004_volume_seed.sql"
PASSWORD = "test-pass-123"  # every factory user gets this password (development test value only)
_HASH_CACHE: dict[str, str] = {}


def run_sql_file(conn, path: Path) -> None:
    """Run a migration file as-is (no parameter parsing, so `%` stays a SQL operator)."""
    conn.connection.cursor().execute(path.read_text(encoding="utf-8"))


def migration_files(with_volume: bool = False) -> list[Path]:
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return [f for f in files if with_volume or f.name != VOLUME_SEED]


@pytest.fixture(scope="session")
def db_ready() -> None:
    """Create the disposable test database if needed (first DB-backed test only)."""
    target = engine.url
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        if not conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": target.database}):
            conn.exec_driver_sql(f'CREATE DATABASE "{target.database}"')
    admin.dispose()


@pytest.fixture
def fresh_db(db_ready) -> None:
    """Rebuild the schema from the same SQL files Postgres runs on first start (without the volume seed)."""
    engine.dispose()  # drop pooled connections left by a previous test or thread
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for f in migration_files():
            run_sql_file(conn, f)


@pytest.fixture
def volume_db(fresh_db) -> None:
    """Add the 50,000-product volume seed (FR-10 / TA-18)."""
    with engine.begin() as conn:
        run_sql_file(conn, MIGRATIONS_DIR / VOLUME_SEED)


@pytest.fixture
def db(fresh_db) -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


# ---------------------------------------------------------------- HTTP client that records the calls it makes
def route_template(path: str) -> str:
    """Map a concrete path to its route template, e.g. /api/orders/12 -> /api/orders/{order_id}."""
    found = route_table.match(app, path)
    return found[0] if found else path


class RecordingClient(TestClient):
    """TestClient that remembers (method, route template, status) for reports/api-coverage.md."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls: list[str] = []

    def request(self, method, url, *args, **kwargs):
        response = super().request(method, url, *args, **kwargs)
        path = str(url).split("?", 1)[0]
        self.calls.append(f"{method.upper()} {route_template(path)} {response.status_code}")
        return response


@pytest.fixture
def client(request, fresh_db) -> Iterator[RecordingClient]:
    c = RecordingClient(app)
    yield c
    for call in dict.fromkeys(c.calls):  # unique, in order
        request.node.user_properties.append(("http", call))


# ---------------------------------------------------------------- factories (Arrange helpers)
@dataclass
class Actor:
    user: User
    headers: dict[str, str]

    @property
    def id(self) -> int:
        return self.user.id


class Factory:
    def __init__(self, session: Session):
        self.db = session
        self._n = 0

    def _next(self) -> int:
        self._n += 1
        return self._n

    def user(self, role: str = "CUSTOMER", email: str | None = None) -> Actor:
        if PASSWORD not in _HASH_CACHE:
            _HASH_CACHE[PASSWORD] = hash_password(PASSWORD)
        u = User(email=email or f"{role.lower()}{self._next()}@test.example", password_hash=_HASH_CACHE[PASSWORD], role=role)
        self.db.add(u)
        self.db.commit()
        return Actor(u, {"Authorization": f"Bearer {create_access_token(u.id)}"})

    def category(self, name: str | None = None) -> Category:
        c = Category(name=name or f"Cat {self._next()}")
        self.db.add(c)
        self.db.commit()
        return c

    def product(
        self, price_cents: int, stock: int, name: str | None = None, category: Category | None = None, sku: str | None = None
    ) -> Product:
        category = category or self.category()
        n = self._next()
        p = Product(
            sku=sku or f"T-{n:04d}",
            name=name or f"Product {n}",
            description="",
            price_cents=price_cents,
            stock=stock,
            category_id=category.id,
        )
        self.db.add(p)
        self.db.commit()
        return p

    def order(self, customer: Actor, lines: list[tuple[Product, int]], status: str = "PLACED") -> Order:
        """Place an order through the service (stock decremented), then force a starting status if asked."""
        order = orders.place_order(self.db, customer.user, [Line(p.id, q) for p, q in lines])
        if status != "PLACED":
            self.set_status(order, status)
        return order

    def set_status(self, order: Order, status: str) -> None:
        """Arrange only: put an order directly in a given state, bypassing the workflow."""
        self.db.execute(update(Order).where(Order.id == order.id).values(status=status))
        self.db.commit()
        self.db.refresh(order)

    def stock(self, product: Product) -> int:
        self.db.expire_all()
        return self.db.get(Product, product.id).stock


@pytest.fixture
def make(db) -> Factory:
    return Factory(db)
