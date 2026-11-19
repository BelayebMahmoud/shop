# Claude Code Integration Kit for the ISO 25010 Project

Nov 19, 2026 · @Mahmoud

## Recommendation at a glance

Install almost nothing and write a little. Six project skills, two subagents and three hooks (all plain files in the repo) do most of the work. On top of that come four official plugins, one built-in command and one optional MCP server. Everything else is optional or would add risk to the golden rule.

| Priority | Component | Type | Source | Tonight's phase | What it does for this project |
| --- | --- | --- | --- | --- | --- |
| P0 | `CLAUDE.md` + 3 hooks | Built-in | Write it (section 4) | Setup, all | Fixes the oracle and golden rules; blocks edits to evidence; formats Python after each edit; reloads the journal on resume |
| P0 | `/test-design`, `/gen-tests` | Project skills | Write them (section 3) | 1–4 | Turn a requirement ID into technique tables (fiche 2), then into tagged tests that are seen failing first |
| P0 | `/anomalie`, `/phase-done` | Project skills | Write them (section 3) | 2–10 | Log defects with confirmation and regression runs (fiche 1); close each phase the same way |
| P0 | `/security-triage`, `/trace` | Project skills | Write them (section 3) | 6, 9 | Triage SAST/SCA/DAST findings with written decisions (fiche 4); build and read the traceability matrix |
| P0 | `test-reviewer`, `evidence-auditor` | Project subagents | Write them (section 4) | 2–4, 10 | A fresh context reviews tests against the oracle rule and checks that every number in the reports exists in a raw file |
| P1 | `/security-review` | Built-in command | Claude Code | 6 | An extra security review of pending changes, recorded as a code review, never as tool evidence |
| P1 | `pyright-lsp`, `typescript-lsp` | Official plugins | `claude-plugins-official` | 2–4 | Live type errors and go-to-definition while Claude edits Python and TypeScript |
| P1 | `code-review`, `claude-code-setup` | Official plugins | `claude-plugins-official` | Setup, 3, 4 | Parallel review of a change set; a read-only scan that suggests further hooks, skills and MCP servers |
| P1 | Playwright MCP | MCP server | Microsoft (`@playwright/mcp`) | 4, 8 | Lets Claude drive a real browser for exploratory testing and for writing page objects |
| P2 | `webapp-testing` | Ready-made skill | `anthropics/skills` | 4 | Python Playwright patterns (server lifecycle, screenshots, console logs) |
| P2 | `docx` / `xlsx` skills | Ready-made skills | `anthropics/skills` | 9 | Only if the supervisor wants Word or Excel copies of the reports |
| Skip | PostgreSQL MCP server | MCP server | Community | — | `psql` through Bash does the same with less setup and no third-party code |
| Skip | Claude GitHub Actions | CI | Anthropic | — | Needs an API key and a remote repository, and adds nothing to the §8 deliverables tonight |

## 1. Built-in Claude Code features to use

Everything in this section ships with Claude Code: you only add files to the repository. Behaviour below was checked against the current documentation on 19 November 2026.

