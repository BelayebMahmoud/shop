# Exigences et scénarios — Gestion commerciale

Référentiel : [`exigences.yaml`](exigences.yaml) (identifiants, priorités, caractéristiques, cibles).
Ce document traduit chaque exigence en scénarios **Soit / Quand / Alors** (fiche 1, méthode commune) :
au moins un scénario valide et un scénario de refus par règle. Les résultats attendus viennent des règles,
jamais du code. Quand une règle ne tranche pas, le scénario renvoie à une question ouverte (Q-xx, fin de document).

Chaîne suivie (fiche 1) : exigence → condition de test → scénario → cas de test
([`cahier-de-test.md`](cahier-de-test.md)) → script → verdict.

Données de référence utilisées dans les scénarios (créées par chaque test, jamais partagées) :

| Donnée | Valeur |
| --- | --- |
| Produit P1 | SKU `P1-TEST`, prix 40,00 €, stock 10, catégorie « Papeterie » |
| Produit P2 | SKU `P2-TEST`, prix 50,00 €, stock 3, catégorie « Papeterie » |
| Clients | Ana (CUSTOMER), Bob (CUSTOMER) |
| Personnel | Sam (STAFF), Alice (ADMIN) |

## 1. Exigences fonctionnelles

### FR-01 — Authentification
- **SC-FR-01-1 (valide)** — Soit un visiteur sans compte, quand il s'inscrit avec `ana@example.com` et un mot de passe de 8 caractères, puis se connecte, alors il reçoit un jeton et `/api/auth/me` renvoie son email et le rôle CUSTOMER.
- **SC-FR-01-2 (refus)** — Soit Ana inscrite, quand elle se connecte avec un mauvais mot de passe, alors la réponse est 401, aucun jeton n'est émis et une entrée « connexion échouée » est journalisée.

### FR-02 — Rôles et droits
- **SC-FR-02-1 (valide)** — Soit Sam (STAFF) connecté, quand il crée un produit, alors la réponse est 201.
- **SC-FR-02-2 (refus)** — Soit Ana (CUSTOMER) connectée, quand elle tente de créer un produit, alors la réponse est 403 et aucun produit n'est créé.

### FR-03 — CRUD des catégories
- **SC-FR-03-1 (valide)** — Soit Sam connecté, quand il crée, lit, renomme puis supprime une catégorie vide, alors il obtient 201, 200, 200, 204, et une nouvelle lecture renvoie 404.
- **SC-FR-03-2 (refus)** — Soit un visiteur non connecté, quand il tente de créer une catégorie, alors la réponse est 401.

### FR-04 — CRUD des produits
- **SC-FR-04-1 (valide)** — Soit Alice (ADMIN) connectée, quand elle crée P1 puis le modifie (prix 42,00 €), alors la lecture de P1 renvoie 42,00 €.
- **SC-FR-04-2 (refus)** — Soit Alice connectée, quand elle crée un produit avec un prix négatif et un SKU vide, alors la réponse est 422 avec une erreur par champ fautif, et aucun produit n'est créé.

### FR-05 — Gestion des utilisateurs
- **SC-FR-05-1 (valide)** — Soit Alice connectée, quand elle passe Bob en STAFF, alors Bob peut ensuite consulter le tableau de bord, et le changement de rôle est journalisé.
- **SC-FR-05-2 (refus)** — Soit Bob désactivé par Alice, quand Bob se connecte, alors la réponse est 401, et un jeton émis avant la désactivation est lui aussi refusé (401, décision Q-08).

### FR-06 — Commandes côté client
- **SC-FR-06-1 (valide)** — Soit Ana connectée, quand elle commande 2 × P1, alors la commande est créée au statut PLACED et apparaît dans « mes commandes ».
- **SC-FR-06-2 (refus)** — Soit Ana connectée, quand elle commande un produit qui n'existe pas, alors la réponse est 404 et rien ne change.

### FR-07 — Commandes côté back-office
- **SC-FR-07-1 (valide)** — Soit une commande PLACED d'Ana, quand Sam la passe à PAID, alors son statut devient PAID.
- **SC-FR-07-2 (refus)** — Soit la même commande, quand Ana tente de la passer à PAID, alors la réponse est 403 et le statut reste PLACED.

