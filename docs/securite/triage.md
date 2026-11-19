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
| S20 | Semgrep | `dangerous-subprocess-use-tainted-env-args` | `tools/capture.py:24` | ERROR (High) | **fausse** | Outil de développement dont le rôle est précisément d'exécuter la commande que le développeur lui passe sur la ligne de commande ; aucune entrée réseau ni utilisateur final ; non embarqué dans les images | justifier (faux positif), conserver | présente, justifiée |
| — | Bandit | toutes règles | `backend/app` (1 036 lignes) | — | — | aucun constat | — | aucun |
| — | gitleaks | toutes règles | historique Git complet | — | — | aucun secret (le `.env` réel est ignoré par Git, vérifié) | — | aucun |

## 2. SCA (dépendances, images, licences)

| # | Outil | Paquet / image | Gravité (avant) | Vraie / fausse | Atteignabilité | Décision | Statut après relance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | pip-audit | 31 paquets Python (directs et transitifs) | aucune | — | — | — | aucune |
| D2 | npm audit, Trivy fs | dépendances web (`package-lock.json`, transitives incluses) | aucune | — | — | — | aucune |
| I1 | Trivy image | `shop-api` sur Debian 13 (slim) : utilitaires système (util-linux, acl…) | 53 High, 112 Medium, 68 Low | vraies | non atteignables par l'application (outils système jamais appelés), mais sans version corrigée | **remplacer** : image de base Alpine (moins de paquets) | voir I3 |
| I2 | Trivy image | `shop-web` sur nginx 1.27 / Alpine 3.21 (openssl, curl, brotli, expat, nginx) | 3 Critical, 65 High, 103 Medium, 46 Low | vraies (openssl et nginx exposés au réseau) | atteignables pour openssl et nginx | **mettre à jour** : nginx 1.31.7, Alpine 3.24, `apk upgrade` à la construction | aucune |
| I3 | Trivy image | `shop-api` Alpine : pip/setuptools embarqués (urllib3, msgpack, setuptools), openssl, zlib | 5 High, 11 Medium (étapes intermédiaires) | vraies | pip non utilisé à l'exécution | **corriger** : pip et setuptools retirés de l'image, `apk upgrade` | aucune |
| C1 | Hadolint | `backend/Dockerfile` : `USER api` (DL3066, info) | info | vraie | — | corriger : `USER 10001` | aucune |
| L1 | pip-licenses | psycopg, psycopg-binary : LGPL-3.0 | — | à surveiller | bibliothèque utilisée sans modification, liée dynamiquement | accepter (usage conforme à la LGPL) — **à valider par le groupe** | — |
| L2 | pip-licenses | certifi, hypothesis : MPL-2.0 | — | à surveiller | fichiers non modifiés ; hypothesis sert aux tests seulement | accepter (usage conforme à la MPL) — **à valider par le groupe** | — |
| L3 | license-checker | dépendances web de production : MIT ; « UNLICENSED » = notre propre paquet privé | — | fausse (notre paquet) | — | — | — |

Inventaire (SBOM CycloneDX, Syft) : `reports/sca/sbom-api.cdx.json` (995 composants) et
`reports/sca/sbom-web.cdx.json` (1 282 composants), dépendances transitives et paquets système inclus.

## 3. DAST

En attente de la signature de [`autorisation.md`](autorisation.md) : aucun scan dynamique n'est lancé avant.
Prévu : ZAP baseline (passif) sur `http://web:8080`, puis ZAP API scan (actif) sur le contrat OpenAPI, depuis le
réseau Docker Compose, puis tri ici, correction et nouveau scan.

Attaques manuelles automatisées (fiche 4, déjà exécutées sur la base de test) : SEC-01 injection SQL, SEC-03
contrôle d'accès, SEC-04 session (`reports/junit-security.xml`, 7 réussis) ; SEC-02 XSS stocké
(`reports/junit-e2e-docker.xml`, réussi sur chromium, firefox et mobile).

## 4. Bilan provisoire (avant DAST)

| Famille | Avant | Après relance |
| --- | --- | --- |
| SAST (Semgrep) | 2 ERROR, 18 WARNING | 1 ERROR, justifiée (faux positif S20) |
| SAST (Bandit), secrets (gitleaks) | 0 | 0 |
| SCA dépendances (pip-audit, npm audit, Trivy fs) | 0 | 0 |
| SCA images (Trivy) | api : 53 High, 112 Medium, 68 Low, 7 Unknown ; web : 3 Critical, 65 High, 103 Medium, 46 Low | 0 sur les deux images |

Preuves « avant » : images reconstruites depuis le commit `80e8c79` (état avant correction) et analysées de nouveau
avec les mêmes outils — `reports/sca/trivy-image-api-avant.json`, `reports/sca/trivy-image-web-avant.json`,
`reports/sast/semgrep-avant.json`. Preuves « après » : les mêmes noms sans le suffixe `-avant`.

Risques proposés à l'acceptation, **en attente de la décision du groupe** : L1 et L2 (licences). Aucun risque de
sécurité n'est accepté à ce stade.
