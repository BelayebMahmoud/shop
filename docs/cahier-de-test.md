# Cahier de test — Gestion commerciale

Étapes **Analyser** et **Concevoir** (fiche 1). Chaque cas a les champs de la fiche 2 : ID, objectif, règle
couverte, préconditions, données d'entrée, étapes, résultat attendu, résultat obtenu, verdict, type
(valide / échec attendu). « Obtenu » et « Verdict » restent vides : ils sont remplis en phase 9 par un script,
à partir des rapports des outils (règle d'or).

Le résultat attendu vient de la règle ([`exigences.yaml`](exigences.yaml)) ou du contrat de
[`conception.md`](conception.md), jamais du code. Les questions Q-01 à Q-12 ont été tranchées le 19/11/2026 ;
un attendu qui en dépend porte la mention « décision Q-xx ».

Conventions : montants en euros (stockés en centimes) ; P1 = 40,00 €, stock 10 ; P2 = 50,00 €, stock 3 ;
Ana et Bob = CUSTOMER, Sam = STAFF, Alice = ADMIN. Chaque test crée ses propres données.

## 0. Tables de conception (techniques de la fiche 2)

### 0.1 BR-03 — Partitions et valeurs limites

| Donnée | Partition invalide basse | Partition valide | Partition invalide haute | Valeurs limites testées |
| --- | --- | --- | --- | --- |
| Quantité d'une ligne | <= 0 | 1 à 99 | >= 100 | -1 (estimation d'erreur), 0, 1, 99, 100 |
| Nombre de lignes | 0 | 1 à 50 | >= 51 | 0, 1, 50, 51 |

### 0.2 BR-04 — Partitions, limites et arrondi

| Partition du sous-total | Taux | Représentant | Limites testées | Cas |
| --- | --- | --- | --- | --- |
| < 0 (invalide) | erreur | — | -0,01 | CT-18 |
| 0 à 99,99 € | 0 % | 50,00 | 0,00 ; 99,99 | CT-52, CT-10, CT-11 |
| 100,00 à 199,99 € | 5 % | 150,00 | 100,00 ; 199,99 | CT-12, CT-13, CT-14 |
| >= 200,00 € | 10 % | 300,00 | 200,00 | CT-15, CT-16 |
| Arrondi demi vers le haut | 5 % | 100,10 (5,005 -> 5,01) | — | CT-17 |

### 0.3 Création de commande — Table de décision (ordre des contrôles : identité → forme → existence → règle)

| Condition / règle | R1 | R2 | R3 | R4 | R5 |
| --- | --- | --- | --- | --- | --- |
| Jeton valide ? | non | oui | oui | oui | oui |
| Corps valide (BR-03) ? | — | non | oui | oui | oui |
| Tous les produits existent ? | — | — | non | oui | oui |
| Stock suffisant (BR-01) ? | — | — | — | non | oui |
| **Résultat** | 401 | 422 | 404 | 409 OUT_OF_STOCK | 201 |
| **Effet** | rien | rien | rien | rien | commande + lignes + stock décrémenté + audit |
| **Cas API** | TA-03 | TA-05 | TA-29 | TA-06 | TA-04 |

### 0.4 BR-05 / BR-06 — Table des transitions d'états (chaque état × chaque événement)

Événements : `payer` (→ PAID), `expédier` (→ SHIPPED), `livrer` (→ DELIVERED), `annuler` (→ CANCELLED).
Acteur : STAFF sauf mention. Toute cellule « refus » = 409 INVALID_TRANSITION et état inchangé.

| État \ événement | payer | expédier | livrer | annuler |
| --- | --- | --- | --- | --- |
| PLACED | **PAID** (CT-19) | refus (CT-24) | refus (CT-25) | **CANCELLED** + remise en stock (CT-22) |
| PAID | refus (CT-26) | **SHIPPED** (CT-20) | refus (CT-27) | **CANCELLED** + remise en stock (CT-23) |
| SHIPPED | refus (CT-28) | refus (CT-29) | **DELIVERED** (CT-21) | refus (CT-30) |
| DELIVERED | refus (CT-31) | refus (CT-32) | refus (CT-33) | refus (CT-34) |
| CANCELLED | refus (CT-35) | refus (CT-36) | refus (CT-37) | refus (CT-38) |

Droits (BR-05) : `payer`, `expédier`, `livrer` réservés à STAFF et ADMIN (ADMIN : CT-53 ; CUSTOMER → 403,
CT-39, CT-54, CT-55) ; un CUSTOMER qui annule une commande SHIPPED reçoit 409 (BR-06, CT-56) ;
CUSTOMER : `annuler` sur sa propre commande PLACED seulement (CT-40 ; PAID → 403, CT-41, décision Q-02).

## 1. Tests unitaires (CT) — services, sans base ni HTTP

