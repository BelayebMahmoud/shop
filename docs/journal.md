# Journal de bord

## Phase 0 — Configuration de Claude Code (19/11/2026)

- Ajout de `CLAUDE.md` (règle de l'oracle, règle d'or), `.claude/settings.json` (permissions, plugins, hooks).
- 3 hooks : protection des preuves (`reports/`, `docs/preuves/`), formatage Python (ruff), reprise de session.
- 6 skills projet : `/test-design`, `/gen-tests`, `/anomalie`, `/security-triage`, `/trace`, `/phase-done`.
- 2 sous-agents : `test-reviewer`, `evidence-auditor`.
- Serveur MCP Playwright déclaré dans `.mcp.json` (exploratoire uniquement, pas une preuve).
- Points ouverts : `docs/exigences.yaml` et `tools/trace.py` restent à écrire.

## Mise en place + P0 (19/11/2026)

- Documents du sujet copiés : `docs/cahier-des-charges.pdf`, `docs/cours/` (Chapitre I, fiches 1, 2, 4, TP3), `docs/plan-de-la-nuit.md`.
- `CLAUDE.md` fusionné (plan + kit), permissions du plan ajoutées à `.claude/settings.json`.
- Images des scanners (ZAP, k6, gitleaks, Trivy, Syft, Hadolint) téléchargées en arrière-plan.
- P0 : analyse des écarts dans `docs/analyse-p0.md` (aucun code écrit). Fichiers de preuve : aucun.
- Points ouverts : 3 questions bloquantes (domaine, critère de sortie sécurité, outils sous Windows).
