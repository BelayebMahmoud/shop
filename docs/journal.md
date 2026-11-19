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

## Phase 2 — Fonctionnalités backend et tests unitaires (19/11/2026)

- Décisions Q-01 à Q-12 acceptées et intégrées aux règles ; Q-07 et Q-09 ont créé BR-10 et BR-11 (TA-30, TA-31).
- Refactorisation en couches `app/api` → `app/services` → `app/models` (+ `app/core`), comportement du MVP inchangé :
  les 8 tests MVP passent (format d'erreur `{"detail": {"code": ...}}` conservé).
- Migrations `003_roles_categories_audit.sql` (rôles, catégories, workflow, remise, unicité sans casse, journal
  d'audit en ajout seul par déclencheur, comptes admin@ et staff@) et `004_volume_seed.sql` (50 000 produits,
  index trigramme). Base de dev réinitialisée : 50 008 produits.
- Implémenté : FR-01 à FR-11, BR-01 à BR-11 ; `/api/health` vérifie la base (503 si indisponible).
- Tests unitaires `backend/tests/unit` : 56 cas CT (CT-01 à CT-56), sans base ni HTTP, attendus copiés du cahier.
- Règles cassées volontairement (`tools/break_rules.py`) : 11 mutations, 11 détectées, fichiers restaurés.
- Revue indépendante (rôle test-reviewer, sous-agent généraliste car l'agent projet ne se charge qu'au redémarrage) :
  aucun bloquant ; 4 constats majeurs corrigés avant commit (CT-43 sans effet vérifié → `cancel_restock` ; cas
  ajoutés CT-52 sous-total 0, CT-53 ADMIN, CT-54/55 client qui expédie ou livre, CT-56 client qui annule après
  SHIPPED) ; mineurs corrigés (marqueurs BR-06, code FORBIDDEN vérifié, `--strict-markers`).
- Corrigé en passant : le healthcheck PostgreSQL répondait « sain » pendant l'initialisation (socket seul) ;
  il passe désormais par TCP.
- `make check` vert : ruff (lint + format), oxlint, tsc, check_docs (129 cas, « no problems »), 56 tests
  unitaires, 8 tests API.
- Fichiers de preuve : `reports/junit-unit.xml`, `reports/junit-api.xml`, `reports/coverage.xml`,
  `reports/htmlcov/`, `reports/unit/regles-cassees.txt`.
- Écart : couverture `app/services` (instructions + branches, sortie `coverage report`) = 59,0 % tous tests
  confondus, 23,3 % unitaires seuls ; cible 80 % non atteinte. Les modules de règles pures sont à 100 % ; les
  services avec base (catalogue, utilisateurs, tableau de bord, recherche) seront couverts par les cas IT/TA de
  la phase 3.
- Points ouverts : comptage du top 5 par statut vérifié seulement en intégration (IT-11) ; tests MVP à remplacer
  par des cas TA tracés en phase 3.
