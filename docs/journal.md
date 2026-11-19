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

## Phase 1 — Planifier, Analyser, Concevoir (19/11/2026)

- Réponses P0 validées : domaine *Gestion commerciale* ; critère de sortie sécurité du TP3 (0 High, 0 Medium non
  justifiée, Low justifiées) ; Semgrep et mutmut en conteneur ; `make` installé (winget, utilisateur).
- Fait : `exigences.yaml` (11 FR, 9 BR, 14 QR, 12 questions ouvertes), `exigences.md` (scénarios Soit/Quand/Alors,
  au moins un valide et un refus par règle), `plan-de-test.md`, `cahier-de-test.md` (121 cas conçus, tables de
  partitions, limites, décision et transitions), `conception.md` (couches, modèle de données, carte des
  interfaces, matrice des droits, utilisation de Claude Code).
- Ajout : `tools/check_docs.py` (cohérence exigence → scénario → cas), intégré à `make check`.
- Vérification : `make check` vert (ruff, oxlint, tsc, check_docs « no problems », pytest 8 passed).
- Fichiers de preuve produits : aucun (phase de conception).
- Écarts : le script a corrigé un comptage fait à la main (CT : 24 valides / 26 échecs attendus).
- Points ouverts : Q-01 à Q-12 (exigences.yaml) à valider avant la phase 2 ; 7 cas portent un attendu NON SPÉCIFIÉ.
