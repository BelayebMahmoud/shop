# Tonight's Execution Plan: ISO 25010 Project with Claude Code

Nov 19, 2026 · @Mahmoud

## Mission and definition of done

By 03:00 tonight, the repository holds a *Gestion commerciale* application that meets every §4 functional minimum of the cahier des charges. It also holds real execution evidence for all 8 ISO/IEC 25010 characteristics and every §8 deliverable. Claude Code writes the code, tests and documents in 10 phases; you approve each phase and do the steps only a person can do.

### Working assumptions

- **Domain**: *Gestion commerciale* (clients, produits, stock, commandes), which is listed in §3. Send your supervisor a one-line confirmation message before you start.
- **Starting point**: the e-commerce MVP built and tested earlier in this conversation (FastAPI, React, PostgreSQL, JWT). The night extends it rather than starting from zero.
- **Language**: deliverable documents in French, like the course; code and identifiers in English.
- **Team**: one person drives Claude Code. Two or three other people are needed for 15 minutes each: the usability sessions and the install on a second machine.
- **Golden rule** (cahier, last page): no result is claimed without a real run. A tool that cannot run is documented as *non disponible*, with its procedure.

### What exists at 03:00

| Deliverable (§8) | Artifact tonight | Phase |
| --- | --- | --- |
| Versioned source code | Git repo, one commit per phase, tag `v1.0` | All |
| Rapport de conception | `docs/conception.md`: architecture, data model, stack justification, AI-use statement | 1, 9 |
| Matrice de traçabilité | `docs/tracabilite/matrice.md`, generated from test reports | 9 |
| Executable test suites + reports | `tests/**`, `reports/**` (JUnit, coverage, k6, Bandit, Semgrep, pip-audit, ZAP, axe) | 2–8 |
| Rapport de conformité ISO 25010 | `docs/conformite.md`, one section per characteristic with sub-characteristics and evidence links | 9 |
| Guide d'installation | `README.md` + `docs/installation.md`, run on a second machine | 5, 8 |
| Soutenance | `docs/demo.md` script: live app + 2 test layers (Playwright, k6) | 10 |
| Test plan and test report (course, fiche 1) | `docs/plan-de-test.md`, `docs/cahier-de-test.md`, `docs/rapport-de-test.md` | 1, 9 |

### Who does what

| Claude Code | You |
| --- | --- |
| Writes requirements, Gherkin, cahier de test, code, tests, scripts, CI, reports | Confirm the domain with the supervisor |
| Runs every tool and reports its real output | Review each phase's diff and say "go" |
| Triages security alerts with written justifications | Accept or reject each risk it proposes to accept |
| Generates the matrix and conformity report from raw files | Run the usability sessions and the second-machine install |
| Never edits evidence files by hand | Read the final reports and rehearse the demo |

## 1. What the course documents require

The four documents add method requirements on top of the cahier des charges. The expected result always comes from the rule, never from the code. Every test follows the chain *exigence → condition de test → scénario → cas de test → script → verdict*. Each layer has named techniques a reviewer will look for. Revision sheets 3 (performance, reliability, maintainability) and 5 (E2E, usability, compatibility, portability) are cited in sheet 1 but were not provided; for those layers the plan follows §7 of the cahier. If you have them, give them to Claude Code at phases 4 and 7.

### Obligations by document

