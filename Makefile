.PHONY: db db-reset api web test lint check smoke

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
test:      ## pytest against the shop_test database (created automatically)
	cd backend && $(VENV)/pytest -q
lint:      ## ruff on the backend, oxlint + type check on the front end
	cd backend && $(VENV)/ruff check .
	cd web && npm run lint && npx tsc -b
check: lint test  ## full gate used by /anomalie and /phase-done
smoke:     ## curl checks against the running API
	./scripts/smoke.sh