| ID | Objectif | Règle | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CT-01 | Refuser une quantité nulle | BR-03 | aucune | 1 ligne, quantité 0 | valider la commande | refus de validation (422 côté API) | | | échec attendu |
| CT-02 | Accepter la quantité minimale | BR-03 | aucune | 1 ligne, quantité 1 | valider la commande | accepté | | | valide |
| CT-03 | Accepter la quantité maximale | BR-03 | aucune | 1 ligne, quantité 99 | valider la commande | accepté | | | valide |
| CT-04 | Refuser la quantité au-delà du maximum | BR-03 | aucune | 1 ligne, quantité 100 | valider la commande | refus de validation (422) | | | échec attendu |
| CT-05 | Refuser une quantité négative | BR-03 | aucune | 1 ligne, quantité -1 | valider la commande | refus de validation (422) | | | échec attendu |
| CT-06 | Refuser une commande vide | BR-03 | aucune | 0 ligne | valider la commande | refus de validation (422) | | | échec attendu |
| CT-07 | Accepter une seule ligne | BR-03 | aucune | 1 ligne, quantité 1 | valider la commande | accepté | | | valide |
| CT-08 | Accepter 50 lignes | BR-03 | aucune | 50 lignes de produits distincts, quantité 1 | valider la commande | accepté | | | valide |
| CT-09 | Refuser 51 lignes | BR-03 | aucune | 51 lignes de produits distincts, quantité 1 | valider la commande | refus de validation (422) | | | échec attendu |
| CT-10 | Pas de remise, partition basse | BR-04 | aucune | sous-total 50,00 € | calculer la remise | remise 0,00 € ; total 50,00 € | | | valide |
| CT-11 | Pas de remise, juste sous 100 € | BR-04 | aucune | sous-total 99,99 € | calculer la remise | remise 0,00 € ; total 99,99 € | | | valide |
| CT-12 | 5 % à la limite basse | BR-04 | aucune | sous-total 100,00 € | calculer la remise | remise 5,00 € ; total 95,00 € | | | valide |
| CT-13 | 5 %, représentant | BR-04 | aucune | sous-total 150,00 € | calculer la remise | remise 7,50 € ; total 142,50 € | | | valide |
| CT-14 | 5 % juste sous 200 €, avec arrondi | BR-04 | aucune | sous-total 199,99 € | calculer la remise | 9,9995 → remise 10,00 € ; total 189,99 € | | | valide |
| CT-15 | 10 % à la limite | BR-04 | aucune | sous-total 200,00 € | calculer la remise | remise 20,00 € ; total 180,00 € | | | valide |
| CT-16 | 10 %, représentant | BR-04 | aucune | sous-total 300,00 € | calculer la remise | remise 30,00 € ; total 270,00 € | | | valide |
| CT-17 | Arrondi demi vers le haut | BR-04 | aucune | sous-total 100,10 € | calculer la remise | 5,005 → remise 5,01 € ; total 95,09 € | | | valide |
| CT-18 | Refuser un sous-total négatif | BR-04 | aucune | sous-total -0,01 € | calculer la remise | erreur (valeur invalide) | | | échec attendu |
| CT-19 | Payer une commande PLACED | BR-05, FR-08 | commande PLACED ; acteur STAFF | événement payer | appliquer la transition | statut PAID | | | valide |
| CT-20 | Expédier une commande PAID | BR-05, FR-08 | commande PAID ; STAFF | expédier | appliquer | statut SHIPPED | | | valide |
| CT-21 | Livrer une commande SHIPPED | BR-05, FR-08 | commande SHIPPED ; STAFF | livrer | appliquer | statut DELIVERED | | | valide |
| CT-22 | Annuler une commande PLACED | BR-05, BR-06, FR-08 | commande PLACED ; STAFF | annuler | appliquer | statut CANCELLED | | | valide |
| CT-23 | Annuler une commande PAID | BR-05, BR-06, FR-08 | commande PAID ; STAFF | annuler | appliquer | statut CANCELLED | | | valide |
| CT-24 | Expédier sans paiement | BR-05 | commande PLACED ; STAFF | expédier | appliquer | INVALID_TRANSITION ; reste PLACED | | | échec attendu |
| CT-25 | Livrer depuis PLACED | BR-05 | PLACED ; STAFF | livrer | appliquer | INVALID_TRANSITION ; reste PLACED | | | échec attendu |
| CT-26 | Payer deux fois | BR-05 | PAID ; STAFF | payer | appliquer | INVALID_TRANSITION ; reste PAID | | | échec attendu |
| CT-27 | Livrer depuis PAID | BR-05 | PAID ; STAFF | livrer | appliquer | INVALID_TRANSITION ; reste PAID | | | échec attendu |
| CT-28 | Payer une commande expédiée | BR-05 | SHIPPED ; STAFF | payer | appliquer | INVALID_TRANSITION ; reste SHIPPED | | | échec attendu |
| CT-29 | Expédier deux fois | BR-05 | SHIPPED ; STAFF | expédier | appliquer | INVALID_TRANSITION ; reste SHIPPED | | | échec attendu |
| CT-30 | Annuler après expédition | BR-05, BR-06 | SHIPPED ; STAFF | annuler | appliquer | INVALID_TRANSITION ; reste SHIPPED | | | échec attendu |
| CT-31 | Payer une commande livrée | BR-05 | DELIVERED ; STAFF | payer | appliquer | INVALID_TRANSITION ; reste DELIVERED | | | échec attendu |
| CT-32 | Expédier une commande livrée | BR-05 | DELIVERED ; STAFF | expédier | appliquer | INVALID_TRANSITION ; reste DELIVERED | | | échec attendu |
| CT-33 | Livrer deux fois | BR-05 | DELIVERED ; STAFF | livrer | appliquer | INVALID_TRANSITION ; reste DELIVERED | | | échec attendu |
| CT-34 | Annuler une commande livrée | BR-05, BR-06 | DELIVERED ; STAFF | annuler | appliquer | INVALID_TRANSITION ; reste DELIVERED | | | échec attendu |
| CT-35 | Payer une commande annulée | BR-05 | CANCELLED ; STAFF | payer | appliquer | INVALID_TRANSITION ; reste CANCELLED | | | échec attendu |
| CT-36 | Expédier une commande annulée | BR-05 | CANCELLED ; STAFF | expédier | appliquer | INVALID_TRANSITION ; reste CANCELLED | | | échec attendu |
| CT-37 | Livrer une commande annulée | BR-05 | CANCELLED ; STAFF | livrer | appliquer | INVALID_TRANSITION ; reste CANCELLED | | | échec attendu |
| CT-38 | Annuler deux fois | BR-05 | CANCELLED ; STAFF | annuler | appliquer | INVALID_TRANSITION ; reste CANCELLED | | | échec attendu |
| CT-39 | Un client ne peut pas payer | BR-05 | commande PLACED d'Ana ; acteur Ana | payer | appliquer | refus de droit (403) ; reste PLACED | | | échec attendu |
| CT-40 | Un client annule sa commande PLACED | BR-05 | commande PLACED d'Ana ; acteur Ana | annuler | appliquer | statut CANCELLED | | | valide |
| CT-41 | Un client annule sa commande PAID | BR-05 | commande PAID d'Ana ; acteur Ana | annuler | appliquer | refus ; reste PAID — code 403 (décision Q-02) | | | échec attendu |
| CT-42 | L'annulation remet chaque ligne en stock | BR-06 | commande PLACED : 2 × P1, 1 × P2 ; stocks après commande 8 et 2 | annuler | appliquer, lire les mouvements de stock | +2 sur P1, +1 sur P2 (stocks 10 et 3) | | | valide |
| CT-43 | Pas de remise en stock après expédition | BR-06 | commande SHIPPED : 2 × P1 ; stock P1 = 8 | annuler | appliquer | INVALID_TRANSITION ; aucun mouvement de stock (P1 = 8) | | | échec attendu |
| CT-44 | Quantité égale au stock acceptée | BR-01 | P2 stock 3 | 1 ligne 3 × P2 | vérifier le stock | accepté ; stock restant 0 | | | valide |
| CT-45 | Quantité au-delà du stock refusée | BR-01 | P2 stock 3 | 1 ligne 4 × P2 | vérifier le stock | OUT_OF_STOCK (409) ; stock inchangé 3 | | | échec attendu |
| CT-46 | Une seule ligne en rupture bloque tout | BR-01 | P1 stock 10, P2 stock 3 | 2 × P1, 4 × P2 | vérifier le stock | OUT_OF_STOCK ; aucun stock modifié (10 et 3) | | | échec attendu |
| CT-47 | Le prix client est ignoré | BR-02 | catalogue : P1 = 40,00 € | ligne 1 × P1 avec prix client 0,01 € | construire les lignes | prix unitaire 40,00 € ; sous-total 40,00 € | | | valide |
| CT-48 | Seuil du stock faible | FR-09 | produits aux stocks 4 et 5 | liste des produits | calculer « stock faible » | produit au stock 4 listé, produit au stock 5 non listé | | | valide |
| CT-49 | Top 5 des produits vendus | FR-09 | 6 produits vendus en quantités 9, 8, 7, 6, 5, 4 (sans égalité) | lignes de commandes comptées (Q-03) | calculer le top 5 | les 5 premiers dans l'ordre 9, 8, 7, 6, 5 ; le 6e absent | | | valide |
| CT-50 | Statuts comptés dans le chiffre d'affaires | FR-09 | commandes : PLACED 50,00 ; PAID 114,00 ; SHIPPED 20,00 ; DELIVERED 30,00 ; CANCELLED 80,00 | commandes | calculer le chiffre d'affaires | 164,00 € (décision Q-03) | | | valide |
| CT-51 | Bornes contrôlées avant la fusion des doublons | BR-03 | aucune | 2 lignes du même produit, quantité 99 chacune | valider puis fusionner | accepté ; une seule ligne de quantité 198 (décision Q-01) | | | valide |
| CT-52 | Pas de remise, limite basse | BR-04 | aucune | sous-total 0,00 € | calculer la remise | remise 0,00 € ; total 0,00 € | | | valide |
| CT-53 | L'ADMIN a les mêmes droits que STAFF | BR-05 | commandes dans chaque état de départ ; acteur ADMIN | payer, expédier, livrer, annuler (PLACED, PAID) | appliquer les 5 transitions autorisées | les 5 transitions sont acceptées | | | valide |
| CT-54 | Un client ne peut pas expédier | BR-05 | commande PAID d'Ana ; acteur Ana | expédier | appliquer | refus de droit (403) ; reste PAID | | | échec attendu |
| CT-55 | Un client ne peut pas livrer | BR-05 | commande SHIPPED d'Ana ; acteur Ana | livrer | appliquer | refus de droit (403) ; reste SHIPPED | | | échec attendu |
| CT-56 | Un client n'annule pas une commande expédiée | BR-06 | commande SHIPPED d'Ana ; acteur Ana | annuler | appliquer | INVALID_TRANSITION (409, BR-06 : impossible après SHIPPED) ; aucun mouvement de stock | | | échec attendu |

