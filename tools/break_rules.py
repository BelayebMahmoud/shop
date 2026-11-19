"""Break each business rule on purpose, run the unit tests, show which cases fail, restore the file byte-for-byte.

Proves the unit tests detect a broken rule (fiche 2: a test that cannot fail proves nothing).
Usage, from the repository root:
    backend/.venv/Scripts/python tools/break_rules.py --backend backend --out reports/unit/regles-cassees.txt
Exit code 1 if a deliberately broken rule is not detected by any test (surviving mutant).
"""

import argparse
import pathlib
import subprocess
import sys
from datetime import UTC, datetime

MUTANTS = [
    (
        "BR-04 negative guard < 0 -> <= 0",
        "app/services/pricing.py",
        "    if subtotal_cents < 0:",
        "    if subtotal_cents <= 0:",
    ),
    (
        "BR-03 max lines 50 -> 51",
        "app/services/order_rules.py",
        "MIN_LINES, MAX_LINES = 1, 50",
        "MIN_LINES, MAX_LINES = 1, 51",
    ),
    (
        "BR-05 ADMIN removed from back office",
        "app/services/workflow.py",
        "BACK_OFFICE = frozenset({STAFF, ADMIN})",
        "BACK_OFFICE = frozenset({STAFF})",
    ),
    (
        "BR-05 customer may ship",
        "app/services/workflow.py",
        "if not (target == CANCELLED and current == PLACED):",
        "if not ((target == CANCELLED and current == PLACED) or target == SHIPPED):",
    ),
    (
        "BR-04 tier boundary >= -> >",
        "app/services/pricing.py",
        "    if subtotal_cents >= TIER_5_FROM_CENTS:",
        "    if subtotal_cents > TIER_5_FROM_CENTS:",
    ),
    (
        "BR-04 rounding half-up -> truncate",
        "app/services/pricing.py",
        "discount = (subtotal_cents * percent + 50) // 100",
        "discount = (subtotal_cents * percent) // 100",
    ),
    (
        "BR-03 max quantity 99 -> 100",
        "app/services/order_rules.py",
        "MIN_QUANTITY, MAX_QUANTITY = 1, 99",
        "MIN_QUANTITY, MAX_QUANTITY = 1, 100",
    ),
    (
        "BR-01 stock check < -> <=",
        "app/services/order_rules.py",
        "if stock[pid] < qty",
        "if stock[pid] <= qty",
    ),
    (
        "BR-05 allow SHIPPED -> CANCELLED",
        "app/services/workflow.py",
        "    SHIPPED: frozenset({DELIVERED}),",
        "    SHIPPED: frozenset({DELIVERED, CANCELLED}),",
    ),
    (
        "BR-05 customer may cancel PAID",
        "app/services/workflow.py",
        "if not (target == CANCELLED and current == PLACED):",
        "if not (target == CANCELLED):",
    ),
    (
        "FR-09 low stock < -> <=",
        "app/services/dashboard_rules.py",
        "return stock < LOW_STOCK_BELOW",
        "return stock <= LOW_STOCK_BELOW",
    ),
]


def run_unit_tests(backend: pathlib.Path) -> str:
    cmd = [sys.executable, "-m", "pytest", "tests/unit", "-q", "-p", "no:cacheprovider"]
    return subprocess.run(cmd, cwd=backend, capture_output=True, text=True).stdout


def summary_line(output: str) -> str:
    return [line for line in output.splitlines() if " passed" in line or " failed" in line][-1].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="backend")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    backend = pathlib.Path(args.backend)

    lines = [
        f"# Rules broken on purpose — {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
    ]
    survivors = 0
    for label, rel, old, new in MUTANTS:
        path = backend / rel
        original = path.read_bytes()
        text = original.decode("utf-8")
        if text.count(old) != 1:
            raise SystemExit(f"{label}: pattern not found once in {rel}")
        path.write_text(text.replace(old, new), encoding="utf-8", newline="")
        try:
            output = run_unit_tests(backend)
        finally:
            path.write_bytes(original)
        failed = sorted({ln.split("[")[1].split("]")[0] for ln in output.splitlines() if ln.startswith("FAILED") and "[" in ln})
        survivors += not failed
        detected = ", ".join(failed) or "NONE (mutant survived)"
        lines.append(f"{label:38} -> {summary_line(output)} | failing cases: {detected}")
        assert path.read_bytes() == original, f"{rel} not restored"

    lines.append(f"after restore: {summary_line(run_unit_tests(backend))}")
    report = "\n".join(lines) + "\n"
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