| Source | Obligation | Where in tonight's plan |
| --- | --- | --- |
| Fiche 1 | The oracle is the rule or specification, never the code under test | `CLAUDE.md` rule; every prompt |
| Fiche 1 | Traceability chain exigence → condition → scénario → cas → script → verdict | Columns of the matrix (phase 9) |
| Fiche 1 | Test process: Planifier, Analyser, Concevoir, Implémenter, Exécuter, Clôturer, each with its output | Phase 1 (plan, conditions, cahier), phases 2–8 (scripts, verdicts, anomalies), phase 9 (rapport de test, leçons) |
| Fiche 1 | Common method: measurable goal, Soit/Quand/Alors scenario, cahier, script, verdict; if it fails, find the cause, fix, re-run | Every phase prompt ends with run + verdict; `docs/anomalies.md` logs each defect with its confirmation and regression re-run |
| Fiche 1 | Run from fastest to slowest: format and SAST → unit → integration, API, SCA → E2E, compatibility → performance, DAST | CI stage order (phase 5) |
| Fiche 1 | Combine static and dynamic tests; black box, white box, experience-based and static techniques | Phases 2, 3, 5 |
| Fiche 2 | Unit: F.I.R.S.T., Arrange-Act-Assert, valid and expected-failure cases; partitions, boundary values, decision table, state transitions | Phase 2 |
| Fiche 2 | Cahier de test fields: ID, objectif, règle couverte, préconditions, données, étapes, attendu, obtenu, verdict, type | `docs/cahier-de-test.md` (phase 1), results filled in phase 9 |
| Fiche 2 | Coverage of statements and branches; mutation testing; property-based testing | pytest-cov (phase 2), mutmut and Hypothesis (phase 8) |
| Fiche 2 | Integration: one test per interface, both success and error; stubs, mocks, drivers; data-flow and error-propagation tests; disposable database; 100% of interfaces exercised | Phase 3 (IT-xx cases) |
| Fiche 2 | API: check status, body and real effect; test in the order the API checks (identity → shape → existence → business rule); resource lifecycle; contract; authorization; never a 500; every route × method × code covered | Phase 3 (TA-xx cases, Schemathesis) |
| Fiche 4 | SAST with rule-based and taint analysis, secret detection; triage each alert true / false / to watch with a written reason; exit criterion: no unhandled high alert | Phase 6 (Semgrep, Bandit, gitleaks); Hadolint in phase 5 |
| Fiche 4 | SCA: full inventory including transitive dependencies (SBOM); per CVE decide update, replace or accept (with reachability and written reason); check licences; re-run | Phase 6 (pip-audit, npm audit, Trivy, Syft) |
| Fiche 4 | DAST: written authorization, test environment, passive then active scan, triage, fix, rescan; 4 manual attacks (injection, XSS, access control, session) | Phase 6 (ZAP baseline + active API scan, local stack only) |
| Chapitre I | Product quality: 8 characteristics and their sub-characteristics | Conformity report structure (phase 9), table below |
| Chapitre I | Quality in use: effectiveness, efficiency, satisfaction, freedom from risk, context coverage | Usability protocol (phase 4), sessions (phase 7), results (phase 8): task success, time on task, SUS |
| Chapitre I | Good practices it names: `/health`, environment variables, parameterized queries, hashed passwords, no hard-coded secrets, field-level error messages, confirmation before deletion, configurable ports, single-responsibility modules | Built in phases 2, 4, 5, 7 and checked in phase 9 |

### Sub-characteristics and tonight's evidence

| Characteristic | Sub-characteristics (Chapitre I) | Evidence produced tonight |
| --- | --- | --- |
| Functional suitability | Completeness, correctness, appropriateness | All FR/BR traced to passing tests; decision tables for discount and order rules |
| Reliability | Maturity, availability, fault tolerance, recoverability | Concurrency and rollback tests; DB restart during load; `/health` + restart policy; recovery time |
| Performance efficiency | Time behaviour, resource utilization, capacity | k6: p95 < 500 ms at 20 users; search on 50,000 products; `docker stats` capture |
| Security | Confidentiality, integrity, non-repudiation, accountability, authenticity | RBAC matrix, access-control test, audit log, Argon2id, JWT expiry; SAST, SCA, DAST reports |
| Usability | Recognizability, learnability, operability and accessibility, user error protection | axe: 0 serious or critical; 3–5 user sessions; field errors; delete confirmation |
| Compatibility | Co-existence, interoperability | E2E on Chromium and Firefox; documented OpenAPI contract checked by Schemathesis; configurable ports |
| Maintainability | Modularity, reusability, analysability, modifiability, testability | Layered code, complexity ≤ 10, coverage ≥ 80% on services, mutation score |
| Portability | Adaptability, installability, replaceability | Whole stack in Docker Compose, env-only configuration, timed clean install, second-machine install log |

## 2. Tonight's timeline

The night runs from 18:30 to 03:00 in ten phases. Portability comes before security so the DAST scan hits the containerised stack, as it would in a real test environment. Your own tasks run in parallel with Claude Code's work, so they cost no extra time.

&#91;embedded content: tonight's schedule · 10 phases, 3 checkpoints\]

At each dashed line, compare where you are with the checkpoint table in section 6 and apply its cuts if you are more than 20 minutes late.

## 3. Setup (18:30 to 18:50)

Start from the tested MVP, put the subject documents inside the repo so Claude Code can read them, and set the rules once in `CLAUDE.md`. Pull the Docker images for the scanners now; they download while phase 1 runs.

### Prerequisites

Docker Desktop (or Docker Engine with Compose), Python 3.12+, Node 22, Git, and Claude Code installed and signed in.

### Steps

1. Unzip the starter repo (`shop-mvp-starter.zip`, sent with this plan; it is the MVP code tested earlier) and commit it:

```bash
unzip shop-mvp-starter.zip && cd shop
git init && git add -A && git commit -m "phase 0: MVP de départ (testé)"
```

