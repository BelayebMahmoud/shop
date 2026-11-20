# Livrables attendus — où les trouver

Correspondance entre la section 8 du [cahier des charges](cahier-des-charges.pdf) et le dépôt, version 1.0
(tag Git `v1.0`). Chaque chiffre cité ici est repris des rapports ; il provient d'un fichier écrit par l'outil et
gelé dans [`preuves/v1.0/`](preuves/v1.0/) avec ses empreintes SHA-256
([`sha256sums.txt`](preuves/v1.0/sha256sums.txt), [`manifest.json`](preuves/v1.0/manifest.json)).

| # | Livrable demandé (cahier § 8) | Où le trouver | État |
| --- | --- | --- | --- |
| 1 | Code source complet, versionné (dépôt Git avec historique) | `backend/` (FastAPI), `web/` (React/TypeScript), `db/` (migrations), [`docker-compose.yml`](../docker-compose.yml) ; historique : `git log --oneline` (un commit par phase, tag `v1.0`) | livré |
| 2 | Rapport de conception : architecture, modèle de données, choix justifiés | [`conception.md`](conception.md) — § 1 choix de la pile, § 2 architecture en couches, § 3 modèle de données, § 5 contrat d'API et matrice des droits, § 7 architecture finale | livré |
| 3 | Matrice de traçabilité : exigence ↔ test(s) ↔ outil(s) ↔ résultat | [`tracabilite/matrice.md`](tracabilite/matrice.md) (et [`.csv`](tracabilite/matrice.csv)), générée par `tools/trace.py` depuis [`exigences.yaml`](exigences.yaml) et les rapports bruts — 36 exigences : 34 PASS, 2 PARTIAL, 0 FAIL | livré |
| 4 | Jeux de tests exécutables pour chaque couche du § 7, avec rapports générés | Tableau ci-dessous ; commandes dans [`installation.md` § 3](installation.md#3-lancer-chaque-couche-de-test) ; synthèse dans [`rapport-de-test.md`](rapport-de-test.md) | livré |
| 5 | Rapport de conformité ISO 25010 : preuve concrète pour chacune des 8 caractéristiques | [`conformite.md`](conformite.md) — §§ 1 à 8 (une caractéristique chacun : exigence, cible, méthode, résultat mesuré avec lien vers la preuve, limites), § 9 qualité en utilisation, § 11 écarts | livré, 2 écarts documentés |
| 6 | Guide d'installation et d'exécution reproductible par un tiers | [`installation.md`](installation.md) (prérequis, 5 commandes, chaque couche de test, dépannage) ; démarrage rapide dans le [`README.md`](../README.md) ; installation propre mesurée : PASS en 29 s ([`portabilite/`](preuves/v1.0/portabilite/)) | livré ; essai sur une 2e machine en attente (PORT-02) |
| 7 | Soutenance : démonstration live + au moins deux couches de test en exécution | [`demo.md`](demo.md) — script de 12 min : parcours métier, **E2E Playwright en direct** (chromium + firefox), **performance k6 en direct**, une ligne de matrice suivie jusqu'à sa preuve, plan B | prêt |

## Livrable 4 — couches de test du § 7

| Couche (cahier § 7) | Outil utilisé | Tests | Rapport généré (gelé) | Résultat |
| --- | --- | --- | --- | --- |
| Unitaires | pytest + Hypothesis | `backend/tests/unit/` | [`junit-unit.xml`](preuves/v1.0/junit-unit.xml), couverture [`htmlcov/`](preuves/v1.0/htmlcov/index.html), [`coverage.xml`](preuves/v1.0/coverage.xml) | 59/59 ; couverture `app/services` 99,4 % |
| Intégration (API ↔ base) | pytest + TestClient, PostgreSQL réel | `backend/tests/integration/` | [`junit-integration.xml`](preuves/v1.0/junit-integration.xml) | 17/17 |
| API (codes HTTP, structure) | pytest + httpx ; Schemathesis (contrat OpenAPI) | `backend/tests/api/`, `backend/tests/contract/` | [`junit-api.xml`](preuves/v1.0/junit-api.xml), [`junit-contract.xml`](preuves/v1.0/junit-contract.xml), [`api-coverage.md`](preuves/v1.0/api-coverage.md) | 169/169 ; contrat 25/25 opérations |
| Fonctionnels / E2E | Playwright + axe-core | `web/e2e/*.spec.ts` | [`junit-e2e-docker.xml`](preuves/v1.0/junit-e2e-docker.xml), [`junit-e2e.xml`](preuves/v1.0/junit-e2e.xml), [`a11y/`](preuves/v1.0/a11y/) | 20 exécutés, 0 échec (4 audits a11y limités à chromium) ; 0 violation axe |
| Performance | k6 | `perf/k6/` | [`perf/`](preuves/v1.0/perf/) | p95 77,39 / 49,41 / 64,32 ms ; 0 % d'erreurs |
| Fiabilité | pytest + sonde sous panne | `backend/tests/reliability/`, `tools/reliability.py` | [`junit-reliability.xml`](preuves/v1.0/junit-reliability.xml), [`reliability/`](preuves/v1.0/reliability/) | reprise 3,15 s et 3,27 s, 0 commande perdue |
| SAST | Bandit, Semgrep, gitleaks | `scripts/security-scans.sh` | [`sast/`](preuves/v1.0/sast/) | 0 High non traitée ; constats triés dans [`securite/triage.md`](securite/triage.md) |
| SCA | pip-audit, npm audit, Trivy, Syft (SBOM), Hadolint | `scripts/security-scans.sh` | [`sca/`](preuves/v1.0/sca/) | 0 vulnérabilité de dépendance ou d'image |
| DAST | OWASP ZAP (baseline + API), sur `localhost` uniquement | `scripts/security-scans.sh`, autorisation : [`securite/autorisation.md`](securite/autorisation.md) | [`dast/`](preuves/v1.0/dast/), [`securite-synthese.md`](preuves/v1.0/securite-synthese.md) | 1 High prouvée faux positif par test (SEC-01) |
| Qualité / maintenabilité | ruff, radon, xenon, import-linter, mutmut | `make lint quality` ; mutmut dans Docker | [`maintenabilite/`](preuves/v1.0/maintenabilite/) | complexité max 9 ; mutation 96 % |
| Compatibilité | Playwright chromium, firefox, mobile (Pixel 7) | `web/e2e/` | [`junit-e2e-docker.xml`](preuves/v1.0/junit-e2e-docker.xml) | mêmes parcours au PASS sur 3 projets ; WebKit non testé |
| Portabilité | Docker Compose + script d'installation propre | `make install-check` | [`portabilite/`](preuves/v1.0/portabilite/) | PASS en 29 s ; 2e machine en attente |

Plan et cas de test : [`plan-de-test.md`](plan-de-test.md), [`cahier-de-test.md`](cahier-de-test.md). Défauts
trouvés et corrigés : [`anomalies.md`](anomalies.md). Déroulé du projet : [`journal.md`](journal.md).

## Règle d'or — ce qui n'est pas encore prouvé

Conformément à la règle d'or du cahier, ces points sont marqués « en attente » et non simulés :

- **UX-02, UX-03** (QR-US-02) : séances d'utilisabilité avec participants ([`utilisabilite.md`](utilisabilite.md)).
- **PORT-02** (QR-PO-01) : installation sur une seconde machine par un coéquipier.

Détail et justification : [`conformite.md` § 11](conformite.md#11-écarts).
