"""REL-01 (restart PostgreSQL under load) and REL-02 (kill the API process) on the Docker Compose stack.

Runs tools/reliability_probe.py in a container on the Compose network, injects the fault after --fault-at seconds,
then checks consistency in PostgreSQL. Writes reports/reliability/<case>.json (the measurements) next to the raw
probe timeline. Usage: backend/.venv/Scripts/python tools/reliability.py rel-01 | rel-02 [--duration 120]
"""

import argparse
import json
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "reliability"
CONSISTENCY_SQL = {
    "orders_without_lines": "SELECT count(*) FROM orders o WHERE NOT EXISTS (SELECT 1 FROM order_items i WHERE i.order_id = o.id)",
    "orders_with_wrong_subtotal": "SELECT count(*) FROM orders o WHERE o.subtotal_cents <> "
    "(SELECT coalesce(sum(i.quantity * i.unit_price_cents), 0) FROM order_items i WHERE i.order_id = o.id)",
    "orders_with_wrong_total": "SELECT count(*) FROM orders WHERE total_cents <> subtotal_cents - discount_cents",
    "negative_stock": "SELECT count(*) FROM products WHERE stock < 0",
    "orders_without_audit": "SELECT count(*) FROM orders o WHERE NOT EXISTS (SELECT 1 FROM audit_log a "
    "WHERE a.action = 'ORDER_CREATED' AND a.entity_id = o.id)",
}


def utc() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def sql(query: str) -> str:
    cmd = ["docker", "compose", "exec", "-T", "db", "psql", "-U", "shop", "-d", "shop", "-tAc", query]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).stdout.strip()


def inject(case: str, log: list) -> None:
    log.append({"time": utc(), "step": "fault injected"})
    if case == "rel-01":
        subprocess.run(["docker", "compose", "restart", "db"], cwd=ROOT, capture_output=True)
        log.append({"time": utc(), "step": "docker compose restart db returned"})
    else:
        container = subprocess.run(
            ["docker", "compose", "ps", "-q", "api"], cwd=ROOT, capture_output=True, text=True
        ).stdout.strip()
        subprocess.run(["docker", "exec", container, "kill", "1"], capture_output=True)  # crash the API process
        log.append({"time": utc(), "step": "API process (PID 1) killed; restart policy must bring it back"})


def analyse(timeline: dict, fault_time: str) -> dict:
    events = timeline["events"]
    health = [(t, s) for t, k, s, _ in events if k == "health"]
    first_down = next((t for t, s in health if t >= fault_time and s != 200), None)
    back_up = next((t for t, s in health if first_down and t > first_down and s == 200), None)

    def seconds(a, b):
        return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 2) if a and b else None

    window = (first_down, back_up)
    in_window = lambda t: first_down is not None and first_down <= t <= (back_up or "9999")  # noqa: E731
    statuses: dict[str, int] = {}
    for t, kind, status, _ in events:
        statuses[f"{kind} {status}"] = statuses.get(f"{kind} {status}", 0) + 1
    return {
        "requests": len(events),
        "status_counts": statuses,
        "health_first_not_200": first_down,
        "health_back_to_200": back_up,
        "recovery_seconds_from_fault": seconds(fault_time, back_up),
        "outage_seen_by_client_seconds": seconds(first_down, back_up),
        "health_codes_during_outage": sorted({s for t, s in health if in_window(t)}),
        "http_500_outside_outage_window": sum(1 for t, k, s, _ in events if s == 500 and not in_window(t)),
        "http_500_total": sum(1 for _, _, s, _ in events if s == 500),
        "orders_acknowledged_201": sorted({o for _, k, s, o in events if k == "order" and s == 201}),
        "window": window,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=["rel-01", "rel-02"])
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--fault-at", type=int, default=30)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    product = sql("SELECT id FROM products WHERE stock > 0 ORDER BY stock DESC LIMIT 1")
    sql(f"UPDATE products SET stock = 100000 WHERE id = {product}")  # enough stock for the whole run (test data)
    steps: list = [{"time": utc(), "step": f"probe started ({args.duration} s, product {product})"}]

    probe = [
        "docker",
        "run",
        "--rm",
        "--network",
        "shop_default",
        "-v",
        f"{(ROOT / 'tools').resolve().as_posix()}:/tools:ro",
        "-v",
        f"{OUT.resolve().as_posix()}:/out",
        "-e",
        f"DURATION={args.duration}",
        "-e",
        f"PRODUCT_ID={product}",
        "-e",
        f"NAME={args.case}",
        "python:3.13-alpine3.24",
        "python",
        "/tools/reliability_probe.py",
    ]
    timer = threading.Timer(args.fault_at, inject, args=(args.case, steps))
    timer.start()
    subprocess.run(probe, check=True)
    timer.join()
    time.sleep(2)
    timeline = json.loads((OUT / f"{args.case}-timeline.json").read_text(encoding="utf-8"))
    result = analyse(timeline, steps[1]["time"])
    acknowledged = result.pop("orders_acknowledged_201")
    ids = ",".join(str(i) for i in acknowledged) or "0"
    found = int(sql(f"SELECT count(*) FROM orders WHERE id IN ({ids})") or 0)
    result.update(
        {
            "case": args.case.upper(),
            "steps": steps,
            "orders_acknowledged_201": len(acknowledged),
            "orders_acknowledged_found_in_database": found,
            "consistency": {name: int(sql(q) or -1) for name, q in CONSISTENCY_SQL.items()},
        }
    )
    (OUT / f"{args.case}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "status_counts"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
