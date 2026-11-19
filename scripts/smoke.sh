#!/usr/bin/env bash
# Smoke test against a running API: make api, then make smoke
set -euo pipefail
BASE=${BASE:-http://localhost:8000/api}
json() { python3 -c "import sys, json; print(json.load(sys.stdin)$1)"; }

echo "health:    $(curl -fsS "$BASE/health")"
echo "products:  $(curl -fsS "$BASE/products?limit=1" | json '["total"]') in catalogue"

code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/orders" \
  -H 'Content-Type: application/json' -d '{"items":[{"product_id":1,"quantity":1}]}')
[ "$code" = 401 ] && echo "no token:  401 as expected" || { echo "FAIL: expected 401, got $code"; exit 1; }

TOKEN=$(curl -fsS -X POST "$BASE/auth/login" -d 'username=demo@example.com&password=demo1234' | json '["access_token"]')
echo "login:     token received"

total=$(curl -fsS -X POST "$BASE/orders" -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"items":[{"product_id":1,"quantity":1}]}' | json '["total_cents"]')
echo "checkout:  201, total_cents=$total"