## 2. Tests d'intégration (IT) — une réussite et une erreur par interface (conception.md §4)

Base PostgreSQL de test jetable, schéma reconstruit avant chaque test.

| ID | Objectif | Règle | Interface | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IT-01 | Un jeton valide identifie l'utilisateur et son rôle | FR-01 | I-1 API ↔ sécurité | Sam (STAFF) en base | jeton émis pour Sam | décoder le jeton, charger l'utilisateur | utilisateur Sam, rôle STAFF | | | valide |
| IT-02 | Un jeton expiré ou falsifié est refusé | FR-01 | I-1 | Sam en base | jeton expiré ; jeton signé avec une autre clé | décoder | refus d'authentification (401) dans les deux cas | | | échec attendu |
| IT-03 | La commande décrémente le stock en base | BR-01 | I-2 commandes ↔ catalogue | P1 stock 10 | 3 × P1 par Ana | créer la commande, relire le stock | stock P1 = 7 ; 1 commande, 1 ligne | | | valide |
| IT-04 | Une panne à la 2e écriture n'écrit rien | BR-01, QR-RE-02 | I-2 + I-7 base | P1 stock 10 ; bouchon qui échoue à l'écriture des lignes | 3 × P1 | créer la commande | erreur remontée à l'appelant ; 0 commande, stock P1 = 10 | | | échec attendu |
| IT-05 | Le prix vient du catalogue en base | BR-02 | I-3 commandes ↔ tarification | P1 = 40,00 € | 1 × P1 avec prix client 0,01 € ; puis prix catalogue changé à 45,00 € | créer, puis modifier le prix, relire la commande | ligne à 40,00 € avant et après le changement de prix | | | valide |
| IT-06 | Flux de données sous-total → remise → total → stock → lignes | BR-04 | I-3 + I-2 | P3 = 75,00 € stock 5 ; P4 = 50,00 € stock 5 | 2 × P3, 1 × P4 | créer la commande | sous-total 200,00 ; remise 20,00 ; total 180,00 ; stocks 3 et 4 ; 2 lignes aux prix 75,00 et 50,00 | | | valide |
| IT-07 | L'annulation remet le stock en base | BR-06, FR-08 | I-4 workflow ↔ stock | commande PLACED 2 × P1, 1 × P2 ; stocks 8 et 2 | annuler (Ana) | annuler, relire | CANCELLED ; stocks 10 et 3 | | | valide |
| IT-08 | Annulation refusée après expédition, base inchangée | BR-06 | I-4 | commande SHIPPED 2 × P1 ; stock 8 | annuler (Sam) | annuler, relire | INVALID_TRANSITION ; statut SHIPPED ; stock 8 | | | échec attendu |
| IT-09 | L'action et son audit sont écrits ensemble | FR-11 | I-5 services ↔ audit | Ana, P1 | création d'une commande | créer, lire le journal | 1 entrée « commande créée » : acteur Ana, cible = id de la commande, horodatage | | | valide |
| IT-10 | Action échouée = aucune entrée d'audit | FR-11 | I-5 | P2 stock 3 | 4 × P2 | créer (refusée), lire le journal | OUT_OF_STOCK ; aucune entrée « commande créée » | | | échec attendu |
| IT-11 | Indicateurs du tableau de bord sur un jeu maîtrisé | FR-09 | I-6 tableau de bord ↔ base | jeu de CT-50 + un produit au stock 4 | aucun filtre | calculer les indicateurs | par statut : PLACED 1, PAID 1, SHIPPED 1, DELIVERED 1, CANCELLED 1 ; stock faible contient le produit au stock 4 ; chiffre d'affaires 164,00 € et top 5 calculés sur les commandes PAID, SHIPPED, DELIVERED (décision Q-03) | | | valide |
| IT-12 | Filtres période et catégorie ; période invalide | FR-09 | I-6 | commandes datées du 01/11, du 15/11, du 20/11 23:59:59 et du 21/11 00:00:00 (UTC) ; deux catégories | période 10/11–20/11, catégorie A ; puis début > fin | appliquer les filtres | seules les commandes du 15/11 contenant la catégorie A sont comptées ; début > fin : 422 (décision Q-04) | | | valide |
| IT-13 | Filtres de recherche combinés | FR-10 | I-7 recherche ↔ base | jeu maîtrisé de 7 produits (noms, catégories, prix, stocks connus ; bornes de prix incluses) | q = « mug », catégorie Cuisine, prix 10,00–20,00, en stock | rechercher | exactement les produits du jeu qui respectent les 4 filtres ; total = leur nombre ; bornes de prix : Q-05 | | | valide |
| IT-14 | Paramètres de recherche invalides | FR-10 | I-7 | catalogue | taille de page 0 ; 101 ; prix min > max | rechercher | 422 pour les tailles 0 et 101 ; min > max : 422 (décision Q-05) | | | échec attendu |