### FR-08 — Workflow de commande
- **SC-FR-08-1 (valide)** — Soit une commande PLACED, quand Sam la passe successivement à PAID, SHIPPED puis DELIVERED, alors chaque étape réussit et le statut final est DELIVERED. Les refus sont décrits en BR-05 et BR-06.

### FR-09 — Tableau de bord
- **SC-FR-09-1 (valide)** — Soit des commandes à plusieurs statuts et un produit au stock 4, quand Sam ouvre le tableau de bord, alors il voit le nombre de commandes par statut, le chiffre d'affaires (commandes PAID, SHIPPED, DELIVERED, total après remise — Q-03), les 5 produits les plus vendus et le produit au stock 4 dans « stock faible ».
- **SC-FR-09-2 (refus)** — Soit Ana (CUSTOMER) connectée, quand elle appelle le tableau de bord, alors la réponse est 403.

### FR-10 — Recherche à fort volume
- **SC-FR-10-1 (valide)** — Soit 50 000 produits, quand un visiteur cherche « mug » dans la catégorie « Cuisine », entre 10,00 € et 20,00 €, en stock seulement, alors chaque résultat respecte tous les filtres, et le total indique le nombre de résultats correspondants.
- **SC-FR-10-2 (refus)** — Soit le catalogue, quand un visiteur demande une page de 101 éléments, alors la réponse est 422.

### FR-11 — Journal d'audit
- **SC-FR-11-1 (valide)** — Soit Sam connecté, quand il passe une commande à SHIPPED, alors une entrée d'audit indique Sam, l'action « statut changé », la commande, l'ancien et le nouveau statut, et l'heure.
- **SC-FR-11-2 (refus)** — Soit des entrées d'audit, quand Alice tente de modifier ou supprimer une entrée, alors aucune route ne le permet (405) et les entrées sont inchangées.

## 2. Règles métier

### BR-01 — Stock jamais négatif
- **SC-BR-01-1 (valide, limite)** — Soit P2 au stock 3, quand Ana commande 3 × P2, alors la commande est créée et le stock de P2 devient 0.
- **SC-BR-01-2 (refus, limite)** — Soit P2 au stock 3, quand Ana commande 4 × P2, alors la réponse est 409 OUT_OF_STOCK, aucune commande n'est créée et le stock reste 3.

### BR-02 — Prix pris au catalogue
- **SC-BR-02-1 (valide)** — Soit P1 à 40,00 €, quand Ana commande 1 × P1, alors le prix unitaire de la ligne est 40,00 €.
- **SC-BR-02-2 (refus du prix client)** — Soit P1 à 40,00 €, quand Ana envoie une ligne avec un prix de 0,01 €, alors le prix est ignoré et la ligne est enregistrée à 40,00 €.

### BR-03 — Bornes de quantité et de lignes
- **SC-BR-03-1 (valide, limites)** — Soit Ana connectée, quand elle commande une ligne de quantité 1, puis une ligne de quantité 99, alors les deux commandes sont acceptées (stock suffisant).
- **SC-BR-03-2 (refus, quantité)** — Soit Ana connectée, quand elle envoie une ligne de quantité 0 ou 100, alors la réponse est 422 et rien ne change.
- **SC-BR-03-3 (refus, lignes)** — Soit Ana connectée, quand elle envoie 0 ligne ou 51 lignes, alors la réponse est 422 ; avec 50 lignes, la commande est acceptée. Les bornes portent sur les lignes envoyées ; les doublons de produit sont fusionnés ensuite (Q-01).

