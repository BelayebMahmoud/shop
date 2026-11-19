"""Start the API for end-to-end tests on a freshly rebuilt, disposable database (default: shop_e2e).

Used by web/playwright.config.ts as its API web server. Applies db/migrations 001..003 (not the 50,000-product
volume seed: E2E tests create their own data), then serves the app with uvicorn. Requests slower than one second
are printed (server-side duration), which made the environment issue ENV-01 visible (docs/anomalies.md).

Environment: E2E_DATABASE_URL (default postgresql+psycopg://shop:shop@localhost:5433/shop_e2e), E2E_API_PORT (8001).
"""

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_URL = os.environ.get("E2E_DATABASE_URL", "postgresql+psycopg://shop:shop@localhost:5433/shop_e2e")
PORT = int(os.environ.get("E2E_API_PORT", "8001"))

os.environ["DATABASE_URL"] = DB_URL
os.environ.setdefault("JWT_SECRET", "e2e-only-secret-0123456789abcdef0123456789")
sys.path.insert(0, str(ROOT / "backend"))

import uvicorn  # noqa: E402
from sqlalchemy import create_engine, make_url, text  # noqa: E402


def rebuild_database() -> None:
    url = make_url(DB_URL)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        if not conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": url.database}):
            conn.exec_driver_sql(f'CREATE DATABASE "{url.database}"')
    admin.dispose()
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for f in sorted((ROOT / "db" / "migrations").glob("*.sql")):
            if f.name != "004_volume_seed.sql":
                conn.connection.cursor().execute(f.read_text(encoding="utf-8"))
    engine.dispose()


if __name__ == "__main__":
    rebuild_database()
    from app.main import app

    @app.middleware("http")
    async def log_slow_requests(request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        if elapsed > 1:
            print(f"SLOW {elapsed:.1f}s {request.method} {request.url.path} -> {response.status_code}", flush=True)
        return response

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
