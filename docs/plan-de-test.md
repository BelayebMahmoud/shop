# Plan de test — Gestion commerciale (ISO/IEC 25010)

Étape **Planifier** du processus de test (fiche 1) : que teste-t-on, avec quels moyens, jusqu'à quand.
Exigences : [`exigences.yaml`](exigences.yaml) · scénarios : [`exigences.md`](exigences.md) ·
cas : [`cahier-de-test.md`](cahier-de-test.md) · architecture : [`conception.md`](conception.md).

## 1. Objet et portée

**Dans la portée** : l'API FastAPI (`backend/`), l'interface React (`web/`), la base PostgreSQL
(`db/migrations/`), la pile Docker Compose et le pipeline d'intégration continue. Toutes les exigences FR, BR et
QR du référentiel, soit les 8 caractéristiques ISO/IEC 25010 (modèle 2011 du Chapitre I) et la qualité en
utilisation.

**Hors portée** : paiement réel (le statut PAID est posé par le personnel), envoi d'emails, facturation,
déploiement en production, navigateurs autres que Chromium et Firefox (WebKit testé si disponible, sans
critère de sortie), charge au-delà de 20 utilisateurs simultanés, endurance de plusieurs heures.

## 2. Approche par niveau

Ordre d'exécution du plus rapide au plus lent (fiche 1) : formatage et SAST → unitaires → intégration, API,
SCA → E2E, compatibilité → performance, DAST.

| Niveau | Préfixe | Ce qu'on vérifie | Techniques (fiches 1 et 2) | Outils | Rapport produit |
| --- | --- | --- | --- | --- | --- |
| Qualité du code / SAST | MA, SEC | style, complexité, couches, failles du code, secrets | analyse statique, règles, flux de données (taint), détection de secrets | ruff, radon, xenon, import-linter, Semgrep, Bandit, gitleaks, Hadolint | `reports/maintenabilite/`, `reports/sast/` |
| Unitaire | CT | règles métier des services, isolées (sans base, sans HTTP) | partitions, valeurs limites, table de décision, transitions d'états, estimation d'erreur ; F.I.R.S.T., AAA ; couverture instructions + branches ; mutation ; propriétés | pytest, pytest-cov, mutmut, Hypothesis | `reports/junit-unit.xml`, `reports/coverage.xml` |
| Intégration | IT | chaque interface de `conception.md` §4, en succès et en erreur | test d'interface, flux de données, propagation d'erreur, bouchon ; base jetable | pytest + PostgreSQL de test | `reports/junit-integration.xml` |
| API | TA | statut, corps et effet réel ; contrat ; droits | table de décision dans l'ordre identité → forme → existence → règle ; cycle de vie ; matrice des droits ; robustesse | pytest + TestClient, Schemathesis | `reports/junit-api.xml`, `reports/api-coverage.md` |
| SCA | SEC | CVE des dépendances directes et indirectes, licences | inventaire (SBOM), rapprochement, atteignabilité | pip-audit, npm audit, Trivy, Syft, pip-licenses, license-checker | `reports/sca/` |
| E2E / compatibilité | E2E | parcours réels sur 2 navigateurs + mobile | cas d'usage, scénarios métier | Playwright Test (chromium, firefox, mobile) | `reports/junit-e2e.xml` |
| Utilisabilité | UX | accessibilité de base ; recette avec utilisateurs | heuristiques, test utilisateur, SUS | @axe-core/playwright, protocole `utilisabilite.md` | `reports/a11y/`, résultats calculés par script |
| Performance | PERF | temps de réponse, débit, ressources | profil de charge, mesure | k6, `docker stats`, EXPLAIN ANALYZE | `reports/perf/` |
| Fiabilité | REL | cohérence après panne, reprise, atomicité | injection de pannes, concurrence | pytest, k6, scripts de panne | `reports/reliability/` |
| DAST | SEC | l'application en marche, de l'extérieur | scan passif puis actif, 4 attaques manuelles | OWASP ZAP (conteneur), Playwright, pytest | `reports/dast/` |
| Portabilité | PORT | installation reproductible | installation propre chronométrée, seconde machine | Docker Compose, `scripts/installation-propre.sh` | `reports/portabilite/` |

