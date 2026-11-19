.PHONY: db db-reset api web test test-unit test-api lint docs check smoke

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

test: test-unit test-api  ## all backend suites, JUnit + coverage (statements and branches) in reports/

test-unit: ## unit tests (no database) -> reports/junit-unit.xml; unit-only coverage of app/services
	cd backend && $(VENV)/pytest tests/unit -q $(COV) --cov-report= --junitxml=$(REPORTS)/junit-unit.xml
	cd backend && $(VENV)/coverage report --include="app/services/*" --precision=1

test-api:  ## API tests on the shop_test database -> reports/junit-api.xml; combined coverage reports
	cd backend && $(VENV)/pytest tests/api -q $(COV) --cov-append --junitxml=$(REPORTS)/junit-api.xml \
	  --cov-report=xml:$(REPORTS)/coverage.xml --cov-report=html:$(REPORTS)/htmlcov --cov-report=
	cd backend && $(VENV)/coverage report --include="app/services/*" --precision=1

lint:      ## ruff (lint + format check) on the backend, oxlint + type check on the front end
	cd backend && $(VENV)/ruff check . && $(VENV)/ruff format --check .
	cd web && npm run lint && npx tsc -b
docs:      ## traceability between exigences.yaml, exigences.md and cahier-de-test.md
	backend/$(VENV)/ruff check --config backend/pyproject.toml tools
	backend/$(VENV)/python tools/check_docs.py docs
check: lint docs test  ## full gate used by /anomalie and /phase-done
smoke:     ## curl checks against the running API
	./scripts/smoke.sh
