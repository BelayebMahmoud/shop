# Rapport de conformité ISO/IEC 25010 — Gestion commerciale

Version 1.0 du 20/11/2026. Modèle de qualité du Chapitre I (ISO/IEC 25010:2011, 8 caractéristiques du produit et
qualité en utilisation). Chaque valeur mesurée est recopiée d'un rapport brut écrit par l'outil, gelé dans
[`preuves/v1.0/`](preuves/v1.0/) avec ses empreintes SHA-256 (`preuves/v1.0/sha256sums.txt`), le commit du gel et
les versions des outils (`preuves/v1.0/manifest.json`, `preuves/v1.0/versions/`). Règle d'or du cahier : aucun
résultat affirmé sans exécution réelle ; ce qui n'a pas pu être exécuté est signalé « en attente » ou « non disponible ».

Synthèse générée : [`tracabilite/matrice.md`](tracabilite/matrice.md) — 36 exigences, 34 PASS, 2 PARTIAL, 0 FAIL,
0 NOT RUN.

**Commit de chaque mesure.** Relancés le 20/11/2026 entre 07:10 et 07:35 UTC sur le commit `aa22690` (commit du
gel, [`manifest.json`](preuves/v1.0/manifest.json)) : tests pytest, règles cassées, qualité (radon, xenon,
import-linter), installation propre (le journal affiche `aa22690`) et tous les scans de sécurité. Le code applicatif
de `aa22690` est identique à celui de `99a818c` : `git diff --exit-code` sur `backend`, `web`, `db` et
`docker-compose.yml` sort avec le code 0 et une sortie vide
([`code/diff-99a818c-aa22690.txt.status.json`](preuves/v1.0/code/diff-99a818c-aa22690.txt.status.json)) ; les E2E et
l'accessibilité ont été rejoués en fin de phase 8, après les corrections ANO-09 et ANO-10 (horodatage dans
`junit-e2e*.xml`, déroulé dans [`journal.md`](journal.md)), sans relance depuis. Non relancés : performance (PERF-01 à 03) et
fiabilité (REL-01, REL-02), mesurées le 19/11/2026 entre 23:45 et 23:55 UTC sur l'arbre de travail de la phase 7,
enregistré ensuite dans le commit `42084ad` (23:58 UTC, [`code/commits.txt`](preuves/v1.0/code/commits.txt)) ; entre
`42084ad` et `99a818c`, le backend ne change que dans `routes/orders.py` et `services/orders.py`
([`code/diff-42084ad-99a818c-backend.txt`](preuves/v1.0/code/diff-42084ad-99a818c-backend.txt)), pour la pagination
de `GET /api/orders` (ANO-09) ; aucune route exercée par ces mesures (liste, détail et recherche de produits,
`POST /api/orders`, `/api/health`) n'en dépend. La mutation (MA-02) a été mesurée en phase 8, avant ANO-09.

Environnement de mesure : Windows 11, 12 cœurs logiques alloués à Docker, Docker 29.9.3
([`perf/environnement.txt`](preuves/v1.0/perf/environnement.txt)) ; pile Docker Compose — PostgreSQL
([`versions/postgres.txt`](preuves/v1.0/versions/postgres.txt)), API Python sur Alpine
([`versions/api-python.txt`](preuves/v1.0/versions/api-python.txt), [`sca/sbom-api.cdx.json`](preuves/v1.0/sca/sbom-api.cdx.json)),
nginx ([`versions/web-nginx.txt`](preuves/v1.0/versions/web-nginx.txt), [`sca/sbom-web.cdx.json`](preuves/v1.0/sca/sbom-web.cdx.json)).

## 1. Aptitude fonctionnelle — complétude, exactitude, pertinence

