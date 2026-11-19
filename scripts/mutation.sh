#!/usr/bin/env bash
# MA-02 (QR-MA-01): mutation testing of the business rules with mutmut, in a Linux container (mutmut needs fork(),
# not available on Windows). Time-boxed (default 15 min). Results: reports/maintenabilite/mutmut-*.{json,txt}.
# Usage: scripts/mutation.sh [timeout-seconds]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIMIT="${1:-900}"
HOST_ROOT="$ROOT"
command -v cygpath >/dev/null 2>&1 && HOST_ROOT="$(cygpath -m "$ROOT")"
MSYS_NO_PATHCONV=1 docker run --rm -v "$HOST_ROOT/backend:/src:ro" -v "$HOST_ROOT/reports/maintenabilite:/out" \
  -e JWT_SECRET=mutation-only-secret-0123456789abcdef0123456789 python:3.13-slim bash -c "
    set -e
    cp -r /src /work && cd /work && rm -rf .venv mutants
    pip install -q --root-user-action=ignore -r requirements-dev.txt mutmut==3.8.1 >/dev/null 2>&1
    echo \"mutmut: run (time box ${LIMIT} s)\"
    timeout ${LIMIT} mutmut run --max-children 4 > /out/mutmut-run.txt 2>&1 || echo \"mutmut stopped (exit \$?)\" >> /out/mutmut-run.txt
    mutmut export-cicd-stats >/dev/null 2>&1 || true
    cp mutants/mutmut-cicd-stats.json /out/mutmut-stats.json 2>/dev/null || true
    mutmut results --all true > /out/mutmut-results.txt 2>&1 || true
    tail -3 /out/mutmut-run.txt
    cat /out/mutmut-stats.json 2>/dev/null || true
  "
