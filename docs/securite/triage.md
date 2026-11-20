# Tri des alertes de sécurité (SAST, SCA, DAST)

Méthode : fiche 4 — chaque alerte est classée **vraie / fausse / à surveiller**, avec une raison écrite et une
décision (**corriger / mettre à jour / remplacer / accepter**), puis l'outil est relancé. Critère de sortie retenu
(TP3 §3.1, décision P0) : **0 High, 0 Medium non justifiée, Low justifiées**.

Les comptes viennent des rapports bruts, résumés automatiquement dans
[`reports/securite-synthese.md`](../../reports/securite-synthese.md) (`tools/security_summary.py`). Les revues de code
faites par Claude Code ne figurent pas ici comme résultats d'outil.

## 1. SAST et secrets

| # | Outil | Règle | Fichier : ligne | Gravité | Vraie / fausse | Justification | Décision | Statut après relance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1–S17 | Semgrep | `github-actions-mutable-action-tag` | `.github/workflows/ci.yml` (17 lignes) | WARNING (Medium) | vraie | Une action référencée par une étiquette (`@v4`) peut être remplacée par son auteur : risque de chaîne d'approvisionnement | corriger : actions épinglées par SHA de commit | absente |
| S18 | Semgrep | `use-defused-xml-parse` | `tools/api_coverage.py:40` | ERROR (High) | vraie (exploitabilité faible : fichiers JUnit locaux) | Le parseur XML standard est vulnérable aux entités externes | corriger : `defusedxml` | absente |
| S19 | Semgrep | `request-host-used` | `web/nginx.conf:17` | WARNING (Medium) | vraie (faible) | Transmettre l'en-tête `Host` du client ouvre la voie à une injection d'en-tête ; l'API ne s'en sert pas | corriger : en-tête retiré | absente |
| S20 | Semgrep | `dangerous-subprocess-use-tainted-env-args` | `tools/capture.py:32` (ligne 24 avant l'ajout des options `--with-stderr`/`--status`) | ERROR (High) | **fausse** | Outil de développement dont le rôle est précisément d'exécuter la commande que le développeur lui passe sur la ligne de commande ; aucune entrée réseau ni utilisateur final ; non embarqué dans les images | justifier (faux positif), conserver | présente, justifiée |
| S21 | Semgrep | `dangerous-subprocess-use-tainted-env-args` | `tools/perf_run.py:91` | ERROR (High) | **fausse** | Lanceur de k6 écrit en phase 7 (après le premier scan) : la commande `docker run grafana/k6` est fixe ; seuls le nom de script et les `-e` passés par le développeur sur la ligne de commande y sont ajoutés, en liste (pas de shell) ; non embarqué dans les images | justifier (faux positif), conserver | présente, justifiée (relance du 20/11/2026) |
| S22 | Semgrep | `dangerous-subprocess-use-tainted-env-args` | `tools/reliability.py:114` | ERROR (High) | **fausse** | Lanceur de la sonde de fiabilité (phase 7) : commande `docker run … reliability_probe.py` fixe, arguments du développeur passés en liste sans shell ; outil local, non embarqué | justifier (faux positif), conserver | présente, justifiée (relance du 20/11/2026) |
| — | Bandit | toutes règles | `backend/app` (1 068 lignes) | — | — | aucun constat | — | aucun |
| — | gitleaks (phase 6) | toutes règles | historique Git complet au commit `d21132a` | — | — | aucun secret (le `.env` réel est ignoré par Git, vérifié) | — | aucun |
| G1 | gitleaks (relance) | `generic-api-key` | rapports ZAP `reports/dast/zap-api*.{json,html}` et leurs copies gelées (230 constats) | — | **fausse** | La règle prend pour une clé des chemins d'URL de l'API (`api:8000/api/categories/10`) cités dans les rapports ; aucune valeur secrète | justifier | présente, justifiée |
| G2 | gitleaks (relance) | `generic-api-key` | `reports/sca/trivy-image-api*.json` et copies (8 constats) | — | **fausse** | `GPG_KEY=7169…6305` est l'empreinte publique de la clé de signature des versions de Python, inscrite dans l'image officielle | justifier | présente, justifiée |
| G3 | gitleaks (relance) | `jwt` | `reports/perf/{smoke,load}.json` et copies (4 constats) | — | **vraie** (risque très faible) | k6 recopiait dans son résumé le jeton JWT de l'utilisateur client jetable des essais de charge : pile locale, rôle CUSTOMER, jeton expiré depuis le 20/11/2026 00:14 UTC (durée 30 min), clé de signature non divulguée, dépôt jamais poussé | **corriger** : `perf/k6/common.js` retire `setup_data` du résumé (les prochaines mesures ne contiennent plus de jeton). Les copies déjà enregistrées restent (historique Git local et `perf/smoke.json`, `perf/load.json` des preuves gelées, mesures non relancées) : **résidu accepté par le groupe le 20/11/2026 à 08:40** (réécriture de l'historique écartée : elle changerait tous les commits cités comme preuves) | corrigé pour l'avenir ; résidu accepté |

