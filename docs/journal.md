# Journal de bord

## Phase 0 — Configuration de Claude Code (19/11/2026)

- Ajout de `CLAUDE.md` (règle de l'oracle, règle d'or), `.claude/settings.json` (permissions, plugins, hooks).
- 3 hooks : protection des preuves (`reports/`, `docs/preuves/`), formatage Python (ruff), reprise de session.
- 6 skills projet : `/test-design`, `/gen-tests`, `/anomalie`, `/security-triage`, `/trace`, `/phase-done`.
- 2 sous-agents : `test-reviewer`, `evidence-auditor`.
- Serveur MCP Playwright déclaré dans `.mcp.json` (exploratoire uniquement, pas une preuve).
- Points ouverts : `docs/exigences.yaml` et `tools/trace.py` restent à écrire.