Principes communs : l'oracle est la règle, jamais le code ; chaque test porte son identifiant de cas et
l'identifiant de l'exigence (`@pytest.mark.req`, `@BR-xx` dans les titres Playwright, tag `req` dans k6) ;
cas valides **et** cas d'échec attendu ; aucun test ne dépend d'un autre ni de données laissées par un autre ;
un échec ouvre une anomalie (`anomalies.md`) suivie d'un test de confirmation et d'une non-régression.

## 3. Environnements

| Environnement | Composition | Usage |
| --- | --- | --- |
| Poste de développement | Windows 11, Python 3.15 (venv `backend/.venv`), Node 26, Docker Desktop ; PostgreSQL 16 en conteneur sur le port hôte **5433** | unitaires, intégration, API, E2E |
| Base de test jetable | base `shop_test`, schéma reconstruit avant chaque test depuis `db/migrations` | intégration, API |
| Pile conteneurisée | `docker compose up -d --build --wait` : db, api, web (nginx) | E2E de recette, performance, fiabilité, DAST |
| Outils en conteneur | ZAP, k6, gitleaks, Trivy, Syft, Hadolint, Semgrep, mutmut (python:3.13) | outils non natifs sous Windows ou isolés |
| Seconde machine | poste d'un coéquipier, Docker uniquement | portabilité (PORT-02) |
| CI | GitHub Actions, étapes dans l'ordre de la fiche 1 | exécution automatique à chaque push |

Les scans actifs ne visent que `http://localhost`, après autorisation écrite (`securite/autorisation.md`).

## 4. Critères d'entrée et de sortie

**Entrée** (par niveau) : exigences et cas du niveau rédigés ; environnement démarré et sain
(`/api/health` = 200) ; `make check` vert sur le niveau précédent.

**Sortie** (fin de campagne) :

1. 100 % des FR et BR P0 au verdict PASS dans la matrice, ou chaque écart documenté (cause, impact, action).
2. Chaque cible QR atteinte, ou écart documenté avec la mesure réelle.
3. Sécurité (critère du TP3, retenu en P0) : 0 alerte High, 0 alerte Medium non justifiée, alertes Low
   justifiées, après relance des scans.
4. Aucune anomalie de gravité bloquante ou majeure ouverte.
5. Chaque nombre des rapports figure dans un fichier brut de `docs/preuves/v1.0/`.

**Suspension** : base indisponible, ou plus de 20 % des tests d'un niveau en échec pour une cause
d'environnement. **Reprise** : cause corrigée et niveau rejoué en entier.

## 5. Indicateurs (KPI)

| Indicateur | Cible | Exigence | Source de la mesure |
| --- | --- | --- | --- |
| FR/BR P0 au verdict PASS | 100 % | QR-FS-01 | `docs/tracabilite/matrice.csv` |
| Couverture app/services (instructions, branches) | >= 80 % | QR-MA-01 | `reports/coverage.xml` |
| Complexité cyclomatique maximale | <= 10 | QR-MA-02 | rapport radon / xenon |
| Score de mutation (pricing, commandes) | rapporté, mutants survivants listés | QR-MA-01 | rapport mutmut |
| p95 liste et détail, 20 utilisateurs | < 500 ms, erreurs < 1 % | QR-PE-01 | `reports/perf/load.json` |
| p95 recherche, 50 000 produits | < 800 ms, erreurs < 1 % | QR-PE-02 | `reports/perf/search.json` |
| E2E sur Chromium et Firefox | 100 % PASS | QR-CO-01 | `reports/junit-e2e.xml` |
| Schemathesis | 0 échec, 0 réponse 500 | QR-CO-02 | rapport Schemathesis |
| Violations axe serious/critical | 0 sur 5 pages | QR-US-01 | `reports/a11y/*.json` |
| Réussite des tâches / SUS moyen | >= 80 % / >= 68 (Q-12) | QR-US-02 | calcul par script |
| Temps de reprise après redémarrage de la base | < 60 s, 0 commande incohérente | QR-RE-01 | `reports/reliability/` |
| Alertes SAST/SCA/DAST | 0 High, 0 Medium non justifiée | QR-SE-01 | `reports/sast/`, `reports/sca/`, `reports/dast/` |
| Matrice des droits | 100 % conforme | QR-SE-02 | `reports/junit-api.xml` |
| Installation propre | < 10 min, smoke OK | QR-PO-01 | `reports/portabilite/*.log` |

