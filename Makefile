.PHONY: db db-reset stack stack-down install-check api web test test-unit test-integration test-api test-contract \
        coverage api-coverage e2e e2e-docker lint docs check smoke

# Python tools: the backend virtualenv (Scripts/ on Windows, bin/ elsewhere). Override with BIN=<dir> (CI).
ifeq ($(OS),Windows_NT)
BIN ?= $(abspath backend/.venv/Scripts)
else
BIN ?= $(abspath backend/.venv/bin)
endif
REPORTS := $(abspath reports)
COV := --cov=app --cov-branch

db:        ## start Postgres only (applies db/migrations on first start)
	docker compose up -d --wait db
db-reset:  ## wipe the volume and re-run migrations + seed
	docker compose down -v && docker compose up -d --wait db
stack:     ## whole stack in containers (db, api, web), configured by .env
	docker compose up -d --build --wait
stack-down:
	docker compose down
install-check: ## PORT-01: clean install from a fresh clone, timed -> reports/portabilite/
	./scripts/installation-propre.sh
e2e-docker: ## E2E from the Playwright container against the Compose stack (Firefox, parallel)
	./scripts/e2e-docker.sh
api:       ## FastAPI on :8000 (terminal 1)
	cd backend && $(BIN)/uvicorn app.main:app --reload --port 8000
web:       ## Vite on :5173, proxies /api to :8000 (terminal 2)
	cd web && npm run dev

# Fastest to slowest (fiche 1): unit -> integration -> API -> contract. Coverage accumulates across the suites.
test: test-unit test-integration test-api test-contract coverage api-coverage  ## all backend suites + reports

test-unit: ## unit tests (no database) -> reports/junit-unit.xml; unit-only coverage of app/services
	cd backend && $(BIN)/pytest tests/unit -q $(COV) --cov-report= --junitxml=$(REPORTS)/junit-unit.xml
	cd backend && $(BIN)/coverage report --include="app/services/*" --precision=1

test-integration: ## IT cases on the shop_test database -> reports/junit-integration.xml
	cd backend && $(BIN)/pytest tests/integration -q $(COV) --cov-append --cov-report= \
	  --junitxml=$(REPORTS)/junit-integration.xml

test-api:  ## TA cases (incl. permissions matrix) -> reports/junit-api.xml
	cd backend && $(BIN)/pytest tests/api -q $(COV) --cov-append --cov-report= --junitxml=$(REPORTS)/junit-api.xml

test-contract: ## TA-28 Schemathesis on /openapi.json, all checks -> reports/junit-contract.xml
	cd backend && $(BIN)/pytest tests/contract -q -p no:logging $(COV) --cov-append --cov-report= \
	  --junitxml=$(REPORTS)/junit-contract.xml

coverage:  ## combined coverage (statements + branches) -> reports/coverage.xml, reports/htmlcov/
	cd backend && $(BIN)/coverage xml -q -o $(REPORTS)/coverage.xml && $(BIN)/coverage html -q -d $(REPORTS)/htmlcov
	cd backend && $(BIN)/coverage report --include="app/services/*" --precision=1 --fail-under=80  # QR-MA-01

api-coverage: ## route x method x documented code, obtained or not -> reports/api-coverage.md
	$(BIN)/python tools/api_coverage.py --junit reports/junit-api.xml reports/junit-integration.xml \
	  --out reports/api-coverage.md

e2e:       ## Playwright on chromium, firefox, mobile + axe -> reports/junit-e2e.xml, reports/a11y/
	cd web && npx playwright test

lint:      ## ruff (lint + format check) on the backend, oxlint + type check on the front end
	cd backend && $(BIN)/ruff check . && $(BIN)/ruff format --check .
	cd web && npm run lint && npx tsc -b
docs:      ## traceability between exigences.yaml, exigences.md and cahier-de-test.md
	$(BIN)/ruff check --config backend/pyproject.toml tools
	$(BIN)/python tools/check_docs.py docs
check: lint docs test  ## full gate used by /anomalie and /phase-done (E2E separately: make e2e)
smoke:     ## curl checks against the running API
	./scripts/smoke.sh
