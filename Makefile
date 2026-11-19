.PHONY: db db-reset api web test test-unit test-integration test-api test-contract coverage api-coverage lint docs check smoke

# The virtualenv keeps its executables in Scripts/ on Windows and bin/ elsewhere.
ifeq ($(OS),Windows_NT)
VENV := .venv/Scripts
else
VENV := .venv/bin
endif

db:        ## start Postgres (applies db/migrations on first start)
	docker compose up -d --wait db
db-reset:  ## wipe the volume and re-run migrations + seed
	docker compose down -v && docker compose up -d --wait db
api:       ## FastAPI on :8000 (terminal 1)
	cd backend && $(VENV)/uvicorn app.main:app --reload --port 8000
web:       ## Vite on :5173, proxies /api to :8000 (terminal 2)
	cd web && npm run dev
REPORTS := ../reports
COV := --cov=app --cov-branch

# Fastest to slowest (fiche 1): unit -> integration -> API -> contract. Coverage accumulates across the suites.
test: test-unit test-integration test-api test-contract coverage api-coverage  ## all backend suites + reports

test-unit: ## unit tests (no database) -> reports/junit-unit.xml; unit-only coverage of app/services
	cd backend && $(VENV)/pytest tests/unit -q $(COV) --cov-report= --junitxml=$(REPORTS)/junit-unit.xml
	cd backend && $(VENV)/coverage report --include="app/services/*" --precision=1

test-integration: ## IT cases on the shop_test database -> reports/junit-integration.xml
	cd backend && $(VENV)/pytest tests/integration -q $(COV) --cov-append --cov-report= \
	  --junitxml=$(REPORTS)/junit-integration.xml

test-api:  ## TA cases (incl. permissions matrix) -> reports/junit-api.xml
	cd backend && $(VENV)/pytest tests/api -q $(COV) --cov-append --cov-report= --junitxml=$(REPORTS)/junit-api.xml

test-contract: ## TA-28 Schemathesis on /openapi.json, all checks -> reports/junit-contract.xml
	cd backend && $(VENV)/pytest tests/contract -q -p no:logging $(COV) --cov-append --cov-report= \
	  --junitxml=$(REPORTS)/junit-contract.xml

coverage:  ## combined coverage (statements + branches) -> reports/coverage.xml, reports/htmlcov/
	cd backend && $(VENV)/coverage xml -q -o $(REPORTS)/coverage.xml && $(VENV)/coverage html -q -d $(REPORTS)/htmlcov
	cd backend && $(VENV)/coverage report --include="app/services/*" --precision=1 --fail-under=80  # QR-MA-01

api-coverage: ## route x method x documented code, obtained or not -> reports/api-coverage.md
	backend/$(VENV)/python tools/api_coverage.py --junit reports/junit-api.xml reports/junit-integration.xml \
	  --out reports/api-coverage.md

lint:      ## ruff (lint + format check) on the backend, oxlint + type check on the front end
	cd backend && $(VENV)/ruff check . && $(VENV)/ruff format --check .
	cd web && npm run lint && npx tsc -b
docs:      ## traceability between exigences.yaml, exigences.md and cahier-de-test.md
	backend/$(VENV)/ruff check --config backend/pyproject.toml tools
	backend/$(VENV)/python tools/check_docs.py docs
check: lint docs test  ## full gate used by /anomalie and /phase-done
smoke:     ## curl checks against the running API
	./scripts/smoke.sh