### BR-04 — Remise sur le sous-total
- **SC-BR-04-1 (valide, sans remise)** — Soit un sous-total de 99,99 €, quand la commande est calculée, alors la remise est 0,00 € et le total 99,99 €.
- **SC-BR-04-2 (valide, 5 %, limite basse)** — Soit un sous-total de 100,00 €, quand la commande est calculée, alors la remise est 5,00 € et le total 95,00 €.
- **SC-BR-04-3 (valide, 10 %, limite)** — Soit un sous-total de 200,00 €, quand la commande est calculée, alors la remise est 20,00 € et le total 180,00 €.
- **SC-BR-04-4 (valide, arrondi)** — Soit un sous-total de 100,10 €, quand la commande est calculée, alors 5 % = 5,005 € est arrondi à 5,01 € (demi vers le haut) et le total est 95,09 €.
- **SC-BR-04-5 (refus)** — Soit un sous-total négatif (-0,01 €), quand la remise est calculée, alors le calcul est refusé (valeur invalide) ; une commande ne peut pas produire ce cas puisque les prix sont >= 0.

### BR-05 — Transitions de statut et droits
- **SC-BR-05-1 (valide)** — Soit une commande PAID, quand Sam la passe à SHIPPED, alors le statut devient SHIPPED.
- **SC-BR-05-2 (refus, transition)** — Soit une commande PLACED, quand Sam la passe directement à DELIVERED, alors la réponse est 409 INVALID_TRANSITION et le statut reste PLACED.
- **SC-BR-05-3 (refus, rôle)** — Soit une commande PLACED d'Ana, quand Ana la passe à PAID, alors la réponse est 403 et le statut reste PLACED. Si la commande d'Ana est PAID, son annulation par Ana est refusée : 403 (Q-02).

### BR-06 — Annulation et remise en stock
- **SC-BR-06-1 (valide)** — Soit une commande PLACED d'Ana avec 2 × P1 et 1 × P2 (stocks 8 et 2 après commande), quand Ana l'annule, alors le statut devient CANCELLED et les stocks reviennent à 10 et 3.
- **SC-BR-06-2 (refus)** — Soit une commande SHIPPED, quand Sam tente de l'annuler, alors la réponse est 409 INVALID_TRANSITION, le statut reste SHIPPED et les stocks ne changent pas.

### BR-07 — Unicité
- **SC-BR-07-1 (valide)** — Soit `ana@example.com` inscrite, quand `bob@example.com` s'inscrit, alors la réponse est 201.
- **SC-BR-07-2 (refus)** — Soit `ana@example.com` inscrite, quand quelqu'un s'inscrit avec `ANA@Example.com`, alors la réponse est 409. De même pour un SKU ou un nom de catégorie déjà utilisé (sans tenir compte de la casse, Q-06).

### BR-08 — Isolation des commandes
- **SC-BR-08-1 (valide)** — Soit une commande d'Ana, quand Ana la lit, alors la réponse est 200 avec ses lignes.
- **SC-BR-08-2 (refus)** — Soit une commande d'Ana, quand Bob la lit ou tente de l'annuler, alors la réponse est 404 et la commande ne change pas.

### BR-09 — Catégorie non vide
- **SC-BR-09-1 (valide)** — Soit une catégorie vide, quand Sam la supprime, alors la réponse est 204.
- **SC-BR-09-2 (refus)** — Soit la catégorie « Papeterie » qui contient P1, quand Sam la supprime, alors la réponse est 409 et la catégorie existe toujours.

### BR-10 — Produit déjà commandé (issue de Q-07)
- **SC-BR-10-1 (valide)** — Soit un produit jamais commandé, quand Sam le supprime, alors la réponse est 204.
- **SC-BR-10-2 (refus)** — Soit P1 présent dans une commande d'Ana, quand Sam supprime P1, alors la réponse est 409 PRODUCT_IN_USE et P1 existe toujours.

### BR-11 — Au moins un ADMIN actif (issue de Q-09)
- **SC-BR-11-1 (valide)** — Soit deux ADMIN actifs (Alice et Zoé), quand Alice passe Zoé en STAFF, alors la réponse est 200.
- **SC-BR-11-2 (refus)** — Soit Alice seule ADMIN active, quand Alice se retire le rôle ADMIN ou se désactive, alors la réponse est 409 LAST_ADMIN et Alice reste ADMIN active.

## 3. Exigences de qualité