2. Put the subject documents in the repo: `docs/cahier-des-charges.pdf` and `docs/cours/` (the 4 PDFs). Export this plan as Markdown (doc menu → Export) to `docs/plan-de-la-nuit.md`.
3. Create `CLAUDE.md`, `.claude/settings.json` and `.claude/hooks/protect_evidence.py` from the blocks below.
4. Pull the scanner images in the background:

```bash
for i in ghcr.io/zaproxy/zaproxy:stable grafana/k6 zricethezav/gitleaks aquasec/trivy anchore/syft hadolint/hadolint; do docker pull -q $i & done; wait
```

5. Start Claude Code in the repo and paste the kick-off prompt (P0).

### `CLAUDE.md`

```markdown
# Project: Gestion commerciale — ISO/IEC 25010 conformity

## Context
FastAPI + SQLAlchemy + PostgreSQL + React/TypeScript + JWT. Graded on ISO/IEC 25010 conformity.
Subject: docs/cahier-des-charges.pdf. Course: docs/cours/*.pdf. Tonight's plan: docs/plan-de-la-nuit.md.
Deliverable documents (docs/*.md) are written in French. Code, identifiers and commit messages in English.

## Golden rule (non-negotiable)
- Never write a result, number, coverage figure or verdict that did not come from a real run.
  Numbers come only from files the tools wrote in reports/.
- If a tool cannot run here: write "non disponible", the procedure and the reason. Never simulate output.
- Never edit reports/ or docs/preuves/ by hand.

## Oracle
- Expected results come from the rule (docs/exigences.yaml, docs/exigences.md), never from the code under test.
- When a test fails, re-read the rule: either the expectation is wrong (say so) or it is a defect.
  A defect goes in docs/anomalies.md; fix it, re-run that test (confirmation), then the full suite (regression).

## Traceability
- Every test carries its requirement IDs: pytest @pytest.mark.req("BR-01"); Playwright "@BR-01" in the title; k6 tag req.
- Test case IDs: CT-xx unit, IT-xx integration, TA-xx API, E2E-xx, SEC-xx, PERF-xx, REL-xx, UX-xx, PORT-xx.
- Never invent a requirement ID; propose the missing requirement instead.

## Writing tests
- Unit tests are F.I.R.S.T. and Arrange-Act-Assert, with valid cases AND expected-failure cases.
- Techniques: equivalence partitions, boundary values, decision tables, state transitions.
- API tests check status + body + real effect, in the order identity → shape → existence → business rule. A 500 is always a defect.
- Never delete, skip or weaken a test or an assertion to make CI pass.

## Architecture
app/api (routes) → app/services (business rules) → app/models (SQLAlchemy). Cyclomatic complexity ≤ 10.
Configuration only through environment variables. No secret in the code.

## Security
Active scans (ZAP) only against http://localhost (authorization in docs/securite/autorisation.md).
Every alert is triaged true / false / to watch with a written reason. Ask me before accepting any risk.

## End of every phase
Run `make check`, show its real output, append to docs/journal.md (done, evidence files, gaps),
then `git commit -m "phase N: ..."`. Then stop and wait for "go phase N+1".
```

### `.claude/settings.json` and the evidence hook

```json
{
  "permissions": {
    "allow": ["Bash(make:*)", "Bash(pytest:*)", "Bash(npm:*)", "Bash(npx:*)", "Bash(docker:*)",
              "Bash(git add:*)", "Bash(git commit:*)", "Bash(git diff:*)", "Bash(git status)"],
    "deny": ["Bash(git push:*)", "Bash(rm -rf:*)", "Read(./backend/.env)", "Edit(reports/**)", "Edit(docs/preuves/**)"]
  },
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/protect_evidence.py" }] }
    ]
  }
}
```

```python
# .claude/hooks/protect_evidence.py — exit code 2 blocks the edit and tells Claude why
import json, sys
path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "").replace("\\", "/")
if "/reports/" in path or "docs/preuves/" in path:
    print("Evidence is written by the tools only (règle d'or du cahier des charges).", file=sys.stderr)
    sys.exit(2)
```

The hook only blocks Claude's file-editing tools; tools that Claude runs through the shell still write their reports normally.

### P0: kick-off prompt

```text
Read CLAUDE.md, docs/cahier-des-charges.pdf, the 4 PDFs in docs/cours/ and docs/plan-de-la-nuit.md.
Do not write code yet. Reply with:
1. Every requirement of the cahier (§4 functional minimums, §6 the 8 characteristics, §7 test layers, §8
   deliverables) with the current state of this repo for each: done / partial / missing.
2. Anything in the plan that contradicts the cahier or the course sheets.
3. At most 3 blocking questions.
Then wait for "go phase 1".
```

