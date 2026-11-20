#!/usr/bin/env bash
# SAST, SCA and DAST scans on the current commit -> reports/{sast,sca,dast}/ (raw tool output, via tools/capture.py).
# DAST runs only against the local Compose stack (docs/securite/autorisation.md).
# Usage: bash scripts/security-scans.sh        (stack must be up: docker compose up -d --wait)
set -u
cd "$(dirname "$0")/.."
P=backend/.venv/Scripts/python
CAP="$P tools/capture.py"
SRC="$(pwd -W 2>/dev/null || pwd)"
export MSYS_NO_PATHCONV=1

# SAST
$CAP --out reports/sast/bandit.json -- backend/.venv/Scripts/bandit -r backend/app -f json -q
$CAP --out reports/sast/semgrep.json -- docker run --rm -v "$SRC:/src" -w /src semgrep/semgrep semgrep scan \
  --config p/owasp-top-ten --config p/python --config p/typescript --json --metrics off \
  --exclude reports --exclude preuves --exclude node_modules --exclude .venv .
# gitleaks writes its own report (stdout is unreliable when it finds many leaks); scans the whole git history
docker run --rm -v "$SRC:/repo" -v "$SRC/reports/sast:/out" zricethezav/gitleaks detect --source /repo \
  --report-format json --report-path /out/gitleaks.json --no-banner --exit-code 0

# SCA
$CAP --out reports/sca/pip-audit.json -- docker run --rm -v "$SRC/backend:/b:ro" python:3.13-alpine3.24 sh -c \
  "pip install -q pip-audit >/dev/null 2>&1 && pip-audit -r /b/requirements.txt -f json --progress-spinner off"
$CAP --out reports/sca/npm-audit.json -- npm --prefix web audit --json
$CAP --out reports/sca/trivy-fs.json -- docker run --rm -v "$SRC:/repo:ro" -v trivy-cache:/root/.cache aquasec/trivy fs \
  --quiet --format json --scanners vuln,secret,misconfig --skip-dirs /repo/web/node_modules \
  --skip-dirs /repo/backend/.venv --skip-dirs /repo/reports --skip-dirs /repo/docs/preuves /repo
for img in api web; do
  $CAP --out "reports/sca/trivy-image-$img.json" -- docker run --rm -v //var/run/docker.sock:/var/run/docker.sock \
    -v trivy-cache:/root/.cache aquasec/trivy image --quiet --format json --scanners vuln "shop-$img"
  $CAP --out "reports/sca/sbom-$img.cdx.json" -- docker run --rm -v //var/run/docker.sock:/var/run/docker.sock \
    anchore/syft "shop-$img" -o cyclonedx-json -q
done
$CAP --out reports/sca/hadolint-backend.json --stdin backend/Dockerfile -- docker run --rm -i hadolint/hadolint hadolint --format json -
$CAP --out reports/sca/hadolint-web.json --stdin web/Dockerfile -- docker run --rm -i hadolint/hadolint hadolint --format json -

# DAST (local stack only)
NET=$(docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' "$(docker compose ps -q web)")
docker run --rm --network "$NET" -v "$SRC/reports/dast:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://web:8080 -J zap-baseline.json -r zap-baseline.html -I | tail -3
TOKEN=$(docker run --rm --network "$NET" curlimages/curl -fsS -X POST http://api:8000/api/auth/login \
  -d 'username=admin@example.com&password=admin1234' | $P -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
docker run --rm --network "$NET" -v "$SRC/reports/dast:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t http://api:8000/openapi.json -f openapi -J zap-api.json -r zap-api.html -I \
  -z "-config replacer.full_list(0).description=auth -config replacer.full_list(0).enabled=true \
-config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=Authorization \
-config replacer.full_list(0).regex=false -config replacer.full_list(0).replacement=Bearer\ $TOKEN" | tail -3

$P tools/security_summary.py --out reports/securite-synthese.md

# Tool versions, as reported by each tool (read by tools/freeze_evidence.py)
mkdir -p reports/versions
v() { local n=$1; shift; local o=(); [ "$1" = --with-stderr ] && { o=(--with-stderr); shift; }; $CAP --out "reports/versions/$n.txt" "${o[@]}" -- "$@"; }
v semgrep docker run --rm semgrep/semgrep semgrep --version
v gitleaks docker run --rm zricethezav/gitleaks version
v trivy docker run --rm aquasec/trivy --version
v syft docker run --rm anchore/syft version
v hadolint docker run --rm hadolint/hadolint hadolint --version
v zap docker run --rm ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd -version
v k6 docker run --rm grafana/k6 version
v bandit backend/.venv/Scripts/bandit --version
v postgres docker compose exec -T db postgres --version
v api-python docker compose exec -T api python --version
v web-nginx docker compose exec -T web sh -c 'nginx -v 2>&1'
v mutmut docker run --rm python:3.13-alpine3.24 sh -c "pip install -q --root-user-action=ignore mutmut==3.8.1 >/dev/null 2>&1; pip show mutmut | head -2"