## 2. SCA (dépendances, images, licences)

| # | Outil | Paquet / image | Gravité (avant) | Vraie / fausse | Atteignabilité | Décision | Statut après relance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | pip-audit | 31 paquets Python (directs et transitifs) | aucune | — | — | — | aucune |
| D2 | npm audit, Trivy fs | dépendances web (`package-lock.json`, transitives incluses) | aucune | — | — | — | aucune |
| I1 | Trivy image | `shop-api` sur Debian 13 (slim) : utilitaires système (util-linux, acl…) | 53 High, 112 Medium, 68 Low | vraies | non atteignables par l'application (outils système jamais appelés), mais sans version corrigée | **remplacer** : image de base Alpine (moins de paquets) | voir I3 |
| I2 | Trivy image | `shop-web` sur nginx 1.27 / Alpine 3.21 (openssl, curl, brotli, expat, nginx) | 3 Critical, 65 High, 103 Medium, 46 Low | vraies (openssl et nginx exposés au réseau) | atteignables pour openssl et nginx | **mettre à jour** : nginx 1.31.7, Alpine 3.24, `apk upgrade` à la construction | aucune |
| I3 | Trivy image | `shop-api` Alpine : pip/setuptools embarqués (urllib3, msgpack, setuptools), openssl, zlib | 5 High, 11 Medium (étapes intermédiaires) | vraies | pip non utilisé à l'exécution | **corriger** : pip et setuptools retirés de l'image, `apk upgrade` | aucune |
| C1 | Hadolint | `backend/Dockerfile` : `USER api` (DL3066, info) | info | vraie | — | corriger : `USER 10001` | aucune |
| L1 | pip-licenses | psycopg, psycopg-binary : LGPL-3.0 | — | à surveiller | bibliothèque utilisée sans modification, liée dynamiquement | accepter (usage conforme à la LGPL) — **accepté par le groupe le 20/11/2026** | — |
| L2 | pip-licenses | certifi, hypothesis : MPL-2.0 | — | à surveiller | fichiers non modifiés ; hypothesis sert aux tests seulement | accepter (usage conforme à la MPL) — **accepté par le groupe le 20/11/2026** | — |
| L3 | license-checker | dépendances web de production : MIT ; « UNLICENSED » = notre propre paquet privé | — | fausse (notre paquet) | — | — | — |

Inventaire (SBOM CycloneDX, Syft) : `reports/sca/sbom-api.cdx.json` (995 composants) et
`reports/sca/sbom-web.cdx.json` (1 282 composants), dépendances transitives et paquets système inclus.

## 3. DAST (OWASP ZAP, pile locale autorisée)

Autorisation : [`autorisation.md`](autorisation.md), accord du 20/11/2026 à 00:33. Scans lancés depuis le réseau
Docker Compose, cibles `http://web:8080` (baseline, passif) et `http://api:8000/openapi.json` (API scan, actif, jeton
ADMIN pour atteindre la logique métier). Rapports avant correction : `reports/dast/zap-*-avant.json` ; après :
`reports/dast/zap-*.json` (HTML lisibles à côté).