**Done when**: Claude Code's gap list matches section 1 of this plan and you have answered its questions.

## 4. Prompt plan, phase by phase

Paste one prompt per phase, in order. Each prompt names the requirement IDs it serves, ends by running the tools and showing their real output, and ends the phase with a commit. Between phases, read the diff and the output, then type `go phase N`.

### Phase 1 · 18:50–19:30 · Planifier, Analyser, Concevoir

```text
go phase 1 — Planifier, Analyser, Concevoir. No application code in this phase.

Functional scope (Gestion commerciale), extending the MVP:
- Roles: CUSTOMER, STAFF, ADMIN.
- Entities: Category 1-N Product; User 1-N Order; Order 1-N OrderItem N-1 Product (Order N-N Product); AuditLog.
- CRUD: categories and products (STAFF, ADMIN); users: list, change role, deactivate (ADMIN);
  orders: create, read own, cancel own (CUSTOMER); read all, change status (STAFF, ADMIN).
- Order workflow: PLACED -> PAID -> SHIPPED -> DELIVERED; PLACED or PAID -> CANCELLED.
- Dashboard (STAFF, ADMIN): revenue, orders by status, top 5 products, low stock (< 5); filters: date range, category.
- Product search on 50,000 seeded rows: text, category, price range, in stock; paginated.
- Audit log: login success/failure, order created / status changed / cancelled, product created / updated /
  deleted, role changed. No route can update or delete audit entries.
Business rules:
BR-01 stock never negative: a line above stock -> 409 OUT_OF_STOCK and nothing changes.
BR-02 unit price taken from the catalogue at order time; client prices are ignored.
BR-03 quantity 1..99 per line and 1..50 lines, else 422.
BR-04 discount on subtotal: < 100.00 EUR -> 0 %; 100.00..199.99 -> 5 %; >= 200.00 -> 10 %; rounded half-up to the cent.
BR-05 status changes follow the workflow, anything else -> 409 INVALID_TRANSITION; PAID, SHIPPED, DELIVERED only by
      STAFF or ADMIN; a CUSTOMER may cancel only their own PLACED orders.
BR-06 cancelling restocks every line; impossible after SHIPPED.
BR-07 unique email (case-insensitive), SKU and category name -> 409.
BR-08 a CUSTOMER cannot read or act on another user's order -> 404.
BR-09 a category that still has products cannot be deleted -> 409.
Quality targets: p95 < 500 ms at 20 users (list, detail), search p95 < 800 ms on 50,000 rows, error rate < 1 %;
0 unhandled high SAST/SCA/DAST finding; coverage >= 80 % on app/services; cyclomatic complexity <= 10;
axe 0 serious/critical on 5 pages; E2E green on 2 browsers; recovery after DB restart < 60 s;
clean install < 10 min on a second machine.

Write, in French:
1. docs/exigences.yaml: FR-01.. (one per §4 item), BR-01..BR-09, QR-FS/PE/CO/US/RE/SE/MA/PO-01 with targets,
   priority (P0/P1) and characteristic.
2. docs/exigences.md: Soit/Quand/Alors scenarios, at least one valid and one refusal per rule.
3. docs/plan-de-test.md: scope, approach per level, tools, environments, entry and exit criteria, KPI table,
   risks, tonight's schedule.
4. docs/cahier-de-test.md: designed cases with the fiche-2 fields (ID, objectif, règle, préconditions, données,
   étapes, attendu, obtenu = empty, verdict = empty, type). Show the techniques: partition and boundary tables for
   BR-03 and BR-04; decision table for order creation (token? body valid? product exists? stock ok? ->
   401/422/404/409/201); state-transition table for BR-05/BR-06 (every state x every event).
5. docs/conception.md: layered architecture and ER model (Mermaid), 3-line stack justification, interface map for
   integration tests (every arrow listed), section "Utilisation de Claude Code".
Reply with the list of IDs and the number of designed cases per level. Commit.
```

**You**: check that every §4 item has an FR, every rule has a refusal scenario, and the expected values come from the rules above. **Done when**: 5 documents exist; the cahier de test has at least 40 designed cases.

### Phase 2 · 19:30–21:00 · Backend features and unit tests

