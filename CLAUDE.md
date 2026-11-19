# Project: Gestion commerciale — ISO/IEC 25010 conformity

## Context
FastAPI + SQLAlchemy + PostgreSQL + React/TypeScript + JWT. Graded on ISO/IEC 25010 conformity.
Subject: docs/cahier-des-charges.pdf. Course: docs/cours/*.pdf. Tonight's plan: docs/plan-de-la-nuit.md.
Claude Code kit (skills, subagents, hooks): docs/kit-claude-code.md.
Deliverable documents (docs/*.md) are written in French. Code, identifiers and commit messages in English.

## Golden rule (non-negotiable)
- Never write a result, number, coverage figure or verdict that did not come from a real run.
  Numbers come only from files the tools wrote in reports/.
- If a tool cannot run here: write "non disponible", the procedure and the reason. Never simulate output.
- Never edit reports/ or docs/preuves/ by hand (a hook and deny rules enforce it; tools run through the shell
  still write there normally).
- Reviews by Claude (/security-review, code-review, subagents) are "revue de code", recorded in
  docs/securite/triage.md or docs/journal.md, never presented as SAST, SCA or DAST tool output.

## Oracle
- Expected results come from the rule (docs/exigences.yaml, docs/exigences.md), never from the code under test.
- When the rule does not decide a case, write "NON SPÉCIFIÉ" and ask.
- When a test fails, re-read the rule: either the expectation is wrong (say so) or it is a defect.
  A defect goes in docs/anomalies.md (/anomalie); fix it, re-run that test (confirmation), then the full suite (regression).

## Traceability
- Every test carries its requirement IDs: pytest @pytest.mark.req("BR-01"); Playwright "@BR-01" in the title; k6 tag req.
- Test case IDs: CT-xx unit, IT-xx integration, TA-xx API, E2E-xx, SEC-xx, PERF-xx, REL-xx, UX-xx, PORT-xx.
- Never invent a requirement ID; propose the missing requirement instead.

## Writing tests
- Unit tests are F.I.R.S.T. and Arrange-Act-Assert, with valid cases AND expected-failure cases.
- Techniques: equivalence partitions, boundary values, decision tables, state transitions.
- API tests check status + body + real effect, in the order identity → shape → existence → business rule. A 500 is always a defect.
- Never delete, skip or weaken a test or an assertion to make CI pass.
- Exploratory sessions with the Playwright MCP are not evidence; only .spec.ts files run by Playwright Test count.

## Architecture
app/api (routes) → app/services (business rules) → app/models (SQLAlchemy). Cyclomatic complexity ≤ 10.
Configuration only through environment variables. No secret in the code.

## Security
Active scans (ZAP) only against http://localhost (authorization in docs/securite/autorisation.md).
Every alert is triaged true / false / to watch with a written reason. Ask me before accepting any risk.

## This machine (Windows 11)
- Postgres in Docker is on host port **5433**: a native Windows PostgreSQL service holds 5432.
- Backend virtualenv: backend/.venv/Scripts/ (python, pytest, ruff). Use `python`, not `python3`.
- GNU make 4.4.1 is installed per-user (winget `ezwinports.make`). If `make` is not on PATH in a shell, prepend
  `$LOCALAPPDATA/Microsoft/WinGet/Packages/ezwinports.make_Microsoft.Winget.Source_8wekyb3d8bbwe/bin`.
- `make check` = lint (ruff, oxlint, tsc) + docs (tools/check_docs.py traceability) + tests.
- Security exit criterion (accepted in P0, from TP3): 0 High, 0 unjustified Medium, Low justified.
- Semgrep and mutmut run in Docker containers (not native on Windows).
- PDFs are read with `pdftotext -layout`.

## Claude Code tooling
Skills: /test-design, /gen-tests, /anomalie, /security-triage, /trace, /phase-done.
Subagents: test-reviewer (before each phase commit), evidence-auditor (before submission).

## End of every phase
Run `make check`, show its real output, append to docs/journal.md (done, evidence files, gaps),
then `git commit -m "phase N: ..."`. Then stop and wait for "go phase N+1".
