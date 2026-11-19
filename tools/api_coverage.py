"""API coverage (fiche 2): every route x method x documented status code, obtained by a test or not.

Documented codes come from the app's OpenAPI contract; obtained codes come from the JUnit reports, where the
test client records each call as <property name="http" value="POST /api/orders 201"/>.

Usage, from the repository root (backend virtualenv):
    backend/.venv/Scripts/python tools/api_coverage.py --junit reports/junit-api.xml reports/junit-integration.xml \
        --out reports/api-coverage.md
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("JWT_SECRET", "api-coverage-tool-only-0123456789abcdef")  # import only, no token is signed

from app.main import app  # noqa: E402
from defusedxml import ElementTree as ET  # noqa: E402  (Semgrep: never parse XML with the stdlib parser)

AUTO_CODES = {"422"}  # FastAPI documents 422 on every route with parameters; reported, not required


def documented() -> dict[tuple[str, str], set[str]]:
    ops = {}
    for path, methods in app.openapi()["paths"].items():
        for method, op in methods.items():
            ops[(method.upper(), path)] = set(op.get("responses", {}))
    return ops


def obtained(junit_files: list[Path]) -> tuple[dict[tuple[str, str], set[str]], int]:
    seen: dict[tuple[str, str], set[str]] = defaultdict(set)
    calls = 0
    for f in junit_files:
        for prop in ET.parse(f).iter("property"):
            if prop.get("name") == "http":
                method, path, code = prop.get("value").split(" ")
                seen[(method, path)].add(code)
                calls += 1
    return seen, calls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    docs = documented()
    seen, calls = obtained([Path(p) for p in args.junit])

    rows, expected_total, hit_total, ops_hit = [], 0, 0, 0
    for (method, path), codes in sorted(docs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        got = seen.get((method, path), set())
        required = codes - AUTO_CODES if codes - AUTO_CODES else codes
        hit = required & got
        expected_total += len(required)
        hit_total += len(hit)
        ops_hit += bool(got)
        cells = ", ".join(f"{c} {'oui' if c in got else 'non'}" for c in sorted(codes))
        extra = ", ".join(sorted(got - codes)) or "—"
        rows.append(f"| `{method}` | `{path}` | {cells} | {extra} |")

    unknown = sorted(f"{m} {p}" for (m, p) in seen if (m, p) not in docs)
    lines = [
        "# Couverture de l'API (route × méthode × code)",
        "",
        f"Généré par `tools/api_coverage.py` le {datetime.now(UTC).isoformat(timespec='seconds')} à partir de "
        f"{', '.join('`' + p + '`' for p in args.junit)} et du contrat OpenAPI de l'application.",
        "",
        f"- Opérations exercées : {ops_hit} / {len(docs)}",
        f"- Codes documentés obtenus (hors 422 automatique non obtenu) : {hit_total} / {expected_total}",
        f"- Appels HTTP enregistrés : {calls}",
        "",
        "| Méthode | Route | Codes documentés : obtenu ? | Codes obtenus non documentés |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
        "Appels vers une route absente du contrat : " + (", ".join(unknown) if unknown else "aucun"),
        "",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[4:7]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