## 6. Risques

| Risque | Probabilité | Impact | Mesure |
| --- | --- | --- | --- |
| Un outil ne s'exécute pas sous Windows (Semgrep, mutmut) | élevée | moyen | exécution en conteneur ; sinon « non disponible » avec procédure |
| Conflit de port 5432 avec un PostgreSQL Windows | constaté | moyen | base Docker sur 5433 (déjà fait) |
| Performance mesurée sur un poste portable, non représentatif | moyenne | moyen | environnement noté dans `reports/perf/environnement.txt` ; écart documenté si besoin |
| Pas de participants pour l'utilisabilité ce soir | moyenne | moyen | sessions le lendemain ; rapport « en attente » avec le protocole |
| Pas de seconde machine ce soir | moyenne | faible | script d'installation propre sur ce poste en résultat intermédiaire |
| Règle non décidée (Q-01 à Q-12) | constaté | moyen | cas marqués NON SPÉCIFIÉ, propositions soumises avant la phase 2 |
| Tests de concurrence instables | moyenne | moyen | synchronisation explicite (barrière), pas de pause fixe |
| Retard sur le planning | moyenne | élevé | coupes prévues aux points de contrôle CP1, CP2, CP3 du plan |

## 7. Calendrier (nuit du 19 au 20/11/2026)

| Phase | Horaire | Étape fiche 1 | Contenu |
| --- | --- | --- | --- |
| 1 | 18:50–19:30 | Planifier, Analyser, Concevoir | exigences, scénarios, plan, cahier, conception |
| 2 | 19:30–21:00 | Implémenter, Exécuter | fonctionnalités backend, tests unitaires, couverture (CP1 à 21:00) |
| 3 | 21:00–21:45 | Implémenter, Exécuter | intégration, API, contrat, matrice des droits |
| 4 | 22:00–22:50 | Implémenter, Exécuter | frontend, E2E, accessibilité, protocole d'utilisabilité |
| 5 | 22:50–23:30 | Implémenter, Exécuter | conteneurs, CI, installation propre |
| 6 | 23:30–00:30 | Exécuter | SAST, SCA, DAST, tri (CP2 à 00:30) |
| 7 | 00:30–01:15 | Exécuter | performance, fiabilité ; sessions d'utilisabilité |
| 8 | 01:15–01:45 | Exécuter | maintenabilité, résultats d'utilisabilité |
| 9 | 01:45–02:30 | Clôturer | matrice, conformité, rapport de test, gel des preuves (CP3 à 02:30) |
| 10 | 02:30–03:00 | Clôturer | vérification indépendante, démonstration, tag v1.0 |

## 8. Livrables de test

Plan de test (ce document), cahier de test, scripts (`backend/tests/**`, `web/e2e/**`, `perf/k6/**`,
`scripts/fiabilite/**`), rapports bruts (`reports/**`), journal des anomalies (`anomalies.md`), matrice de
traçabilité (`tracabilite/`), rapport de test (`rapport-de-test.md`), rapport de conformité (`conformite.md`).