**Exigence** : QR-FS-01 — toutes les fonctions du §4 implémentées et exactes (FR-01 à FR-11, BR-01 à BR-11).
**Cible** : 100 % des FR et BR de priorité P0 au verdict PASS dans la matrice.
**Méthode** : pytest 9.2.0 (unitaires sans base, intégration et API sur PostgreSQL jetable), Playwright 1.65.1 (E2E),
techniques de la fiche 2 (partitions, limites, table de décision, transitions d'états) ; règles cassées
volontairement (`tools/break_rules.py`).
**Résultat mesuré** : 19/19 FR/BR P0 au PASS (matrice, ligne QR-FS-01) — atteint. Exécutions : 59 tests unitaires,
17 d'intégration, 169 d'API, 0 échec ([`junit-unit.xml`](preuves/v1.0/junit-unit.xml),
[`junit-integration.xml`](preuves/v1.0/junit-integration.xml), [`junit-api.xml`](preuves/v1.0/junit-api.xml)) ;
18 règles cassées volontairement, toutes détectées par au moins un cas nommé
([`unit/regles-cassees.txt`](preuves/v1.0/unit/regles-cassees.txt), [`api/regles-cassees.txt`](preuves/v1.0/api/regles-cassees.txt)).
**Preuve** : [`tracabilite/matrice.csv`](tracabilite/matrice.csv) · code de `99a818c`
**Sous-caractéristiques** : complétude (chaque item du §4 a une FR tracée), exactitude (remise BR-04 aux valeurs
limites des cas CT-11 à CT-17, valeurs dans [`cahier-de-test.md`](cahier-de-test.md), résultats dans
`junit-unit.xml`), pertinence (tableau de bord et workflow vérifiés de
bout en bout, E2E-03 et E2E-05).
**Limites** : les règles sont celles fixées par le groupe (questions Q-01 à Q-12 tranchées) ; aucune recette par un
client réel.

## 2. Efficacité de performance — comportement temporel, utilisation des ressources, capacité

**Exigence** : QR-PE-01 (liste et détail sous charge), QR-PE-02 (recherche sur 50 000 produits).
**Cible** : p95 < 500 ms à 20 utilisateurs simultanés, erreurs < 1 % ; recherche p95 < 800 ms.
**Méthode** : k6 ([`versions/k6.txt`](preuves/v1.0/versions/k6.txt)) dans le réseau Docker Compose (seuils déclarés
dans les scripts `perf/k6/*.js`), 20 utilisateurs virtuels pendant 5 min (liste, détail) et 2 min (recherche
filtrée), au commit `42084ad` ; base d'environ 50 000 produits (paramètre `PRODUCT_COUNT` = 50 008 de
`perf/k6/common.js` ; 50 165 produits comptés dans cette base à la clôture,
[`perf/produits-en-base.txt`](preuves/v1.0/perf/produits-en-base.txt)) ; relevés `docker stats` environ toutes les 12 s.
**Résultat mesuré** — atteint :

| Cas | Requêtes | p95 | Erreurs | Rapport |
| --- | --- | --- | --- | --- |
| PERF-01 smoke (1 utilisateur, 30 s) | 113 | 64,13 ms | 0 % | [`perf/smoke.json`](preuves/v1.0/perf/smoke.json) |
| PERF-02 liste (20 utilisateurs, 5 min) | 22 417 au total | 77,39 ms | 0 % | [`perf/load.json`](preuves/v1.0/perf/load.json) |
| PERF-02 détail | (même exécution) | 49,41 ms | 0 % | [`perf/load.json`](preuves/v1.0/perf/load.json) |
| PERF-03 recherche filtrée (20 utilisateurs, 2 min) | 4 636 | 64,32 ms | 0 % | [`perf/search.json`](preuves/v1.0/perf/search.json) |

Ressources : [`perf/ressources-load.csv`](preuves/v1.0/perf/ressources-load.csv) (75 relevés),
[`perf/ressources-search.csv`](preuves/v1.0/perf/ressources-search.csv).
**Sous-caractéristiques** : comportement temporel (p95 ci-dessus), utilisation des ressources (CPU et mémoire par
conteneur), capacité (20 utilisateurs sans erreur ; index trigramme GIN pour la recherche).
**Limites** : mesures sur un poste de développement, client et serveur sur la même machine ; pas d'essai d'endurance
ni au-delà de 20 utilisateurs (hors portée du plan de test).