```text
go phase 2 — backend features and unit tests.
1. Refactor into app/api, app/services, app/models without changing behaviour; the MVP tests must still pass.
2. Add migrations db/migrations/003_roles_categories_audit.sql and 004_volume_seed.sql (50,000 products via
   generate_series, pg_trgm GIN index on lower(name)). Keep 001 and 002. Seed one user per role
   (admin@example.com, staff@example.com, demo@example.com).
3. Implement the FR and BR of docs/exigences.yaml: require_role(...) dependency, CRUD, workflow service, discount
   service, audit service (written in the same transaction as the action), dashboard query, filtered search.
4. Unit tests in backend/tests/unit, on services only (no DB, no HTTP): every CT case of docs/cahier-de-test.md
   for BR-03, BR-04, BR-05, BR-06, with pytest.mark.parametrize, test ids = case IDs, expected values copied from
   the cahier.
5. Add pytest-cov. Create `make check` = ruff + unit tests with coverage, writing reports/junit-unit.xml,
   reports/coverage.xml, reports/htmlcov/. Show the pytest and coverage summary lines.
Commit.
```

**You**: try the new routes in http://localhost:8000/docs with each role. **Done when**: unit tests green; coverage of `app/services` ≥ 80%; the 8 MVP API tests still pass.

### Phase 3 · 21:00–21:45 · Integration and API tests

```text
go phase 3 — integration and API tests.
Integration (backend/tests/integration, real PostgreSQL test database, IT-xx cases from the cahier):
- one success test and one error test per interface listed in docs/conception.md;
- data-flow test: subtotal -> discount -> total -> stock -> order rows;
- error propagation: a failure on the second write of an order leaves no order and no stock change (stub it).
API (backend/tests/api, TA-xx cases):
- order creation decision table in check order identity -> shape -> existence -> business rule
  (401, 422, 404, 409, 201), each asserting status AND body AND the real effect in the database;
- lifecycle for categories and products: 201 -> 200 -> 200 (PUT) -> 204 -> 404;
- RBAC matrix docs/rbac.yaml (every role x every route) as one parametrized test;
- access control: customer B reading or cancelling customer A's order -> 404 and nothing changes;
- concurrency: two parallel checkouts for the last units -> exactly one 201 and one 409, final stock 0.
Contract and robustness: run Schemathesis on /openapi.json with all checks. Any 500 is a defect: log it in
docs/anomalies.md, fix it, re-run the test (confirmation) and the full suite (regression).
Write reports/api-coverage.md (route x method x expected codes, obtained yes/no) with a script that reads the JUnit
files. Add these suites to `make check`. Show the pytest and Schemathesis summaries. Commit.
```

**Done when**: every interface has a success and an error test; no 500 from Schemathesis; RBAC matrix fully green.

### Break · 21:45–22:00

### Phase 4 · 22:00–22:50 · Frontend, E2E, accessibility, usability protocol

```text
go phase 4 — frontend, E2E, accessibility, usability protocol.
1. Pages: product management (STAFF, ADMIN) with field-level error messages and a confirmation dialog before
   delete; orders back-office whose buttons show only allowed transitions; dashboard with date and category
   filters; search filters on the catalogue. Hide what a role cannot do, but the API stays the enforcer.
2. Playwright in web/e2e with projects chromium, firefox and mobile (Pixel 7, chromium). Specs:
   E2E-01 customer journey (search -> detail -> cart -> login -> order -> my orders); E2E-02 out-of-stock refusal;
   E2E-03 staff moves an order PLACED -> PAID -> SHIPPED; E2E-04 admin creates then deletes a product through the
   confirmation; E2E-05 dashboard filters. Requirement IDs in titles. JUnit to reports/junit-e2e.xml.
3. Accessibility: @axe-core/playwright on 5 pages, fail on serious or critical, attach the JSON.
4. docs/utilisabilite.md: protocol for 3 to 5 participants: 3 tasks with success criteria, time on task,
   think-aloud notes, SUS questionnaire (10 items, scoring formula), consent line, empty results table.
   Do not fill any result.
Run Playwright on all projects and show the summary line. Commit.
```

**You**: book 3 participants for 10 minutes each during phase 7 (video call is fine). **Done when**: E2E green on Chromium and Firefox; axe has no serious or critical violation.

### Phase 5 · 22:50–23:30 · Portability, containers, CI

```text
go phase 5 — portability, containers and CI.
1. backend/Dockerfile (python:3.13-slim, non-root user, HEALTHCHECK on /api/health) and web/Dockerfile (Node build
   stage -> nginx serving dist and proxying /api; headers CSP, X-Content-Type-Options, frame-ancestors,
   Referrer-Policy).
2. docker-compose.yml with db, api, web: healthchecks, depends_on service_healthy, restart: unless-stopped, every
   port and secret from .env; .env.example documented; no secret committed. One command:
   docker compose up -d --build --wait.
3. scripts/installation-propre.sh: clone into a temp folder, copy .env.example, compose up --wait, run
   scripts/smoke.sh, print the elapsed time; log to reports/portabilite/installation-<host>.log.
4. docs/installation.md in French for someone who has never seen the project: prerequisites, the 5 commands, how
   to run each test layer, troubleshooting.
5. .github/workflows/ci.yml ordered fastest to slowest (fiche 1): format + SAST -> unit -> integration, API, SCA
   -> E2E -> performance smoke + DAST baseline; upload reports as artifacts.
6. Hadolint on both Dockerfiles; Trivy image scan of both images; outputs to reports/sca/.
Run the clean-install script and show the end of its log. Commit.
```

