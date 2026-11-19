"""Load and health probe for REL-01/REL-02, run inside a container on the Compose network (stdlib only).

Registers a unique customer, then for DURATION seconds: WORKERS threads place 1-unit orders and list products,
while one thread polls /api/health every 0.25 s. Every request is recorded as [utc_time, kind, status, order_id].
Writes /out/<NAME>-timeline.json.
"""

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime

BASE = os.environ.get("BASE_URL", "http://web:8080")
DURATION = float(os.environ.get("DURATION", "120"))
WORKERS = int(os.environ.get("WORKERS", "4"))
PRODUCT_ID = int(os.environ.get("PRODUCT_ID", "1"))
NAME = os.environ.get("NAME", "rel")

events: list = []
lock = threading.Lock()


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def call(method: str, path: str, body: bytes | None = None, headers: dict | None = None, timeout: float = 10):
    req = urllib.request.Request(f"{BASE}{path}", data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return 0, b""  # no answer at all (connection refused or timeout)


def record(kind: str, status: int, order_id=None) -> None:
    with lock:
        events.append([now(), kind, status, order_id])


def main() -> None:
    email = f"rel-{uuid.uuid4().hex[:10]}@test.example"
    call(
        "POST",
        "/api/auth/register",
        json.dumps({"email": email, "password": "rel-pass-123"}).encode(),
        {"Content-Type": "application/json"},
    )
    status, body = call(
        "POST",
        "/api/auth/login",
        urllib.parse.urlencode({"username": email, "password": "rel-pass-123"}).encode(),
        {"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = json.loads(body)["access_token"]
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    stop = time.monotonic() + DURATION
    order_body = json.dumps({"items": [{"product_id": PRODUCT_ID, "quantity": 1}]}).encode()

    def worker() -> None:
        while time.monotonic() < stop:
            s, b = call("POST", "/api/orders", order_body, auth)
            order_id = json.loads(b).get("id") if s == 201 else None
            record("order", s, order_id)
            s, _ = call("GET", "/api/products?limit=5")
            record("list", s)
            time.sleep(0.2)

    def health() -> None:
        while time.monotonic() < stop:
            s, _ = call("GET", "/api/health", timeout=2)
            record("health", s)
            time.sleep(0.25)

    threads = [threading.Thread(target=worker) for _ in range(WORKERS)] + [threading.Thread(target=health)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with open(f"/out/{NAME}-timeline.json", "w", encoding="utf-8") as f:
        json.dump({"customer": email, "product_id": PRODUCT_ID, "events": events}, f)
    print(f"{len(events)} requests recorded for {email}")


if __name__ == "__main__":
    main()