## 3. Compatibilité — coexistence, interopérabilité

**Exigence** : QR-CO-01 (deux navigateurs), QR-CO-02 (contrat OpenAPI).
**Cible** : E2E-01 à E2E-05 au PASS sur Chromium et Firefox ; Schemathesis toutes vérifications : 0 échec, 0 réponse 500.
**Méthode** : Playwright 1.65.1, projets chromium, firefox et mobile (Pixel 7), exécutés depuis l'image officielle
Playwright dans le réseau Compose (Firefox ne démarre pas sur ce Windows : ENV-02) ; Schemathesis 4.33.4 sur
`/openapi.json` ; ports configurables par `.env`.
**Résultat mesuré** — atteint : 24 tests E2E dont 20 exécutés et réussis sur 3 navigateurs, 4 audits d'accessibilité
volontairement limités à chromium ([`junit-e2e-docker.xml`](preuves/v1.0/junit-e2e-docker.xml)) ; poste : 16 tests,
14 réussis, 2 limités à chromium ([`junit-e2e.xml`](preuves/v1.0/junit-e2e.xml)) ; contrat : 25 opérations sur 25 sans
échec ([`junit-contract.xml`](preuves/v1.0/junit-contract.xml)) ; couverture de l'API : 25/25 opérations exercées
([`api-coverage.md`](preuves/v1.0/api-coverage.md)).
**Sous-caractéristiques** : interopérabilité (contrat OpenAPI publié et vérifié ; erreurs documentées par route),
coexistence (l'installation propre tourne sous son propre projet Compose et ses propres ports à côté de la pile de
développement — [`portabilite/installation-desktop-svtshjh.log`](preuves/v1.0/portabilite/installation-desktop-svtshjh.log)).
**Limites** : WebKit/Safari non testé ; pas de système tiers réel connecté (le contrat OpenAPI tient lieu d'interface
externe).

## 4. Facilité d'utilisation — reconnaissabilité, apprentissage, exploitabilité et accessibilité, protection contre les erreurs

**Exigence** : QR-US-01 (accessibilité), QR-US-02 (recette utilisateur).
**Cible** : axe-core 0 violation serious/critical sur 5 pages ; réussite des tâches >= 80 % et SUS >= 68 (Q-12).
**Méthode** : @axe-core/playwright (règles WCAG 2.0/2.1 A et AA) sur pages remplies de données, plus deux états
(dialogue de confirmation ouvert, formulaire en erreur) ; protocole [`utilisabilite.md`](utilisabilite.md).
**Résultat mesuré** : axe — 7 audits, **0 violation** de tout niveau ([`a11y/`](preuves/v1.0/a11y/)) — atteint.
Recette utilisateur — **en attente** (séances le 20/11/2026, décision du groupe).
**Sous-caractéristiques** : protection contre les erreurs (confirmation avant suppression vérifiée contre l'API,
E2E-04 ; messages sous le champ fautif ; refus de stock lisible, E2E-02) ; exploitabilité sur téléphone (ANO-07 et
ANO-10 trouvées par le projet mobile et corrigées) ; reconnaissabilité et apprentissage : mesurés par la recette.
**Écart** : QR-US-02 au verdict PARTIAL (voir § Écarts).
**Limites** : axe ne détecte qu'une partie des problèmes d'accessibilité ; pas de test avec lecteur d'écran.

## 5. Fiabilité — maturité, disponibilité, tolérance aux fautes, recouvrabilité

**Exigence** : QR-RE-01 (reprise après panne), QR-RE-02 (atomicité, pas de survente).
**Cible** : reprise < 60 s ; aucune commande perdue ou incohérente ; aucune 500 hors de la fenêtre de panne.
**Méthode** : sonde dans le réseau Compose pendant 120 s, au commit `42084ad` (paramètres de
`tools/reliability_probe.py` : 4 fils qui commandent, `/api/health` interrogé toutes les 0,25 s) ; panne injectée à 30 s ; contrôles SQL de cohérence après coup (`tools/reliability.py`) ;
tests pytest REL-03 (vraie erreur PostgreSQL entre deux écritures) et REL-04 (double soumission simultanée).
**Résultat mesuré** — atteint :

