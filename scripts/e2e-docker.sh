#!/usr/bin/env bash
# E2E against the running Docker Compose stack, from the official Playwright image, on the Compose network.
# Covers browsers that cannot run on the host (ENV-02: Firefox on Windows) and checks parallel runs (ENV-01).
# Usage: scripts/e2e-docker.sh [projects...]   e.g. scripts/e2e-docker.sh firefox chromium   (default: all)
# Env: E2E_WORKERS (default 4), E2E_JUNIT_NAME (default junit-e2e-docker.xml). Needs `make stack` first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NETWORK="$(docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' "$(docker compose -f "$ROOT/docker-compose.yml" ps -q web)")"
PROJECTS=""
for p in "$@"; do PROJECTS="$PROJECTS --project=$p"; done
MSYS_NO_PATHCONV=1 docker run --rm --ipc=host --network "$NETWORK" \
  -v "$ROOT:/repo" -v /repo/web/node_modules -w /repo/web \
  -e E2E_BASE_URL=http://web:8080 -e E2E_WORKERS="${E2E_WORKERS:-4}" \
  -e E2E_JUNIT="../reports/${E2E_JUNIT_NAME:-junit-e2e-docker.xml}" -e CI=1 \
  mcr.microsoft.com/playwright:v1.65.1-noble \
  bash -c "npm ci --no-audit --no-fund --silent && npx playwright test $PROJECTS"