**You**: send the repo (zip or Git remote) to the teammate who will install it on a second machine during phase 7. **Done when**: the clean install finishes under 10 minutes and the smoke script passes on the containers.

### Phase 6 · 23:30–00:30 · Security: SAST, SCA, DAST

```text
go phase 6 — security (fiche 4). Every scan targets this machine only.
0. Write docs/securite/autorisation.md: owner, scope (the local Docker stack), date, scan types. I will sign it.
SAST: Semgrep (p/owasp-top-ten, p/python, p/typescript), Bandit on backend/app, gitleaks on the full Git history.
      JSON reports to reports/sast/.
SCA: pip-audit, npm audit --omit=dev, Trivy fs on the repo; CycloneDX SBOM with Syft for backend and web,
     transitive dependencies included; licences with pip-licenses and license-checker. Reports to reports/sca/.
DAST: on the running containers, ZAP baseline (passive) on http://localhost:<web port>, then ZAP API scan (active)
      with the OpenAPI file against the API. Reports to reports/dast/.
Manual attacks as tests (backend/tests/security and web/e2e, SEC-xx): SQL injection in product search; stored XSS
in a product name (Playwright: the script shows as text and never runs); access control with another user's order
id; session (expired token -> 401; token issued before a role change).
Then write docs/securite/triage.md, one row per finding: tool, rule/CWE/CVE, severity, true / false / to watch,
reason, decision (fix / update / replace / accept), reachability for CVEs, status after re-run. Fix every true
high finding, update vulnerable packages to the highest fixed version and re-run the regression suite, then rescan.
Show before/after counts read from the report files. Ask me before accepting any risk. Commit.
```

**You**: sign `autorisation.md`; decide on every risk Claude Code proposes to accept. **Done when**: no unhandled high finding in SAST, SCA or DAST; every finding has a written decision; the 4 manual attacks are refused.

### Phase 7 · 00:30–01:15 · Performance and reliability

```text
go phase 7 — performance and reliability.
Performance (perf/k6, PERF-xx): smoke.js (1 user, 30 s); load.js (20 users, 5 min: list, detail, search; login
once in setup()); search.js (filters on 50,000 products). Thresholds from docs/exigences.yaml; handleSummary writes
reports/perf/*.json. Sample `docker stats --no-stream` every 10 s during load.js into reports/perf/ressources.csv.
Write the machine (CPU, RAM, OS, Docker version) to reports/perf/environnement.txt. If a threshold fails, find the
cause (EXPLAIN ANALYZE), fix it, re-run, and keep both runs.
Reliability (backend/tests/reliability and scripts/fiabilite/, REL-xx):
- /api/health checks the database and answers 503 while it is down;
- REL-01 restart PostgreSQL during a 2-minute k6 run: no 500 outside the outage window, no lost or half-written
  order (consistency SQL), recovery time measured by polling /api/health;
- REL-02 kill the API container: the restart policy brings it back; measure the time;
- REL-03 a failure between two writes of one order rolls everything back;
- REL-04 the same order submitted twice at once does not oversell.
Results to reports/reliability/. Show the k6 threshold lines and the measured recovery times. Commit.
```

**You**: run the usability sessions now (protocol in `docs/utilisabilite.md`) and write raw notes per participant. The teammate runs the second-machine install with `docs/installation.md` and sends you the log. **Done when**: k6 thresholds met on this machine, or a deviation written with its cause; recovery under 60 s.

### Phase 8 · 01:15–01:45 · Maintainability and usability results

```text
go phase 8 — maintainability, then usability results.
Maintainability (reports/maintenabilite/): ruff lint + format check; radon cc -s -a and xenon --max-absolute B on
backend/app; import-linter contract api -> services -> models with no reverse import; coverage >= 80 % on
app/services; Hypothesis property test for BR-04 (discount never negative, never above subtotal, never decreases
when the subtotal grows); mutmut on the pricing and order services, timeboxed to 15 minutes: report the score and
the surviving mutants, and kill the ones you can with sharper assertions.
Usability: the raw session notes and the teammate's install log are pasted below. Put the notes in
docs/utilisabilite.md and compute task success rate, median time per task and SUS per participant and on average
with a script, not by hand. List the problems found, fix the top 2, re-run E2E. Save the install log as
reports/portabilite/installation-machine2.log.
<paste notes and log here>
Commit.
```