## 3. Tests d'API (TA) — statut + corps + effet réel

| ID | Objectif | Règle | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TA-01 | Inscription d'un client | FR-01 | aucun compte | `POST /api/auth/register` ana@example.com, mot de passe 8 caractères | appeler, puis se connecter, puis `/me` | 201 ; corps : email en minuscules, rôle CUSTOMER ; connexion 200 avec jeton | | | valide |
| TA-02 | Mauvais mot de passe | FR-01, FR-11 | Ana inscrite | mot de passe erroné | `POST /api/auth/login`, lire le journal | 401 ; aucun jeton ; 1 entrée « connexion échouée » | | | échec attendu |
| TA-03 | Commande sans jeton (R1) | FR-01, FR-06 | P1 stock 10 | `POST /api/orders` sans en-tête Authorization | appeler, relire | 401 ; 0 commande ; stock 10 | | | échec attendu |
| TA-04 | Commande valide avec remise (R5) | FR-06, BR-04, BR-01 | Ana connectée ; P1 stock 10 | 3 × P1 | `POST /api/orders`, relire stock et commande | 201 ; corps : sous-total 120,00, remise 6,00, total 114,00, statut PLACED ; stock P1 = 7 ; `GET /api/orders/{id}` = mêmes valeurs | | | valide |
| TA-05 | Corps invalide (R2) | BR-03, FR-06 | Ana connectée ; P1 stock 10 | 1 ligne quantité 0 ; puis 51 lignes | appeler, relire | 422 avec le champ fautif ; 0 commande ; stock 10 | | | échec attendu |
| TA-06 | Stock insuffisant (R4) | BR-01, FR-06 | Ana ; P2 stock 3 | 4 × P2 | appeler, relire | 409, code OUT_OF_STOCK ; 0 commande ; stock 3 | | | échec attendu |
| TA-07 | Prix client ignoré | BR-02, FR-06 | Ana ; P1 = 40,00 € | 1 × P1 avec `unit_price` 0,01 | appeler | 201 ; ligne à 40,00 € ; total 40,00 € | | | valide |
| TA-08 | Cycle de vie d'une catégorie | FR-03, BR-09 | Sam connecté | catégorie « Test » | POST, GET, PUT (renommer), DELETE, GET | 201, 200, 200, 204, 404 | | | valide |
| TA-09 | Cycle de vie d'un produit | FR-04, BR-10 | Sam ; une catégorie | produit valide | POST, GET, PUT (prix 42,00), DELETE, GET | 201, 200, 200 (prix 42,00 relu), 204, 404 | | | valide |
| TA-10 | Email déjà pris, autre casse | BR-07 | ana@example.com inscrite | ANA@Example.com | `POST /api/auth/register` | 409 ; un seul compte en base | | | échec attendu |
| TA-11 | SKU déjà pris | BR-07 | P1 existe | nouveau produit SKU `P1-TEST` (casse : Q-06) | `POST /api/products` | 409 ; un seul produit `P1-TEST` | | | échec attendu |
| TA-12 | Nom de catégorie déjà pris | BR-07 | catégorie « Papeterie » | « Papeterie » (casse : Q-06) | `POST /api/categories` | 409 ; une seule catégorie | | | échec attendu |
| TA-13 | Deux commandes simultanées, dernières unités | BR-01, QR-RE-02 | P5 stock 2 ; Ana et Bob connectés | chacun 2 × P5, envoyés en même temps (barrière) | lancer en parallèle, relire | exactement un 201 et un 409 OUT_OF_STOCK ; stock final 0 ; 1 commande | | | échec attendu |
| TA-14 | Annulation par le client | FR-06, BR-06 | commande PLACED d'Ana 2 × P1 ; stock 8 | `POST /api/orders/{id}/cancel` | appeler, relire | 200 ; statut CANCELLED ; stock P1 = 10 | | | valide |
| TA-15 | Workflow par le personnel | FR-07, BR-05, FR-11 | commande PLACED ; Sam | statuts PAID puis SHIPPED | `PATCH /api/orders/{id}/status` ×2, relire | 200 et 200 ; statut final SHIPPED ; 2 entrées d'audit « statut changé » | | | valide |
| TA-16 | Transition interdite par l'API | FR-07, BR-05, BR-06 | commande SHIPPED ; Sam | statut CANCELLED | appeler, relire | 409 INVALID_TRANSITION ; statut SHIPPED | | | échec attendu |
| TA-17 | Tableau de bord : droits et filtres | FR-09 | jeu de IT-11 | Sam avec filtres valides ; Ana | `GET /api/dashboard` | Sam : 200 et indicateurs de IT-11 ; Ana : 403 | | | valide |
| TA-18 | Recherche filtrée sur 50 000 produits | FR-10 | jeu de volume (004) + jeu maîtrisé de IT-13 | filtres de IT-13 | `GET /api/products?...` | 200 ; chaque élément respecte les filtres ; `total` = nombre de correspondances (requête SQL de contrôle) ; taille de page respectée | | | valide |
| TA-19 | Paramètres de recherche invalides | FR-10 | catalogue | `limit=0`, `limit=101`, `min_price_cents=a` | appeler | 422 pour chacun ; jamais 500 | | | échec attendu |
| TA-20 | Matrice des droits complète | FR-02, QR-SE-02 | un utilisateur par rôle + anonyme | chaque rôle × chaque route de conception.md §5 | appeler chaque couple | code obtenu = code attendu de la matrice, pour 100 % des couples | | | valide |
| TA-21 | Changement de rôle par l'ADMIN | FR-05, FR-11, BR-11 | Alice ; Bob CUSTOMER | Bob → STAFF | `PATCH /api/users/{id}/role`, puis Bob appelle le tableau de bord ; puis Alice passe Zoé (2e ADMIN) en STAFF | 200 ; Bob a le rôle STAFF ; tableau de bord 200 ; 1 entrée d'audit « rôle changé » ; Zoé : 200 (SC-BR-11-1) | | | valide |
| TA-22 | Compte désactivé | FR-05 | Alice ; Bob actif avec un jeton | désactiver Bob | `PATCH /api/users/{id}/deactivate`, connexion de Bob, appel avec l'ancien jeton | 200 ; connexion 401 ; ancien jeton : 401 (décision Q-08) | | | échec attendu |
| TA-23 | Journal d'audit non modifiable | FR-11 | au moins une entrée | `PUT` et `DELETE` sur `/api/audit/{id}` | appeler, relire le journal | 405 pour les deux ; entrées inchangées | | | échec attendu |
| TA-24 | Lecture du journal d'audit | FR-11 | entrées existantes | Alice ; Sam | `GET /api/audit` | Alice : 200 avec les entrées ; Sam : 403 (décision Q-11) | | | valide |
| TA-25 | Un client ne lit pas la commande d'un autre | BR-08 | commande d'Ana ; Bob connecté | id de la commande d'Ana | `GET /api/orders/{id}` par Bob | 404 | | | échec attendu |
| TA-26 | Un client n'annule pas la commande d'un autre | BR-08 | commande PLACED d'Ana 2 × P1 ; stock 8 | id de la commande d'Ana | `POST /api/orders/{id}/cancel` par Bob, relire | 404 ; statut PLACED ; stock 8 | | | échec attendu |
| TA-27 | Suppression d'une catégorie non vide | BR-09 | « Papeterie » contient P1 | — | `DELETE /api/categories/{id}`, relire | 409 ; catégorie et P1 toujours présents | | | échec attendu |
| TA-28 | Contrat OpenAPI et robustesse | QR-CO-02 | API démarrée | `/openapi.json` | Schemathesis, toutes vérifications | 0 violation du contrat ; 0 réponse 500 | | | valide |
| TA-30 | Suppression d'un produit déjà commandé | BR-10 | P1 présent dans une commande d'Ana ; Sam connecté | id de P1 | `DELETE /api/products/{id}`, relire | 409, code PRODUCT_IN_USE ; P1 toujours présent ; la commande d'Ana inchangée | | | échec attendu |
| TA-31 | Le dernier ADMIN ne peut pas disparaître | BR-11 | Alice seule ADMIN active | Alice → CUSTOMER ; puis désactivation d'Alice | `PATCH /api/users/{id}/role`, `PATCH /api/users/{id}/deactivate`, relire | 409 LAST_ADMIN pour les deux ; Alice reste ADMIN et active | | | échec attendu |
| TA-29 | Produit inexistant (R3) | FR-06 | Ana connectée | 1 × produit id 999999 | appeler, relire | 404 ; 0 commande ; aucun stock modifié | | | échec attendu |
| TA-32 | Nombre hors plage : refus précis, jamais 500 | QR-CO-02 | API démarrée | id de chemin 2^63 et 2^53 ; `category_id` et `offset` 2^63 ; `product_id` 2^63 dans une commande | appeler | 422 pour chacun (ANO-01) | | | échec attendu |
| TA-33 | Caractère NUL : refus précis, jamais 500 | QR-CO-02, FR-01 | API démarrée | `a\x00b` dans l'email de connexion, l'email d'inscription, un nom de catégorie | appeler | 422 pour chacun (ANO-02) | | | échec attendu |
| TA-34 | Types JSON respectés | QR-CO-02, FR-04, FR-09 | Alice (ADMIN) | stock `false`, `"5"`, `5.0` ; `date_to=0`, `date_to=20261120` | créer un produit ; lire le tableau de bord | `false` et `"5"` : 422 ; `5.0` : 201, stock 5 ; dates non ISO : 422, date ISO : 200 (ANO-03) | | | échec attendu |
| TA-35 | En-tête `Allow` complet sur 405 | QR-CO-02 | API démarrée | `PATCH` sur `/api/categories`, `/api/products/1`, `/api/audit/1` | appeler | 405 ; `Allow` = GET, POST / DELETE, GET, PUT / GET (ANO-04) | | | échec attendu |
| TA-36 | Un client n'annule ni une commande PAID ni une commande SHIPPED | BR-05, BR-06 | commande d'Ana 2 × P1 au statut PAID, puis SHIPPED ; stock 8 | — | `POST /api/orders/{id}/cancel` par Ana, relire | PAID : 403 FORBIDDEN (décision Q-02) ; SHIPPED : 409 INVALID_TRANSITION ; statut et stock (8) inchangés | | | échec attendu |
| TA-37 | Annulation et modifications de produit journalisées | FR-11 | Ana, Sam (STAFF), une commande PLACED d'Ana | annulation par Ana ; création, modification, suppression d'un produit par Sam | appeler, lire le journal | entrées ORDER_CANCELLED (Ana), PRODUCT_CREATED, PRODUCT_UPDATED, PRODUCT_DELETED (Sam) avec la bonne cible | | | valide |
| TA-38 | Liste des commandes paginée et filtrée | FR-07 | 7 commandes d'Ana ; Sam connecté | `limit=3`, `offset=3`, `status=PAID`, `limit=201` | appeler `GET /api/orders` | pages de 3 dans l'ordre antichronologique, sans recouvrement ; filtre PAID : la seule commande payée ; `limit=201` → 422 (ANO-09) | | | valide |

