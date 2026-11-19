# Shop MVP — ISO/IEC 25010 test project

A FastAPI + PostgreSQL backend (`backend/`), a React/Vite front end (`web/`) and SQL migrations (`db/migrations/`).
The project is evaluated on its test and quality evidence for the 8 ISO/IEC 25010 characteristics.

## The two rules that override everything

1. **Oracle rule.** An expected result comes only from the requirement (`docs/exigences.yaml`, `docs/exigences.md`)
   or from the test case in `docs/cahier-de-test.md`. Never read the expected value from the code. When the rule does
   not decide a case, write `NON SPÉCIFIÉ` and ask. When a test fails because the code is wrong, never change the
   expectation: run `/anomalie <test-id>`.
2. **Golden rule (règle d'or).** Evidence is produced by tools, never written by hand.
   - `reports/**` and `docs/preuves/**` are written only by tools (pytest, Playwright, Semgrep, Bandit, pip-audit,
     ZAP, k6, `tools/trace.py`...). A hook blocks every Edit/Write there.
   - Every number, percentage or verdict in a report must be found in a raw file it links to.
   - Reviews by Claude (`/security-review`, `code-review`, subagents) are *revue de code*, recorded in
     `docs/securite/triage.md` or `docs/journal.md`, never presented as SAST, SCA or DAST tool output.
   - Never accept a security risk on the user's behalf: list the candidates and ask.

## Layout

| Path | Content |
| --- | --- |
| `backend/app/` | FastAPI app: `routers/` (auth, products, orders), `models.py`, `schemas.py`, `security.py` |
| `backend/tests/` | pytest; `conftest.py` rebuilds the schema of `shop_test` from `db/migrations` before each test |
| `web/src/` | React pages, Vite proxies `/api` to `:8000` |
| `docs/` | Deliverables in French: exigences, cahier de test, anomalies, journal, rapports, traçabilité |
| `reports/` | Raw tool output (JSON, XML, logs) — tool-written only |
| `.claude/` | Project skills, subagents and hooks (part of the deliverable) |

## Commands

- `make db` / `make db-reset` — Postgres 16 in Docker (user/password/db `shop`).
- `make api` (port 8000), `make web` (port 5173).
- `make test` — pytest against `shop_test`; `make check` — the full gate used by `/anomalie` and `/phase-done`.
- Windows without `make`: run the recipe directly, e.g. `cd backend && .venv/Scripts/python -m pytest -q`.

## Tests

- pytest: mark each test `@pytest.mark.req("<REQ-ID>")`, test name/id = case ID from the cahier.
- Playwright: `@<REQ-ID>` in the test title. Exploratory browser sessions (Playwright MCP) are not evidence;
  only `.spec.ts` files run by Playwright Test count.
- Arrange-Act-Assert, F.I.R.S.T.: no fixed sleeps, no order dependence, no network beyond localhost.
- API tests assert status, body **and** the real effect (database state or a follow-up GET). A 500 is a defect.
- A new test must be seen failing when the rule is broken (`/gen-tests` does this).

## Workflow

- Work phase by phase. Close each with `/phase-done <N>` and wait for "go phase <next>".
- Skills: `/test-design`, `/gen-tests`, `/anomalie`, `/security-triage`, `/trace`, `/phase-done`.
- Subagents: `test-reviewer` before each phase commit, `evidence-auditor` before submission.
- Deliverable documents are written in French; code, identifiers and commit messages in English.