**Done when**: complexity and coverage targets met; usability results computed from the notes; second-machine log saved.

### Phase 9 · 01:45–02:30 · Clôturer: evidence and reports

```text
go phase 9 — Clôturer: evidence and reports, in French.
1. tools/trace.py reads docs/exigences.yaml and every report in reports/ (JUnit XML with req properties or IDs in
   test names; k6 JSON thresholds; Bandit, Semgrep, pip-audit, Trivy and ZAP JSON; manual YAML in
   docs/preuves/manuel/) and writes docs/tracabilite/matrice.md and .csv with the columns exigence, condition de
   test, scénario, cas de test, script, outil, verdict, preuve, commit. Exit code 1 if a P0 requirement is NOT RUN
   or FAIL.
2. Fill "obtenu" and "verdict" in docs/cahier-de-test.md from the reports with a script.
3. docs/conformite.md: for each of the 8 characteristics: sub-characteristics (Chapitre I), requirement, target,
   method and tool version, measured value copied from its report, verdict, evidence link, limits. Add a
   quality-in-use section and a short ISO 25010:2011 -> 2023 mapping. Missed targets go in an "Écarts" table.
4. docs/rapport-de-test.md (fiche 1, Clôturer): scope tested, cases per level, defects found and fixed from
   docs/anomalies.md, exit criteria met or not, lessons learned.
5. Finish docs/conception.md (final architecture, data model, interface map, how Claude Code was used and reviewed).
6. Freeze the evidence with shell commands: copy reports/ to docs/preuves/v1.0/, write manifest.json (commit SHA,
   date, tool versions) and sha256sums.txt.
Show the matrix totals by verdict. Commit.
```

**Done when**: the matrix has no P0 requirement at NOT RUN or FAIL (or each has an écart); every number in `conformite.md` links to a file.

### Phase 10 · 02:30–03:00 · Independent check, demo, tag

```text
go phase 10 — independent verification and demo.
Start a subagent that has not seen this session's work. It clones the repo into a temp folder, follows
docs/installation.md exactly, runs every test layer, regenerates the matrix and compares it with
docs/tracabilite/matrice.csv. Then, for each number in docs/conformite.md, it looks for that number in the raw file
the link points to, and lists any number it cannot find.
Write docs/demo.md: a 12-minute soutenance script (business journey with a role switch; Playwright on chromium and
firefox in headed mode; a 1-minute k6 run with thresholds; one matrix row followed to its raw report; one écart
explained). Fix what the check found, then tag v1.0. Show the subagent's report.
```

**You**: read `conformite.md` and `rapport-de-test.md` end to end; rehearse the demo once. **Done when**: the subagent finds no unsupported number; tag `v1.0` exists.

## 5. Evidence and deliverables

Every deliverable is either generated from the tools' report files or points to them. A reviewer should be able to start from any requirement and reach a raw file and a commit in three clicks.

### Final `docs/` layout

```text
docs/
├── cahier-des-charges.pdf, cours/            # subject (input)
├── exigences.yaml, exigences.md              # FR, BR, QR + Soit/Quand/Alors        (phase 1)
├── plan-de-test.md                           # Planifier                            (phase 1)
├── cahier-de-test.md                         # Concevoir, then results by script    (phases 1, 9)
├── conception.md                             # architecture, data model, stack      (phases 1, 9)
├── anomalies.md                              # defect log: found, fixed, confirmed  (phases 2–8)
├── utilisabilite.md                          # protocol and results                 (phases 4, 8)
├── securite/autorisation.md, triage.md       # fiche 4                              (phase 6)
├── installation.md                           # install guide                        (phase 5)
├── tracabilite/matrice.md, matrice.csv       # generated                            (phase 9)
├── conformite.md                             # ISO 25010 conformity report          (phase 9)
├── rapport-de-test.md                        # Clôturer                             (phase 9)
├── demo.md                                   # soutenance script                    (phase 10)
├── journal.md                                # what each phase did                  (all)
└── preuves/v1.0/                             # frozen reports + manifest + sha256   (phase 9)
```

### Matrix format (one row per test case; values come from the reports)