## 4. Tests de bout en bout (E2E) — Chromium, Firefox, mobile (Pixel 7)

| ID | Objectif | Règle | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E2E-01 | Parcours client complet | FR-01, FR-06, FR-10 | pile démarrée ; Ana inscrite ; P1 stock 10 | recherche « P1 » | chercher → fiche produit → panier (3) → connexion → commander → mes commandes | commande visible, statut PLACED, total 114,00 € (remise 6,00 €) | | | valide |
| E2E-02 | Refus pour rupture de stock | BR-01 | Ana connectée ; P2 stock 3 | 4 × P2 au panier | commander | message d'erreur clair « stock insuffisant » ; aucune commande ajoutée | | | échec attendu |
| E2E-03 | Le personnel fait avancer une commande | FR-07, BR-05 | commande PLACED ; Sam connecté | — | back-office → PAID → SHIPPED | statut SHIPPED affiché ; seuls les boutons des transitions autorisées sont visibles à chaque étape | | | valide |
| E2E-04 | Créer puis supprimer un produit avec confirmation | FR-04, QR-US-02 | Alice connectée | produit valide ; puis un prix invalide | créer (erreur de champ affichée sur le prix invalide) → supprimer → annuler la boîte → supprimer → confirmer | message sous le champ fautif ; le produit reste après « annuler » ; il disparaît après « confirmer » | | | valide |
| E2E-05 | Filtres du tableau de bord | FR-09 | jeu de IT-11 ; Sam connecté | période et catégorie | appliquer les filtres | indicateurs affichés identiques à ceux de l'API pour les mêmes filtres | | | valide |

