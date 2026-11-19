# Analyse initiale (P0) — exigences du cahier vs état du dépôt

Date : 19/11/2026 · commit de référence : `e7b6b30` · Aucun code écrit à cette étape.

Sources lues : `docs/cahier-des-charges.pdf`, `docs/cours/` (Chapitre I, fiches 1, 2 et 4, TP3 DAST),
`docs/plan-de-la-nuit.md`. Les fiches 3 et 5 ne sont pas fournies (confirmé).

État : **fait** / **partiel** / **manquant**.

## 1. §4 — Exigences fonctionnelles minimales

| Exigence §4 | État | Constat dans le dépôt |
| --- | --- | --- |
| Authentification et ≥ 3 rôles | partiel | JWT (`/auth/register`, `/login`, `/me`), mots de passe Argon2 ; aucun rôle (table `users` sans colonne `role`) |
| ≥ 4 entités liées (1-N, N-N) avec CRUD complet | partiel | `User`, `Product`, `Order`, `OrderItem` (N-N Order↔Product) ; pas de `Category` ; produits en lecture seule, commandes : création + liste |
| Workflow à statuts avec règles de transition | manquant | colonne `status` = `PLACED` seulement, aucune transition |
| Tableau de bord (indicateurs agrégés, filtres) | manquant | — |
| Recherche / filtrage sur une entité à fort volume | partiel | recherche texte `q` + pagination sur 8 produits ; ni volume, ni filtres catégorie/prix/stock |
| Journal d'audit | manquant | — |
| ≥ 5 règles métier documentées et testables | partiel | déjà codées sans documentation : stock jamais négatif (409), prix pris côté serveur, fusion des lignes en double, email unique (409) |

## 2. §6 — Les 8 caractéristiques ISO 25010 (exigence + test/outil + preuve)

| Caractéristique | État | Constat |
| --- | --- | --- |
| 6.1 Aptitude fonctionnelle | partiel | 8 tests pytest (API + base réelle), sans ID d'exigence ni rapport |
| 6.2 Efficacité de performance | manquant | aucun test de charge |
| 6.3 Compatibilité | manquant | OpenAPI générée par FastAPI mais non vérifiée ; aucun test multi-navigateurs |
| 6.4 Facilité d'utilisation | manquant | aucune page de gestion, ni axe, ni session utilisateur |
| 6.5 Fiabilité | partiel | verrouillage `FOR UPDATE` contre la survente ; `/api/health` ne vérifie pas la base ; aucun test |
| 6.6 Sécurité | partiel | Argon2, JWT avec expiration, requêtes paramétrées (ORM) ; ni RBAC, ni SAST, SCA ou DAST |
| 6.7 Maintenabilité | partiel | ruff configuré (`E`, `F`) ; pas de couche services ; ni couverture, ni complexité mesurée |
| 6.8 Portabilité | partiel | Docker Compose pour la base seulement ; pas de Dockerfile api/web, pas de guide |

## 3. §7 — Couches de test

| Couche | État | | Couche | État |
| --- | --- | --- | --- | --- |
| Unitaires | manquant | | SAST | manquant |
| Intégration | partiel (TestClient + PostgreSQL jetable) | | SCA | manquant |
| API | partiel (statut + corps + effet sur le stock) | | DAST | manquant |
| E2E | manquant | | Qualité / maintenabilité | partiel (ruff) |
| Performance | manquant | | Compatibilité | manquant |
| Fiabilité | manquant | | Portabilité | manquant |

## 4. §8 — Livrables

| Livrable | État |
| --- | --- |
| Code versionné avec historique | partiel (Git initialisé, 2 commits de configuration) |
| Rapport de conception | manquant |
| Matrice de traçabilité | manquant |
| Jeux de tests exécutables + rapports générés | partiel (tests MVP, aucun rapport dans `reports/`) |
| Rapport de conformité ISO 25010 | manquant |
| Guide d'installation | manquant (`web/README.md` est le modèle Vite) |
| Soutenance (démo + 2 couches de test) | manquant |
| Plan, cahier et rapport de test (fiche 1) | manquant |

Conclusion : l'écart correspond à la section 1 du plan. Le MVP couvre environ la moitié de §4 ;
§6, §7 et §8 restent presque entièrement à produire.

## 5. Contradictions et points d'attention

| # | Plan | Source | Constat et proposition |
| --- | --- | --- | --- |
| 1 | Phase 6 : sortie = « 0 alerte haute non traitée » | TP3 §3.1 : 0 High, **0 Medium non justifiée**, Low justifiées | Le plan est moins strict que le TP. Proposition : adopter le critère du TP3 pour SAST, SCA et DAST |
| 2 | SEC « session » : jeton expiré → 401 | Fiche 4 p. 6 : « rester inactif, puis rejouer une requête → demande de reconnexion » | L'expiration absolue JWT (30 min) n'est pas une expiration après inactivité. Proposition : documenter l'équivalence et la limite dans `conformite.md` (ou ajouter un délai d'inactivité) |
| 3 | BR-03 → 422 | Fiche 2 p. 7 (exemple TA-03 : quantité 0 → 400) | Pas une contradiction : la fiche admet le code « selon l'API ». Justifier 422 (FastAPI/Pydantic) dans `conception.md` |
| 4 | TP3 : vérifier l'en-tête `Server` (D02) et l'absence de message technique | Le plan cite seulement CSP, X-Content-Type-Options, frame-ancestors, Referrer-Policy | Ajouter en phase 5 : en-tête `Server` sans version (nginx `server_tokens off`), messages d'erreur génériques, cookies `HttpOnly`/`Secure` s'il y en a |
| 5 | Phase 8 : mutmut | Environnement Windows | mutmut 3 ne s'exécute pas nativement sous Windows. Proposition : le lancer dans un conteneur `python:3.13` (ou WSL) |
| 6 | Phase 6 : Semgrep | Environnement Windows | Semgrep ne fonctionne pas nativement sous Windows. Proposition : image Docker `semgrep/semgrep` (absente de la liste de pull de la mise en place) |
| 7 | `make check` à chaque phase | Environnement | `make` n'est pas installé. Les recettes sont lancées directement, ou après `choco install make` |
| 8 | Prérequis Python 3.12+, image `python:3.13-slim` | Poste : Python 3.15 | Les versions épinglées s'installent en 3.15 ; à revérifier en 3.13 lors de la construction de l'image (phase 5) |
| 9 | Base sur `localhost:5432` | Poste | Un service PostgreSQL Windows occupe 5432 : la base Docker est sur **5433** (déjà fait, commit `e7b6b30`) |
| 10 | Rapport de conformité | Chapitre I | Le cours suit le modèle ISO 25010:2011 (8 caractéristiques + 5 en utilisation). Le plan s'y tient et ajoute un tableau 2011 → 2023 : cohérent |

## 6. Questions bloquantes

1. **Domaine** : l'encadrant a-t-il validé *Gestion commerciale* (clients, produits, stock, commandes, sans facturation) ?
2. **Critère de sortie sécurité** : adopte-t-on celui du TP3 (0 High, 0 Medium non justifiée, Low justifiées) au lieu de « 0 haute non traitée » ?
3. **Outils sous Windows** : peut-on lancer Semgrep et mutmut dans des conteneurs Docker et installer `make` avec Chocolatey ?