| Exigence | Condition de test | Scénario | Cas de test | Script | Outil | Verdict | Preuve | Commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BR-04 | subtotal at the 100.00 € boundary | Soit un panier de 100,00 €… | CT-12 | `tests/unit/test_pricing.py::test_discount[CT-12]` | pytest | {from JUnit} | `preuves/v1.0/junit-unit.xml` | {sha} |
| QR-PE-01 | 20 concurrent users, 5 min | Soit 20 utilisateurs… | PERF-02 | `perf/k6/load.js` | k6 | {from k6 JSON} | `preuves/v1.0/perf/load.json` | {sha} |

### Conformity section template (`docs/conformite.md`, one per characteristic)

```markdown
## {n}. {Caractéristique} — sous-caractéristiques : {liste du Chapitre I}
**Exigence** : {QR-xx-01} — {énoncé}
**Cible** : {seuil chiffré}
**Méthode** : {outil + version, configuration, environnement}
**Résultat mesuré** : {valeur recopiée du rapport} — {atteint / non atteint}
**Preuve** : [{fichier}](preuves/v1.0/...) · commit {sha}
**Écart éventuel** : {cause, impact, action}
**Limites** : {ce que cette preuve ne démontre pas}
```

### What the reviewer checks against the course

- **Fiche 1**: the six process outputs exist (plan, conditions, cahier, scripts, verdicts, report); defects show a confirmation and a regression run.
- **Fiche 2**: technique tables are visible in the cahier; coverage reports statements and branches; API tests check body and effect, not only the status code.
- **Fiche 4**: every alert has a decision and a reason; SCA covers transitive dependencies; DAST was authorized and stayed local; findings were rescanned.
- **Chapitre I**: each characteristic is argued through its sub-characteristics, not only one metric.

## 6. Checkpoints, fallbacks and final checklist

Three checkpoints decide what to cut. If you are more than 20 minutes late at a checkpoint, apply its cuts at once rather than hoping to catch up. P0 items are never cut; they become documented deviations if they fail.

### Checkpoints

| Checkpoint | Expected state | Cuts if late |
| --- | --- | --- |
| CP1 · 21:00 | Phase 2 committed: roles, CRUD, workflow, audit, dashboard, search, unit tests green | Dashboard: 2 indicators + 1 filter. User management: role change only. Audit: logins and orders only |
| CP2 · 00:30 | Phase 6 committed: all scans run and triaged | Merge `search.js` into `load.js`. Reliability: REL-01 and REL-03 only. Mutation testing moved to Écarts |
| CP3 · 02:30 | Phase 9 committed: matrix, conformity and test reports generated | Hard freeze: no new feature or test. Only fixes to reports and the demo |

### Fallbacks

| Problem | What to do |
| --- | --- |
| A tool will not run (image pull fails, ZAP cannot reach the stack) | Try once with another option (`host.docker.internal`, the `--network host` flag on Linux, an equivalent tool from the course sheet). Otherwise write *non disponible* + procedure + reason in the conformity report. Never simulate |
| No usability participants tonight | Run the sessions tomorrow before submission. Until then the report says *en attente* and gives the protocol |
| No second machine tonight | Run the clean-install script on your machine as an interim result. The teammate's install is done tomorrow and added as a separate log |
| Claude Code's context fills up | `/compact`, or a new session started with: "Read CLAUDE.md and docs/journal.md, then continue with phase N." The journal is the memory between sessions |
| Usage limit reached mid-phase | Stop at the last commit. The journal and the phase prompts let you resume from that point |
| A KPI target is missed | Keep the run, write the deviation (measured value, cause, action). An honest écart is better than an unproven pass |

### Final checklist before submission

- [ ] §4: 3 roles, 4+ related entities with full CRUD, workflow with rules, dashboard with filters, search on 50,000 rows, audit log, 9 business rules, each traced
- [ ] §6: each of the 8 characteristics has a requirement, a test or tool that ran, and an evidence file
- [ ] §7: every test layer has a runnable suite and a generated report (unit, integration, API, E2E, performance, reliability, SAST, SCA, DAST, quality, compatibility, portability)
- [ ] §8: code with history, conception, matrix, test suites and reports, conformity report, install guide, demo script
- [ ] Fiche 1: plan de test, cahier de test, rapport de test, anomalies with confirmation and regression runs
- [ ] Fiche 2: technique tables in the cahier; coverage of statements and branches; API tests check body and real effect
- [ ] Fiche 4: authorization signed; every finding triaged with a reason; rescan after fixes; SBOM and licences
- [ ] Chapitre I: conformity argued through sub-characteristics, plus quality in use
- [ ] Golden rule: every number in the reports is found in a raw file under `docs/preuves/v1.0/`; anything that could not run is marked *non disponible*
- [ ] Tag `v1.0` pushed; demo rehearsed once