## 5. Sécurité (SEC) — fiche 4

| ID | Objectif | Règle | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-01 | Injection SQL dans la recherche | QR-SE-02, FR-10 | catalogue | `q = ' OR 1=1 --` et `q = '; DROP TABLE products; --` | rechercher, recompter les produits | traité comme du texte : 200, 0 résultat inattendu ; table intacte ; jamais 500 | | | échec attendu |
| SEC-02 | XSS stocké dans un nom de produit | QR-SE-02 | Sam connecté | nom `<script>window.__xss=1</script>` | créer, afficher la liste et la fiche dans le navigateur | le texte s'affiche tel quel ; `window.__xss` reste indéfini | | | échec attendu |
| SEC-03 | Contrôle d'accès par numéro de commande | QR-SE-02, BR-08, FR-02 | commandes d'Ana ; Bob connecté | ids de commandes d'Ana | lire et annuler via l'API | 404 ; rien ne change | | | échec attendu |
| SEC-04 | Session : jeton expiré, jeton émis avant un changement de rôle | QR-SE-02, FR-01 | Bob STAFF avec un jeton ; puis rétrogradé CUSTOMER | jeton expiré ; ancien jeton après rétrogradation | appeler une route STAFF | expiré : 401 ; ancien jeton : le rôle courant en base s'applique, 403 | | | échec attendu |
| SEC-05 | SAST et secrets | QR-SE-01 | dépôt complet | code + historique Git | Semgrep, Bandit, gitleaks ; tri ; correction ; relance | 0 High ; 0 Medium non justifiée ; chaque alerte triée dans `securite/triage.md` | | | valide |
| SEC-06 | SCA, SBOM et licences | QR-SE-01 | dépendances installées | requirements, package-lock, images | pip-audit, npm audit, Trivy, Syft, licences ; décision par CVE ; relance | 0 High ; 0 Medium non justifiée ; dépendances indirectes incluses ; SBOM produit | | | valide |
| SEC-07 | DAST passif puis actif | QR-SE-01 | autorisation signée ; pile locale | `http://localhost` | ZAP baseline puis scan API actif ; tri ; correction ; relance | 0 High ; 0 Medium non justifiée ; Low justifiées | | | valide |

