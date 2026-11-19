#!/usr/bin/env bash
# PORT-01 (QR-PO-01): clean install from a fresh clone, timed, with the smoke test, logged to
#   reports/portabilite/installation-<host>.log
# Runs under its own Compose project and ports, so it co-exists with a running development stack.
# Usage: scripts/installation-propre.sh [repository-url-or-path]   (default: this repository)
# Needs: git, docker (with compose), curl, python. Set KEEP=1 to leave the stack running afterwards.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${1:-$ROOT}"
HOST="$(hostname | tr '[:upper:]' '[:lower:]')"
LOG_DIR="$ROOT/reports/portabilite"
LOG="$LOG_DIR/installation-$HOST.log"
PROJECT="shop-install"
export DB_PORT="${DB_PORT:-5543}" API_PORT="${API_PORT:-8100}" WEB_PORT="${WEB_PORT:-8180}"
PY="$(command -v python3 >/dev/null 2>&1 && python3 -c 'print(1)' >/dev/null 2>&1 && echo python3 || echo python)"
WORK="$(mktemp -d)"
mkdir -p "$LOG_DIR"

exec > >(tee "$LOG") 2>&1
echo "== Installation propre — $(date -u +%Y-%m-%dT%H:%M:%SZ) — machine: $HOST"
echo "== OS: $(uname -srm) | $(docker --version) | $(docker compose version | head -1)"
START=$(date +%s)

cleanup() {
  if [ "${KEEP:-0}" != "1" ]; then
    (cd "$WORK/shop" 2>/dev/null && docker compose -p "$PROJECT" down -v --remove-orphans >/dev/null 2>&1) || true
  fi
}
trap cleanup EXIT

echo "== 1/5 clone $SOURCE"
git clone --quiet "$SOURCE" "$WORK/shop"
cd "$WORK/shop"
git log --oneline -1

echo "== 2/5 configuration (.env from .env.example, random secrets)"
cp .env.example .env
SECRET="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(32))')"
DBPASS="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(16))')"
sed -i.bak -e "s|^JWT_SECRET=.*|JWT_SECRET=$SECRET|" -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$DBPASS|" \
  -e "s|^DB_PORT=.*|DB_PORT=$DB_PORT|" -e "s|^API_PORT=.*|API_PORT=$API_PORT|" -e "s|^WEB_PORT=.*|WEB_PORT=$WEB_PORT|" .env
rm -f .env.bak

echo "== 3/5 docker compose up -d --build --wait (ports db $DB_PORT, api $API_PORT, web $WEB_PORT)"
docker compose -p "$PROJECT" up -d --build --wait
docker compose -p "$PROJECT" ps --format "table {{.Service}}\t{{.State}}\t{{.Health}}"

echo "== 4/5 smoke test through the web container (nginx -> API -> PostgreSQL)"
BASE="http://127.0.0.1:$WEB_PORT/api" PYTHON="$PY" ./scripts/smoke.sh
echo "security headers on /:"
curl -fsSI "http://127.0.0.1:$WEB_PORT/" | grep -iE "^(content-security-policy|x-content-type-options|x-frame-options|referrer-policy|server):" || true

END=$(date +%s)
ELAPSED=$((END - START))
echo "== 5/5 result: installation and smoke test OK in ${ELAPSED}s (target < 600 s)"
[ "$ELAPSED" -lt 600 ] && echo "VERDICT: PASS" || echo "VERDICT: FAIL (over 10 minutes)"
