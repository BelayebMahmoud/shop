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

## Phase 3 — Tests d'intégration et d'API (19/11/2026)

- Intégration (`backend/tests/integration`) : IT-01 à IT-14, une réussite et une erreur par interface de
  `conception.md` §4, base PostgreSQL de test reconstruite avant chaque test.
- API (`backend/tests/api`) : TA-01 à TA-37 — table de décision 401/422/404/409/201 avec statut, corps et effet en
  base ; cycles de vie ; matrice des droits `docs/rbac.yaml` (27 routes × 4 rôles = 108 tests, TA-20) ; isolation
  entre clients ; concurrence ; robustesse (TA-32 à TA-35).
- Contrat (`backend/tests/contract`) : Schemathesis 4.33.4, toutes vérifications, 25 opérations (TA-28).
- Anomalies : Schemathesis a trouvé 2 erreurs 500 (ANO-01 identifiant hors plage, ANO-02 caractère NUL) et 3 écarts
  de contrat (ANO-03 à ANO-05) ; corrigés, confirmés et suivis d'une non-régression (`docs/anomalies.md`).
  ANO-06 : exclusion justifiée d'une vérification pour deux règles inter-champs.
- Défaut de test DT-01 : TA-13 (concurrence) ne pouvait pas échouer ; course désormais forcée. Mutations au niveau
  API (`tools/break_rules.py --suite api`) : 7 sur 7 détectées.
- Revue indépendante (rôle test-reviewer) : aucun bloquant ; 3 majeurs corrigés (TA-01 normalisation de l'email,
  IT-12 borne de fin et 422 HTTP, TA-28 opérations client avec un jeton client) ; lacunes comblées par TA-36
  (Q-02 et annulation après SHIPPED via l'API) et TA-37 (audit annulation et produits).
- `make check` vert : lint, check_docs (135 cas), 56 unitaires, 17 intégration, 168 API, 25 contrat ; couverture
  `app/services` 99,4 % (instructions + branches, seuil 80 % bloquant) ; API : 25/25 opérations, 74/95 codes
  documentés obtenus (`reports/api-coverage.md`).
- Fichiers de preuve : `reports/junit-{unit,integration,api,contract}.xml`, `reports/coverage.xml`,
  `reports/htmlcov/`, `reports/api-coverage.md`, `reports/unit/regles-cassees.txt`, `reports/api/regles-cassees.txt`.
- Points ouverts (constats mineurs de la revue) : assertions de corps/état à renforcer sur TA-03, TA-07, TA-15,
  TA-18, TA-21, TA-22, TA-25, IT-04, IT-05, IT-11, IT-14 ; TA-20 dépend de l'entrée d'audit n° 1 ; ADMIN_ID codé en
  dur ; attente de 2 s dans TA-13 ; mutations API de BR-02, BR-04, BR-07, Q-08 non encore tentées ; 21 codes
  documentés jamais obtenus.

## Phase 4 — Frontend, E2E, accessibilité, protocole d'utilisabilité (19/11/2026)

- Interface en français : catalogue (recherche, catégorie, prix, en stock, pagination), fiche, panier, connexion,
  mes commandes (annulation), back-office commandes (seules les transitions permises), produits (erreurs sous le champ,
  boîte de confirmation accessible), tableau de bord (période, catégorie). L'API reste seule garante des droits.
- Playwright 1.65.1 (chromium, firefox, mobile Pixel 7) sur le build de production (`vite preview`), base `shop_e2e`
  reconstruite par `tools/e2e_api.py` ; E2E-01 à E2E-05 et UX-01 (axe sur 5 pages + dialogue + erreurs de champ).
- Résultat : chromium et mobile → 12 réussis (`reports/junit-e2e.xml`) ; axe : 0 violation serious/critical sur les
  7 audits (`reports/a11y/`).
- Anomalie ANO-07 (back-office inutilisable sur téléphone) trouvée par le projet mobile, corrigée, confirmée.
- Environnement : ENV-01 (blocages ~10 s en parallèle via le port Docker redirigé → 1 worker par défaut, vérification
  en phase 5 dans le réseau Compose) ; ENV-02 (Firefox ne démarre pas sous ce Windows → Firefox en conteneur en phase 5).
- Revue indépendante (agent test-reviewer) : aucun bloquant ; 4 majeurs corrigés (E2E-04 vérifie l'API après création
  et après « Annuler », E2E-05 teste une période passée et début > fin, UX-01 audite des pages remplies et deux états).
- Protocole `docs/utilisabilite.md` (3 tâches, critères de réussite, consentement, SUS, tableau de résultats vide).
- `make check` vert (56 / 17 / 168 / 25, couverture services 99,4 %).
- Points ouverts : Firefox (conteneur, phase 5) ; E2E en parallèle à confirmer (ENV-01) ; sessions d'utilisabilité.