## 6. Performance (PERF), fiabilité (REL), utilisabilité (UX), maintenabilité (MA), portabilité (PORT)

| ID | Objectif | Règle | Préconditions | Données d'entrée | Étapes | Résultat attendu | Obtenu | Verdict | Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PERF-01 | Smoke de performance | QR-PE-01 | pile en conteneurs | 1 utilisateur, 30 s | k6 smoke.js | 0 erreur ; seuils vérifiés | | | valide |
| PERF-02 | Charge sur liste et détail | QR-PE-01 | pile ; 50 000 produits | 20 utilisateurs, 5 min | k6 load.js + docker stats | p95 < 500 ms ; erreurs < 1 % | | | valide |
| PERF-03 | Recherche filtrée sur 50 000 produits | QR-PE-02, FR-10 | pile ; 50 000 produits | filtres variés | k6 search.js | p95 < 800 ms ; erreurs < 1 % | | | valide |
| REL-01 | Redémarrage de la base sous charge | QR-RE-01 | pile ; charge k6 2 min | redémarrage de PostgreSQL | redémarrer, sonder /api/health, requêtes SQL de cohérence | 503 pendant la panne ; reprise < 60 s ; 0 réponse 500 hors fenêtre ; 0 commande incohérente | | | valide |
| REL-02 | Arrêt brutal du conteneur API | QR-RE-01 | pile | kill du conteneur api | tuer, mesurer le retour | redémarrage automatique (politique restart) ; temps mesuré et rapporté | | | valide |
| REL-03 | Panne entre deux écritures | QR-RE-02 | P1 stock 10 ; panne injectée | 3 × P1 | créer la commande | tout est annulé : 0 commande, stock 10 | | | échec attendu |
| REL-04 | Double soumission simultanée | QR-RE-02, BR-01 | P5 stock 2 | même commande 2 × P5 envoyée deux fois en même temps | lancer, relire | une seule commande ; stock 0 ; jamais de stock négatif | | | échec attendu |
| UX-01 | Accessibilité de base | QR-US-01 | pile | 5 pages : catalogue, fiche produit, panier, back-office commandes, gestion produits | axe-core via Playwright | 0 violation serious ou critical | | | valide |
| UX-02 | Réussite et temps des tâches | QR-US-02 | protocole `utilisabilite.md` ; 3 à 5 participants | 3 tâches | sessions observées, calcul par script | réussite >= 80 % ; temps médian rapporté (Q-12) | | | valide |
| UX-03 | Satisfaction (SUS) | QR-US-02 | mêmes sessions | questionnaire SUS de 10 items | calcul par script | SUS moyen >= 68 (Q-12) | | | valide |
| MA-01 | Couverture des services | QR-MA-01 | tests unitaires | app/services | pytest-cov | >= 80 % en instructions et en branches | | | valide |
| MA-02 | Qualité des tests : mutation et propriété | QR-MA-01, BR-04 | tests unitaires | services tarification et commandes | mutmut (conteneur, 15 min) ; Hypothesis : remise >= 0, remise <= sous-total, remise croissante avec le sous-total | score rapporté, survivants listés ; propriété vraie sur toutes les entrées générées | | | valide |
| MA-03 | Complexité cyclomatique | QR-MA-02 | backend/app | — | radon cc, xenon --max-absolute B | aucune fonction > 10 | | | valide |
| MA-04 | Dépendances entre couches | QR-MA-02 | backend/app | contrat api → services → models | import-linter ; ruff | 0 violation ; ruff sans erreur | | | valide |
| PORT-01 | Installation propre chronométrée | QR-PO-01 | Docker seul | dépôt cloné dans un dossier temporaire | `scripts/installation-propre.sh` | pile saine ; smoke OK ; durée < 10 min (journal) | | | valide |
| PORT-02 | Installation sur une seconde machine | QR-PO-01 | poste d'un coéquipier | `docs/installation.md` | suivre le guide | smoke OK ; durée < 10 min ; journal remis | | | valide |

## 7. Synthèse

| Niveau | Préfixe | Nombre de cas | Valides | Échec attendu |
| --- | --- | --- | --- | --- |
| Unitaire | CT | 56 | 27 | 29 |
| Intégration | IT | 14 | 9 | 5 |
| API | TA | 38 | 15 | 23 |
| E2E | E2E | 5 | 4 | 1 |
| Sécurité | SEC | 7 | 3 | 4 |
| Performance | PERF | 3 | 3 | 0 |
| Fiabilité | REL | 4 | 2 | 2 |
| Utilisabilité | UX | 3 | 3 | 0 |
| Maintenabilité | MA | 4 | 4 | 0 |
| Portabilité | PORT | 2 | 2 | 0 |
| **Total** | | **136** | | |

Cas dont l'attendu dépend d'une décision Q-xx du 19/11/2026 : CT-41, CT-50, IT-11, IT-12, IT-13, IT-14, TA-11,
TA-12, TA-22, TA-24, TA-30, TA-31. Comptages produits par `tools/check_docs.py`, pas à la main.