| Exigence | Scénario Soit / Quand / Alors |
| --- | --- |
| QR-FS-01 | Soit tous les rapports de test, quand la matrice est générée, alors chaque FR et BR P0 est au verdict PASS. |
| QR-PE-01 | Soit la pile en conteneurs et 20 utilisateurs virtuels pendant 5 min sur liste et détail, quand k6 s'exécute, alors p95 < 500 ms et erreurs < 1 %. |
| QR-PE-02 | Soit 50 000 produits, quand k6 exécute des recherches filtrées, alors p95 < 800 ms et erreurs < 1 %. |
| QR-CO-01 | Soit les 5 parcours E2E, quand Playwright les exécute sur Chromium et Firefox, alors tous passent. |
| QR-CO-02 | Soit le contrat `/openapi.json`, quand Schemathesis génère des requêtes, alors aucune réponse ne viole le contrat et aucune n'est une 500. |
| QR-US-01 | Soit les 5 pages principales, quand axe les analyse, alors aucune violation serious ou critical. |
| QR-US-02 | Soit 3 à 5 participants et 3 tâches, quand ils les réalisent, alors réussite >= 80 % et SUS moyen >= 68 (Q-12). |
| QR-RE-01 | Soit une charge en cours, quand PostgreSQL redémarre, alors /api/health répond 503 pendant la panne, le service revient en moins de 60 s et aucune commande n'est incohérente. |
| QR-RE-02 | Soit deux commandes simultanées pour les 2 dernières unités, quand elles arrivent ensemble, alors une seule réussit et le stock final est 0. |
| QR-SE-01 | Soit les rapports SAST, SCA et DAST, quand le tri est terminé, alors 0 High, 0 Medium non justifiée, Low justifiées. |
| QR-SE-02 | Soit la matrice des droits, quand chaque rôle appelle chaque route, alors chaque réponse correspond à la matrice ; les 4 attaques manuelles sont refusées. |
| QR-MA-01 | Soit les tests unitaires, quand la couverture est mesurée, alors app/services atteint 80 % en instructions et en branches. |
| QR-MA-02 | Soit le code de backend/app, quand radon, xenon et import-linter s'exécutent, alors complexité <= 10 et aucune dépendance inverse. |
| QR-PO-01 | Soit une machine avec Docker, quand on suit `docs/installation.md`, alors la pile démarre et le smoke test passe en moins de 10 min. |

## 4. Questions tranchées

Ces points n'étaient pas décidés par les règles initiales. Toutes les propositions ont été acceptées par le groupe
le 19/11/2026 ; elles font désormais partie des règles (Q-07 et Q-09 ont créé BR-10 et BR-11).

| ID | Exigence | Question | Décision |
| --- | --- | --- | --- |
| Q-01 | BR-03 | Doublons de produit : bornes avant ou après fusion des lignes ? | Bornes sur les lignes envoyées, fusion ensuite |
| Q-02 | BR-05 | CUSTOMER qui annule sa commande PAID : 403 ou 409 ? | 403 |
| Q-03 | FR-09 | Commandes comptées dans le chiffre d'affaires et le top 5 ? | PAID, SHIPPED, DELIVERED ; total après remise |
| Q-04 | FR-09 | Bornes de période incluses ? Fuseau ? | Incluses, UTC ; début > fin -> 422 |
| Q-05 | FR-10 | Bornes de prix incluses ? min > max ? | Incluses ; min > max -> 422 |
| Q-06 | BR-07 | SKU et nom de catégorie insensibles à la casse ? | Oui |
| Q-07 | FR-04 | Suppression d'un produit déjà commandé ? | Nouvelle règle BR-10 : 409 PRODUCT_IN_USE |
| Q-08 | FR-05 | Jeton émis avant désactivation ? | Refusé (401) |
| Q-09 | FR-05 | Retrait du dernier ADMIN actif ? | Nouvelle règle BR-11 : 409 |
| Q-10 | FR-06 | STAFF et ADMIN peuvent-ils commander ? | Non, 403 |
| Q-11 | FR-11 | Qui lit le journal d'audit ? | ADMIN seulement |
| Q-12 | QR-US-02 | Cibles chiffrées d'utilisabilité ? | Réussite >= 80 %, SUS >= 68 |