| Cas | Panne | Reprise | Réponses 500 | Commandes acquittées retrouvées | Cohérence | Rapport |
| --- | --- | --- | --- | --- | --- | --- |
| REL-01 | redémarrage de PostgreSQL | 3,15 s | 0 | 1 784 / 1 784 | 5 contrôles à 0 | [`reliability/rel-01.json`](preuves/v1.0/reliability/rel-01.json) |
| REL-02 | arrêt brutal de l'API | 3,27 s | 0 | 1 774 / 1 774 | 5 contrôles à 0 | [`reliability/rel-02.json`](preuves/v1.0/reliability/rel-02.json) |

REL-03, REL-04 et le contrat 503 : 3 tests réussis ([`junit-reliability.xml`](preuves/v1.0/junit-reliability.xml)) ;
concurrence TA-13 réussie (course forcée, DT-01).
**Sous-caractéristiques** : disponibilité (pendant REL-01, `/api/health` répond 503, une interrogation restant sans réponse ; pendant REL-02, le proxy
nginx répond 502 tant que l'API redémarre ; politique `restart`),
tolérance aux fautes (base indisponible → 503 `Retry-After`, jamais 500), recouvrabilité (aucune donnée perdue),
maturité (verrous de ligne, transactions uniques par commande).
**Limites** : une seule panne de chaque type par essai ; pas de perte du volume de données ni de bascule vers une
seconde instance.

## 6. Sécurité — confidentialité, intégrité, non-répudiation, imputabilité, authenticité

**Exigence** : QR-SE-01 (absence de faille connue), QR-SE-02 (droits et attaques manuelles).
**Cible** (TP3, retenu en P0) : 0 alerte High non traitée, 0 Medium non justifiée, Low justifiées ; matrice des
droits 100 % conforme ; 4 attaques refusées.
**Méthode** : `scripts/security-scans.sh`, relancé sur le commit `aa22690` le 20/11/2026 (versions lues des outils
dans [`versions/`](preuves/v1.0/versions/)) — SAST Semgrep, Bandit, gitleaks (historique Git complet) ; SCA pip-audit,
npm audit, Trivy (images et dépôt), SBOM Syft (CycloneDX) ; DAST OWASP ZAP (baseline passif puis scan d'API actif,
autorisation écrite) ; matrice des droits `rbac.yaml` (27 routes × 4 rôles) ; attaques SEC-01 à SEC-04.
**Résultat mesuré** — atteint, après corrections et relance ([`securite-synthese.md`](preuves/v1.0/securite-synthese.md)) :

| Famille | Avant | Après | Rapport |
| --- | --- | --- | --- |
| SAST Semgrep | 2 ERROR, 18 WARNING | 19 corrigés ; 3 ERROR, faux positifs justifiés (S20 à S22, outils locaux) | [`sast/semgrep-avant.json`](preuves/v1.0/sast/semgrep-avant.json), [`sast/semgrep.json`](preuves/v1.0/sast/semgrep.json) |
| SAST Bandit | non conservé (0 au journal) | 0 | [`sast/bandit.json`](preuves/v1.0/sast/bandit.json) |
| Secrets gitleaks | non conservé (0 au journal, avant l'ajout des rapports au dépôt) | 242 constats, tous dans des rapports de preuve : 238 faux positifs (G1, G2), 4 jetons de test expirés (G3 : présents dans `perf/smoke.json` et `perf/load.json` de ces preuves et dans l'historique Git local ; corrigé pour les prochaines mesures ; résidu accepté par le groupe le 20/11/2026) ; 0 dans le code | [`sast/gitleaks.json`](preuves/v1.0/sast/gitleaks.json) |
| SCA dépendances (31 paquets Python, npm, dépôt) | non conservé (0 au journal) | 0 | [`sca/pip-audit.json`](preuves/v1.0/sca/pip-audit.json), [`sca/npm-audit.json`](preuves/v1.0/sca/npm-audit.json), [`sca/trivy-fs.json`](preuves/v1.0/sca/trivy-fs.json) |
| SCA images Docker (Trivy) | api : 53 High ; web : 3 Critical, 65 High | 0 vulnérabilité | [`sca/trivy-image-*-avant.json`](preuves/v1.0/sca/), [`sca/trivy-image-*.json`](preuves/v1.0/sca/) |
| DAST ZAP | 1 High, 5 Low | 1 High faux positif prouvé par test (Z4), 0 Low | [`dast/zap-*-avant.json`](preuves/v1.0/dast/), [`dast/zap-*.json`](preuves/v1.0/dast/) |

Matrice des droits : 108 cas réussis ; attaques injection SQL, XSS stocké, contrôle d'accès, session : refusées
([`junit-security.xml`](preuves/v1.0/junit-security.xml), [`junit-api.xml`](preuves/v1.0/junit-api.xml),
[`junit-e2e-docker.xml`](preuves/v1.0/junit-e2e-docker.xml)). Tri complet : [`securite/triage.md`](securite/triage.md).
**Sous-caractéristiques** : confidentialité (rôles, BR-08 : la commande d'un autre est introuvable), intégrité
(prix pris au catalogue BR-02, entrées bornées ANO-01 à ANO-03), non-répudiation et imputabilité (journal d'audit en
ajout seul, protégé par un déclencheur), authenticité (Argon2id, JWT à durée limitée, rôle relu à chaque requête).
**Limites** : l'alerte ZAP 40018 reste signalée par l'heuristique (justifiée) ; pas de test d'intrusion par un
expert ; HTTPS hors portée (pile locale).

## 7. Maintenabilité — modularité, réutilisabilité, analysabilité, modifiabilité, testabilité

**Exigence** : QR-MA-01 (couverture et qualité des tests), QR-MA-02 (couches, complexité).
**Cible** : couverture >= 80 % (instructions et branches) sur `app/services` ; complexité <= 10 ; aucune dépendance
inverse entre couches ; score de mutation rapporté.
**Méthode** : pytest-cov, mutmut ([`versions/mutmut.txt`](preuves/v1.0/versions/mutmut.txt), dans Docker, phase 8),
Hypothesis 6.170.15 ([`sca/licences-python.json`](preuves/v1.0/sca/licences-python.json)), radon/xenon,
import-linter, ruff.
**Résultat mesuré** — atteint :
- couverture `app/services` : instructions 388/391, branches 96/96, 99,4 % ([`coverage.xml`](preuves/v1.0/coverage.xml)) ;
- mutation : 128 mutants tués sur 133 (96 %), 5 survivants examinés et justifiés
  ([`maintenabilite/mutmut-stats.json`](preuves/v1.0/maintenabilite/mutmut-stats.json),
  [`maintenabilite/mutmut-results.txt`](preuves/v1.0/maintenabilite/mutmut-results.txt)) ;
- complexité : 129 blocs analysés, moyenne 1,84 ([`maintenabilite/radon-cc.txt`](preuves/v1.0/maintenabilite/radon-cc.txt)),
  maximum 9 (après ANO-08) ([`maintenabilite/radon-cc.json`](preuves/v1.0/maintenabilite/radon-cc.json)) ; xenon
  (seuil B) : code de sortie 0 ([`maintenabilite/xenon.txt.status.json`](preuves/v1.0/maintenabilite/xenon.txt.status.json)) ;
- couches : 2 contrats tenus, 0 rompu ([`maintenabilite/import-linter.txt`](preuves/v1.0/maintenabilite/import-linter.txt)).
**Sous-caractéristiques** : modularité (api → services → models), réutilisabilité (règles en fonctions pures
partagées par l'API et les tests), analysabilité (complexité moyenne 1,84), modifiabilité (18 règles cassées
volontairement détectées), testabilité (règles testées sans base ni HTTP).
**Limites** : la couverture combine toutes les suites ; l'interface React n'est couverte que par les E2E.

## 8. Portabilité — adaptabilité, facilité d'installation, remplaçabilité

**Exigence** : QR-PO-01 — installation reproductible sur une autre machine.
**Cible** : installation propre < 10 min avec smoke test réussi ; journal d'installation sur une seconde machine.
**Méthode** : Docker Compose (3 services, healthchecks, configuration par `.env`), `scripts/installation-propre.sh`
(clone neuf, secrets aléatoires, ports isolés, chronomètre), guide [`installation.md`](installation.md).
**Résultat mesuré** : installation propre depuis un clone du commit `aa22690` (images Alpine durcies) et smoke test
en 29 s, verdict PASS
([`portabilite/installation-desktop-svtshjh.log`](preuves/v1.0/portabilite/installation-desktop-svtshjh.log)) —
atteint sur ce poste ; seconde machine **en attente**. Hadolint : 0 constat sur les deux Dockerfile
([`sca/hadolint-backend.json`](preuves/v1.0/sca/hadolint-backend.json), [`sca/hadolint-web.json`](preuves/v1.0/sca/hadolint-web.json)).
**Sous-caractéristiques** : adaptabilité (ports, secrets et base par variables d'environnement), facilité
d'installation (une commande), remplaçabilité (l'API et le web sont des images indépendantes derrière un contrat).
**Écart** : QR-PO-01 au verdict PARTIAL (voir § Écarts).
**Limites** : 29 s avec un cache Docker déjà rempli ; le premier téléchargement des images n'est pas inclus.

## 9. Qualité en utilisation (Chapitre I)

| Caractéristique | Mesure prévue | Statut |
| --- | --- | --- |
| Efficacité | taux de réussite des 3 tâches (UX-02) | en attente (séances du 20/11/2026) |
| Efficience | temps médian par tâche (UX-02) | en attente |
| Satisfaction | score SUS moyen (UX-03) | en attente |
| Absence de risque | refus de stock négatif (BR-01), confirmation avant suppression, aucune perte de commande en panne (REL-01/02) | vérifié par les tests cités aux §1, §4 et §5 |
| Couverture contextuelle | bureau et téléphone, Chromium et Firefox | vérifié (§3) |

## 10. Correspondance ISO/IEC 25010:2011 → 2023

| 2011 (ce rapport, Chapitre I) | 2023 | Changement principal |
| --- | --- | --- |
| Aptitude fonctionnelle | Aptitude fonctionnelle | inchangée (complétude, exactitude, pertinence) |
| Efficacité de performance | Efficacité de performance | inchangée |
| Compatibilité | Compatibilité | inchangée |
| Facilité d'utilisation | Capacité d'interaction | renommée ; ajoute l'inclusivité et l'auto-descriptivité |
| Fiabilité | Fiabilité | « maturité » devient « absence de défaut » |
| Sécurité | Sécurité | ajoute la résistance |
| Maintenabilité | Maintenabilité | inchangée |
| Portabilité | Flexibilité | renommée ; ajoute la scalabilité |
| — | Sûreté (*safety*) | nouvelle caractéristique ; ici couverte en partie par l'absence de risque (§9) |

## 11. Écarts

| Exigence | Cible | Mesuré | Cause | Impact | Action |
| --- | --- | --- | --- | --- | --- |
| QR-US-02 | réussite >= 80 %, SUS >= 68 | non mesuré (UX-02, UX-03 NOT RUN) | séances avec participants reportées au 20/11/2026 par décision du groupe | la qualité en utilisation n'est pas encore prouvée par des utilisateurs | séances selon `utilisabilite.md`, calcul par script, mise à jour de la matrice |
| QR-PO-01 | installation sur une seconde machine | PORT-02 NOT RUN ; PORT-01 PASS (29 s) | coéquipier non disponible cette nuit | la reproductibilité est prouvée sur un seul poste | installation par un coéquipier avec `installation-propre.sh`, journal ajouté aux preuves |

Constats d'environnement documentés (sans effet sur le produit) : ENV-01 (blocages via le port redirigé de Docker
Desktop, mesures faites dans le réseau Compose), ENV-02 (Firefox lancé en conteneur) — [`anomalies.md`](anomalies.md).