| Feature | What the documentation says | How this project uses it |
| --- | --- | --- |
| **Skills** | A skill is `.claude/skills/<name>/SKILL.md` in the project (commit it to share). Custom commands and skills are now one system: `.claude/commands/x.md` and `.claude/skills/x/SKILL.md` both create `/x`. [Skills docs](https://code.claude.com/docs/en/skills) | Six project skills (section 3), versioned with the code, so the method is part of the deliverable |
| **Skill frontmatter** | Useful fields: `description` (Claude uses it to decide when to load the skill), `disable-model-invocation` (only you can run it), `allowed-tools` (no prompt for those tools during the turn), `arguments` (named `$name` values), `context: fork` with `agent` (runs in a forked subagent), `paths` (limits auto-loading). [Skills docs](https://code.claude.com/docs/en/skills) | `/phase-done` and `/trace` are manual-only; `/test-design` loads automatically when you mention a requirement ID |
| **Dynamic context** | `` !`command` `` runs before Claude sees the skill and its output replaces the placeholder. If the command fails, the whole skill invocation aborts. [Skills docs](https://code.claude.com/docs/en/skills) | `/trace` injects the matrix totals. Commands that can exit non-zero (`trace.py` on a gap) end with `\|\| true` so the skill still runs |
| **Bundled skills** | Claude Code ships `/code-review` (alias `/review`), `/debug`, `/batch`, `/loop`, `/run`, `/verify` among others. [Skills docs](https://code.claude.com/docs/en/skills) | `/debug` on a failing test; `/code-review` before each phase commit |
| **Subagents** | Markdown files in `.claude/agents/` with frontmatter such as `name`, `description`, `tools`, `model`. File-based subagents also accept fields like `disallowedTools`, `permissionMode`, `mcpServers`, `hooks` and `maxTurns`. [Subagents docs](https://code.claude.com/docs/en/sub-agents) | `test-reviewer` and `evidence-auditor` (section 4) review in a context that did not write the code |
| **Hooks** | Commands that run on events such as `PreToolUse`, `PostToolUse`, `SessionStart` and `Stop`, configured in `.claude/settings.json` | Block edits to evidence; format Python after edits; reload the journal at session start |
| **`/security-review`** | A built-in command that reviews the pending changes for vulnerabilities. You can customise it by copying `security-review.md` from Anthropic's repository into `.claude/commands/`. [claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | Phase 6, after Semgrep and Bandit. Its findings go in `triage.md` as "revue de code orientée sécurité" (fiche 4), never as SAST tool output |
| **Headless mode** | `claude -p` runs non-interactively; `--output-format json` and `--json-schema` give machine-readable output. `--bare` skips hooks, skills, plugins, MCP servers and `CLAUDE.md`, and needs `ANTHROPIC_API_KEY` because it does not use your subscription login. [Headless docs](https://code.claude.com/docs/en/headless) | Optional: a scripted review in `make check`. Do not use `--bare` there, or the project rules in `CLAUDE.md` are not loaded |
| **Plugins** | The official marketplace `claude-plugins-official` is available automatically; install with `/plugin install <name>@claude-plugins-official`. [Plugin docs](https://code.claude.com/docs/en/discover-plugins) | Four official plugins (section 2) |

## 2. Ready-made plugins, skills and MCP servers

Four official plugins and one MCP server are worth installing; the rest are optional. Prefer the official marketplace: its plugins are maintained by Anthropic, while third-party servers run code you have not reviewed.

### Official plugins (`claude-plugins-official`)

Descriptions follow a 2026 catalogue of the official marketplace ([DesignRevision](https://designrevision.com/blog/official-claude-code-plugins)); run `/plugin` for the live list.

| Plugin | Function | Install | Requires | Use in this project |
| --- | --- | --- | --- | --- |
| `pyright-lsp` | Live Python type errors and go-to-definition | `/plugin install pyright-lsp@claude-plugins-official` | The `pyright-langserver` binary: `npm install -g pyright` | Phases 2–3: catches type mistakes in services and schemas before tests run |
| `typescript-lsp` | The same for TypeScript | `/plugin install typescript-lsp@claude-plugins-official` | `npm install -g typescript-language-server typescript` | Phase 4: React pages and Playwright specs |
| `code-review` | Parallel agents review a change set for bugs, missed edge cases and style | `/plugin install code-review@claude-plugins-official` | Nothing extra | Before each phase commit, alongside `test-reviewer` |
| `claude-code-setup` | Scans the repository read-only and recommends hooks, skills, MCP servers and subagents | `/plugin install claude-code-setup@claude-plugins-official` | Nothing extra | Once at setup, to check this kit against your actual repo |
| `security-guidance` | Reviews Claude's diffs for injection, XSS and exposed secrets | Check `/plugin`; the catalogue lists it as enabled by default | Nothing extra | Keep it on: it supports the SAST obligations of fiche 4 while code is written |
| `playwright` | Partner plugin that pre-configures the Playwright MCP server | `/plugin install playwright@claude-plugins-official` | Node 18+ | Alternative to the manual MCP setup below; install one, not both |
| `skill-creator` | Interviews you about a workflow and scaffolds or evaluates a skill | `/plugin install skill-creator@claude-plugins-official` | Nothing extra | Optional: refine the six skills in section 3 after tonight |

### Anthropic example skills (`anthropics/skills`)

The repository can be added as a plugin marketplace with `/plugin marketplace add anthropics/skills` ([listing](https://www.mdskills.ai/skills/webapp-testing)).

| Skill | Function | Compatibility | Verdict |
| --- | --- | --- | --- |
| `webapp-testing` | Toolkit for testing local web apps with Python Playwright: server lifecycle helpers, screenshots, console logs. Apache-2.0 licence ([skill page](https://moltchat-agent-commons.onrender.com/api/v1/pages/skill-anthropic-webapp-testing)) | Needs `pip install playwright` and `playwright install`. Your E2E suite is TypeScript Playwright, so use it only for quick exploratory scripts | P2 |
| `docx`, `xlsx`, `pdf` | Create and edit Word, Excel and PDF files | Python libraries installed by the skill | P2: only if a Word or Excel copy of the reports is required. The Markdown reports stay the source |

### MCP servers

| Server | Function | Setup | Compatibility | Verdict |
| --- | --- | --- | --- | --- |
| Playwright MCP (Microsoft) | Drives Chromium, Firefox or WebKit through accessibility snapshots rather than screenshots ([Playwright docs](https://playwright.dev/docs/getting-started-mcp)) | `claude mcp add playwright --scope project -- npx @playwright/mcp@latest --headless` (server flags go after `--`) | Node 18+; `--scope project` writes `.mcp.json`, shared through Git | P1 for exploratory testing (fiche 1, experience-based techniques) and for drafting page objects. Tests that count as evidence must still be `.spec.ts` files run by Playwright Test |
| PostgreSQL MCP | Schema exploration and read-only queries | Community servers only; the reference server is reported as archived ([Peliqan overview](https://peliqan.io/blog/postgres-mcp/)) | Varies by server | Skip: Claude Code already runs `psql` and `EXPLAIN ANALYZE` through Bash with the project's own credentials |

### Not recommended tonight

- **`anthropics/claude-code-security-review` GitHub Action**: needs an API key secret and a hosted repository, and its README warns it is not hardened against prompt injection, so it should only review trusted PRs ([repository](https://github.com/anthropics/claude-code-security-review)). Use the local `/security-review` command instead.
- **`anthropics/claude-code-action`**: useful for team PR reviews later, but adds nothing to the §8 deliverables tonight.

## 3. Project-specific skills to create

Six skills encode the course method so every phase applies it the same way. Each is one file at `.claude/skills/<name>/SKILL.md`, committed with the code. The deliverable documents they write are in French; the instructions are in English for Claude.

| Skill | Invoked by | Course source | Phases |
| --- | --- | --- | --- |
| `/test-design <REQ-ID>` | You or Claude (auto when a requirement needs cases) | Fiche 2: partitions, boundaries, decision tables, state transitions | 1–4 |
| `/gen-tests <REQ-ID> <level>` | You or Claude | Fiche 2: F.I.R.S.T., AAA, API checks; fiche 1: oracle | 2–4 |
| `/anomalie <test-id>` | You or Claude | Fiche 1: erreur, défaut, défaillance; confirmation and regression | 2–8 |
| `/security-triage` | You only | Fiche 4: true / false / to watch; update, replace or accept | 6 |
| `/trace` | You only | Fiche 1: exigence → … → verdict chain | 9, 10 |
| `/phase-done <N>` | You only | Fiche 1: Exécuter → Clôturer for each phase | All |

### `.claude/skills/test-design/SKILL.md`

```markdown
---
name: test-design
description: Design test cases for one requirement ID (FR, BR or QR) with the fiche-2 techniques and add them to docs/cahier-de-test.md. Use when a requirement needs test cases before any test code is written.
argument-hint: <REQ-ID>
arguments: [req]
allowed-tools: Read Grep Edit
---
Design the test cases for $req.

1. Read $req in docs/exigences.yaml and its Soit/Quand/Alors scenarios in docs/exigences.md.
   If either is missing, stop and say so.
2. Choose techniques from the shape of the rule (fiche 2):
   - a threshold or range -> equivalence partitions + boundary values (last value before and first after each boundary);
   - several combined conditions -> decision table, one column per rule;
   - an object that changes state -> state-transition table, every state x every event, valid and forbidden;
   - an API route -> checks in the order identity -> shape -> existence -> business rule.
3. Show the technique table first. Then add one row per case to docs/cahier-de-test.md with the fields:
   ID, objectif, règle couverte, préconditions, données d'entrée, étapes, résultat attendu,
   résultat obtenu (empty), verdict (empty), type (valide / échec attendu).
4. Expected results come only from the rule. When the rule does not decide a case, write "NON SPÉCIFIÉ"
   and list it as a question. Never take the answer from the code.
5. Write in French. Reply with the number of cases per technique.
```

### `.claude/skills/gen-tests/SKILL.md`

```markdown
---
name: gen-tests
description: Write automated tests for cases already designed in docs/cahier-de-test.md, tagged with requirement and case IDs, and prove each test fails when the rule is broken. Use after /test-design.
argument-hint: <REQ-ID> <unit|integration|api|e2e>
arguments: [req, level]
---
Write the $level tests for the cases of $req in docs/cahier-de-test.md.

Rules:
- One test per case. Test id = case ID. pytest: @pytest.mark.req("$req"); Playwright: "@$req" in the title.
- Arrange-Act-Assert. Assert the expected result copied from the cahier, never a value read from the code.
- API tests assert status, body AND the real effect (database state or a follow-up GET). A 500 is a defect.
- No fixed sleeps, no dependency on test order or on data left by another test.
Then:
1. Run the new tests and show the summary line.
2. Break the rule in the code on purpose (for example change >= into >), run the tests, show that at least one
   fails, restore the code, run them again.
3. If a test fails because the code is wrong, run /anomalie instead of changing the expectation.
```

### `.claude/skills/anomalie/SKILL.md`

```markdown
---
name: anomalie
description: Log a defect revealed by a failing test in docs/anomalies.md, fix it, then run the confirmation test and the regression suite. Use whenever a test fails because the code is wrong, not the expectation.
argument-hint: <test-id>
arguments: [test]
---
The test $test failed.
1. Re-read the rule behind it. If the expected result is wrong, say so and stop: that is a test defect.
2. Otherwise add an entry to docs/anomalies.md (in French): ANO-xx, date, exigence, test, étapes de
   reproduction, résultat attendu, résultat obtenu, gravité, erreur (the human mistake), défaut (where in the
   code), défaillance (what a user would see).
3. Fix the defect with the smallest change.
4. Confirmation: re-run $test alone and record its result.
5. Non-régression: run `make check` and record the summary line.
6. Mark the entry "Corrigée" with both results and the commit SHA.
```

### `.claude/skills/security-triage/SKILL.md`

```markdown
---
name: security-triage
description: Triage every SAST, SCA and DAST finding into docs/securite/triage.md with a written decision, following fiche 4. Use after the security scans have run.
disable-model-invocation: true
---
## Report files available now
!`ls reports/sast reports/sca reports/dast 2>/dev/null || true`

For each finding in those files (read the JSON itself, never a summary):
1. One row in docs/securite/triage.md: outil, règle / CWE / CVE, fichier ou paquet, gravité,
   vraie / fausse / à surveiller, justification, décision, statut après relance.
2. SAST: a false positive is justified in writing, never silently removed. A true finding is fixed, then the
   tool is re-run.
3. SCA: transitive dependencies count too. Decide: update (to the highest "fixed in" version listed for that
   package), replace, or accept with reachability (is the vulnerable code actually called?). Re-run the tests
   after any update.
4. DAST: only results from the local stack named in docs/securite/autorisation.md.
5. Never accept a risk yourself: list the candidates and ask me.
6. End with before/after counts by severity, read from the re-run report files.
```

### `.claude/skills/trace/SKILL.md`

```markdown
---
name: trace
description: Regenerate the traceability matrix from the test reports and list every requirement that is not at PASS.
disable-model-invocation: true
allowed-tools: Bash(python tools/trace.py *) Read
---
## Matrix run
!`python tools/trace.py --requirements docs/exigences.yaml --reports reports --out docs/tracabilite 2>&1 | tail -25 || true`

From the output above and docs/tracabilite/matrice.csv:
1. List every P0 requirement that is NOT RUN, FAIL or PARTIAL, grouped by characteristic, with the smallest
   next step for each.
2. List test IDs that reference an unknown requirement.
3. Quote statuses exactly as the CSV has them. Never edit the matrix: it is regenerated, not written.
```

### `.claude/skills/phase-done/SKILL.md`

```markdown
---
name: phase-done
description: Close one phase of tonight's plan by running the checks, updating the journal, reviewing and committing.
argument-hint: <phase-number>
arguments: [n]
disable-model-invocation: true
allowed-tools: Bash(make *) Bash(git add *) Bash(git commit *) Bash(git status *) Read Edit
---
Close phase $n.
1. Run `make check` and show its real summary lines.
2. Append to docs/journal.md (in French): phase $n, heure, ce qui a été fait, fichiers de preuve produits
   (paths under reports/), écarts, points ouverts.
3. Ask the test-reviewer subagent to review the test files changed in this phase. If it reports a blocker,
   stop before committing and show it.
4. git add -A, then git commit -m "phase $n: <one-line summary>".
5. Stop and wait for "go phase <next>".
```

Usage examples: `/test-design BR-04`, then `/gen-tests BR-04 unit`; `/anomalie TA-07`; `/phase-done 3`. The `|| true` in the two injected commands matters: if an injected command fails, the whole skill invocation aborts, and `trace.py` deliberately exits 1 when a requirement has a gap.

## 4. Subagents and hooks

Two read-only subagents give the reviews a context that did not write the work. Three hooks enforce rules mechanically instead of relying on the prompt. The three hook scripts below were run on sample input in a scratch repository; the settings file and the subagents were not run inside Claude Code.

### `.claude/agents/test-reviewer.md`

```markdown
---
name: test-reviewer
description: Reviews new or changed tests against the course rules (oracle from the rule, valid and expected-failure cases, Arrange-Act-Assert, no order dependence, requirement tags). Use after tests are written and before a phase is committed.
tools: Read, Grep, Glob, Bash
model: inherit
---
You review tests. You never edit files.
Scope: test files listed by `git diff --name-only HEAD` and untracked test files from `git status --porcelain`.
For each test, check:
1. Oracle: the expected value matches docs/exigences.yaml or docs/cahier-de-test.md, not a value taken from the code.
2. Would the test still pass if the rule were deleted? (status-only assertions, asserting a mock's own return value)
3. Each valid case has an expected-failure case for the same rule.
4. API tests check status + body + real effect.
5. F.I.R.S.T.: no sleep, no network outside localhost, no dependence on order or leftover data.
6. Requirement ID and case ID are present and exist.
Output one table: file | test | problem | severity (blocker / major / minor) | fix.
Then list the requirement IDs whose coverage you judge insufficient.
```

### `.claude/agents/evidence-auditor.md`

```markdown
---
name: evidence-auditor
description: Independently checks that every number, verdict and claim in docs/conformite.md, docs/rapport-de-test.md and docs/tracabilite/matrice.md exists in the raw report file it cites. Use before submission.
tools: Read, Grep, Glob
model: inherit
---
You did not produce this work and must not trust it. You never edit files.
For every number, percentage, count or verdict in the three documents:
1. Open the file the sentence links to (under docs/preuves/v1.0/ or reports/).
2. Find the value in the raw file (JSON, XML, CSV or log).
3. Record: document, line, claimed value, file, value found, OK / NOT FOUND / DIFFERENT.
Also check that each of the 8 characteristics cites at least one raw file, that every tool marked
"non disponible" has a procedure, and that docs/preuves/v1.0/sha256sums.txt lists every evidence file.
Output the table, then one line: claims checked, claims not supported.
```

Phase 10 then becomes: "Use the evidence-auditor subagent on the final documents and fix everything it reports."

### Exploratory testing with Playwright MCP (no file needed)

Once the Playwright MCP server or plugin is installed, the course's experience-based technique is one prompt:

```text
Use the Playwright MCP browser on http://localhost:<web port>. Spend 15 minutes on exploratory testing of the
checkout and the back-office, as a heuristic tester: empty fields, 0, -1, huge numbers, accents, Arabic text,
back button during payment, two tabs, expired session. Write each observation in docs/exploratoire.md (in French)
with steps, expected, observed. Every real defect becomes an /anomalie and a new automated test.
```

### Hooks in `.claude/settings.json`

Merge this `hooks` block into the settings file from tonight's plan (the permissions block stays as it is).

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/protect_evidence.py" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/format_python.py" }] }
    ],
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "python3 .claude/hooks/session_context.py" }] }
    ]
  }
}
```

```python
# .claude/hooks/protect_evidence.py — PreToolUse: exit code 2 blocks the edit and tells Claude why
import json, sys
path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "").replace("\\", "/")
if "/reports/" in path or "docs/preuves/" in path:
    print("Evidence is written by the tools only (règle d'or du cahier des charges).", file=sys.stderr)
    sys.exit(2)
```

```python
# .claude/hooks/format_python.py — PostToolUse: format and lint-fix a Python file right after Claude edits it
import json, subprocess, sys
path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
if path.endswith(".py"):
    for cmd in (["ruff", "format", "--quiet", path], ["ruff", "check", "--fix", "--quiet", path]):
        try:
            subprocess.run(cmd, check=False, timeout=30)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # ruff not on PATH: skip; make check still catches it
sys.exit(0)
```

```python
# .claude/hooks/session_context.py — SessionStart: print the journal tail and last commits so a new session resumes the plan
import pathlib, subprocess
journal = pathlib.Path("docs/journal.md")
if journal.exists():
    print("== docs/journal.md (last 30 lines) ==")
    print("\n".join(journal.read_text(encoding="utf-8").splitlines()[-30:]))
try:
    log = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=10).stdout
    print("== last commits ==\n" + log)
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass
```

Results of the scratch run: the evidence hook exited 2 on `reports/perf/load.json` and 0 on `docs/conformite.md`; the formatter reformatted a messy `.py` file, removed an unused import and ignored a `.md` file; the session hook printed the journal and the last commit. On Windows, replace `python3` with `python` in the three commands, and activate the backend virtualenv (or install ruff globally) so the formatter finds `ruff`.

## 5. Compatibility, install order and risks

The whole kit installs in about 15 minutes during tonight's setup slot, and everything except the plugins and the MCP server is plain files in the repository. Update Claude Code to its latest version first: skill fields such as `arguments` and `context` must be supported by your installed version.

### Compatibility matrix

| Component | Works on | Needs | Network at install | Extra cost |
| --- | --- | --- | --- | --- |
| `CLAUDE.md`, 6 skills, 2 subagents | Claude Code on Windows, macOS, Linux | Nothing | No | No |
| 3 hooks | Same | `python3` on PATH (`python` on Windows); `ruff` for the formatter, skipped if absent | No | No |
| `pyright-lsp` | Same | `pyright-langserver` (npm package `pyright`) | Yes | No |
| `typescript-lsp` | Same | `typescript-language-server` + `typescript` | Yes | No |
| `code-review`, `claude-code-setup` | Same | Nothing | Yes | Uses your normal Claude Code usage |
| `/security-review` | Same | A Git repo with pending changes | No | Uses your normal Claude Code usage |
| Playwright MCP | Same | Node 18+; browsers download on first use | Yes | No |
| `webapp-testing` (optional) | Same | Python Playwright + browsers | Yes | No |
| Headless `claude -p --bare` (not recommended here) | Same | `ANTHROPIC_API_KEY`; skips `CLAUDE.md`, hooks and skills | Yes | API billing |

### Install order (18:30 to 18:45)

```bash
# 1. Files: CLAUDE.md, .claude/settings.json, .claude/hooks/*.py, .claude/skills/*/SKILL.md, .claude/agents/*.md
#    (contents in sections 3 and 4 and in tonight's plan)

# 2. Language-server binaries for the LSP plugins
npm install -g pyright typescript-language-server typescript

# 3. Playwright MCP, shared through .mcp.json (skip if you install the playwright plugin instead)
claude mcp add playwright --scope project -- npx @playwright/mcp@latest --headless
```

```text
# 4. Inside Claude Code
/plugin install pyright-lsp@claude-plugins-official
/plugin install typescript-lsp@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
```

5. Restart Claude Code, then check: `/plugin` lists the 4 plugins; `/mcp` shows `playwright` connected; typing `/` shows the 6 project skills; the session opens with the journal tail from the hook.
6. Ask the `claude-code-setup` plugin to scan the repository and compare its suggestions with this kit.
7. Commit `CLAUDE.md`, `.claude/` and `.mcp.json` as "phase 0: Claude Code configuration".

### Risks to watch

| Risk | Mitigation |
| --- | --- |
| An AI review is presented as tool evidence, breaking the golden rule | Findings from `/security-review`, `code-review` or a subagent go in `triage.md` or the journal as *revue de code*, never as SAST, SCA or DAST results |
| Third-party plugins, skills or MCP servers run code on your machine | Install only the official marketplace items and Microsoft's Playwright server listed here; read `.mcp.json` before committing it |
| Each plugin and MCP server adds context and slows long sessions | Keep to this list; disable what a phase does not need with `/plugin` |
| An injected command in a skill fails and the whole skill aborts | Commands that may exit non-zero end with `\|\| true` (already done in `/trace` and `/security-triage`) |
| `--bare` mode silently drops `CLAUDE.md` and the hooks | Do not use `--bare` for project work; it is meant for reproducible CI calls |
| A slow hook on every edit | The formatter has a 30-second timeout and skips non-Python files |
| The plugin catalogue changes | Descriptions here are from a 2026 catalogue; confirm names in `/plugin` before installing |

### Sources

- [Claude Code: skills](https://code.claude.com/docs/en/skills)
- [Claude Code: subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code: headless mode](https://code.claude.com/docs/en/headless)
- [Claude Code: discover plugins](https://code.claude.com/docs/en/discover-plugins)
- [Official plugin catalogue (DesignRevision, 2026)](https://designrevision.com/blog/official-claude-code-plugins)
- [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review)
- [Playwright MCP](https://playwright.dev/docs/getting-started-mcp)
- [webapp-testing skill page](https://moltchat-agent-commons.onrender.com/api/v1/pages/skill-anthropic-webapp-testing)
- [Postgres MCP overview (Peliqan)](https://peliqan.io/blog/postgres-mcp/)