| # | Scan | Alerte ZAP (id) | Risque (confiance) | URL / paramètre | Vraie / fausse | Justification | Décision | Statut après relance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Z1 | baseline | Cross-Origin-Embedder/Opener/Resource-Policy absents (90004) | Low (Medium) | `http://web:8080` | vraie | En-têtes d'isolation absents ; toutes les ressources sont de même origine | corriger : COOP, COEP, CORP dans `nginx.conf` | absente |
| Z2 | API | X-Content-Type-Options absent (10021) | Low (Medium) | `http://api:8000/…` (accès direct, sans nginx) | vraie | L'API est aussi joignable sur le port 8000 sans passer par nginx | corriger : en-têtes ajoutés par l'API elle-même | absente |
| Z3 | API | Cross-Origin-Resource-Policy absent (90004) | Low (Medium) | `http://api:8000/…` | vraie | idem Z2 | corriger : `Cross-Origin-Resource-Policy: same-origin` | absente |
| Z4 | API | **SQL Injection (40018)** | **High (Medium)** | `PUT /api/categories/{id}` puis `POST /api/categories`, paramètre `name` (`ZAP AND 1=1 -- `, `ZAP OR 1=1 -- `) | **fausse** | Heuristique « réponses différentes » : ZAP renomme une catégorie avec sa charge, la réponse renvoie ce texte, puis une autre charge donne une réponse différente (texte différent, ou 409 nom déjà pris). Toutes les requêtes passent par l'ORM avec paramètres liés ; Bandit et Semgrep n'ont trouvé aucun SQL construit à la main. **Preuve exécutée** : test SEC-01-zap-40018 — les deux charges booléennes renvoient 200 et sont enregistrées telles quelles (`reports/junit-security.xml`) ; SEC-01 (3 charges dans la recherche) : table intacte. | justifier (faux positif prouvé par test), conserver le test de non-régression | toujours signalée par l'heuristique (2 instances), **justifiée** |
| Z5 | baseline | Modern Web Application (10109), Storable and Cacheable Content (10049) | Informational | `http://web:8080` | — | Informations : application monopage ; fichiers statiques versionnés mis en cache volontairement | aucune | informations |
| Z6 | API | Client Error response code (100000), Authentication Request Identified (10111), Non-Storable Content (10049) | Informational | — | — | Réponses 4xx attendues aux attaques ; route de connexion identifiée | aucune | informations |

Attaques manuelles automatisées (fiche 4) : SEC-01 injection SQL (recherche et catégories), SEC-03 contrôle d'accès,
SEC-04 session (`reports/junit-security.xml`) ; SEC-02 XSS stocké (`reports/junit-e2e-docker.xml`, chromium,
firefox, mobile) — toutes refusées comme attendu.

## 4. Bilan

| Famille | Avant | Après relance |
| --- | --- | --- |
| SAST (Semgrep) | 2 ERROR, 18 WARNING | 19 corrigées ; 3 ERROR restantes, toutes justifiées (faux positifs S20, S21, S22 — S21 et S22 portent sur des outils ajoutés après le premier scan) |
| SAST (Bandit) | 0 | 0 |
| Secrets (gitleaks) | 0 (historique au commit `d21132a`, avant l'ajout des rapports au dépôt) | 242 constats, tous dans les rapports de preuve : 238 faux positifs (G1, G2), 4 jetons expirés (G3, corrigé pour l'avenir, résidu accepté) ; 0 dans le code ou la configuration |
| SCA dépendances (pip-audit, npm audit, Trivy fs) | 0 | 0 |
| SCA images (Trivy) | api : 53 High, 112 Medium, 68 Low, 7 Unknown ; web : 3 Critical, 65 High, 103 Medium, 46 Low | 0 sur les deux images |
| DAST baseline (ZAP) | 3 Low, 2 informations | 0 Low, 2 informations |
| DAST API (ZAP) | 1 High, 2 Low, 3 informations | 1 High **faux positif prouvé** (Z4), 0 Low, 3 informations |

Preuves « avant » : images reconstruites depuis le commit `80e8c79` (état avant correction) et analysées de nouveau
avec les mêmes outils — `reports/sca/trivy-image-api-avant.json`, `reports/sca/trivy-image-web-avant.json`,
`reports/sast/semgrep-avant.json`. Preuves « après » : les mêmes noms sans le suffixe `-avant`, relancés sur le code
de `99a818c` le 20/11/2026 par `scripts/security-scans.sh` (commandes réunies dans un script pour être rejouables).
Pour Bandit, gitleaks, pip-audit, npm audit et Trivy fs, aucun rapport « avant » n'a été conservé : la colonne
« Avant » vient du premier passage noté dans [`journal.md`](../journal.md).

**Critère de sortie (TP3)** : 0 High non traitée — la seule High restante (Z4) est un faux positif démontré par un
test exécuté ; les trois ERROR Semgrep restantes (S20 à S22) sont des faux positifs justifiés sur des outils locaux ;
0 Medium ; aucune Low restante. Risques acceptés par le groupe le 20/11/2026 : L1 et L2 (licences LGPL-3.0 et
MPL-2.0, usage conforme) ; le 20/11/2026 à 08:40 : résidu G3 (4 jetons de test expirés dans l'historique Git
local, jamais publié). Aucun autre risque de sécurité accepté.
