# Rapport de test — Gestion commerciale (clôture de campagne)

Version 1.0 du 20/11/2026, activité « Clôturer » de la fiche 1. Plan : [`plan-de-test.md`](plan-de-test.md).
Cas : [`cahier-de-test.md`](cahier-de-test.md) (136 cas). Défauts : [`anomalies.md`](anomalies.md).
Conformité par caractéristique : [`conformite.md`](conformite.md). Matrice : [`tracabilite/matrice.md`](tracabilite/matrice.md).
Toutes les valeurs ci-dessous viennent des rapports bruts gelés dans [`preuves/v1.0/`](preuves/v1.0/) (commit de
gel et versions des outils dans `preuves/v1.0/manifest.json` et `preuves/v1.0/versions/` ; commit de chaque mesure :
[`conformite.md`](conformite.md), en-tête).

## 1. Périmètre testé

- **Testé** : les 11 fonctions FR-01 à FR-11, les 11 règles BR-01 à BR-11 (dont BR-10 et BR-11 issues des
  décisions Q-01 à Q-12), les 14 exigences de qualité QR des 8 caractéristiques ISO/IEC 25010:2011 ; API REST,
  interface React (bureau et téléphone), base PostgreSQL, pile Docker Compose.
- **Hors périmètre** (plan §1) : HTTPS et déploiement en production, charge au-delà de 20 utilisateurs, endurance,
  WebKit/Safari, test d'intrusion par un expert, lecteur d'écran.

## 2. Cas exécutés par niveau

| Niveau | Identifiants | Tests exécutés | Réussis | Échecs | Ignorés | Rapport |
| --- | --- | --- | --- | --- | --- | --- |
| Unitaire | CT-01 à CT-56, MA-02 | 59 | 59 | 0 | 0 | [`junit-unit.xml`](preuves/v1.0/junit-unit.xml) |
| Intégration | IT-01 à IT-14 | 17 | 17 | 0 | 0 | [`junit-integration.xml`](preuves/v1.0/junit-integration.xml) |
| API | TA-01 à TA-38 (dont matrice des droits) | 169 | 169 | 0 | 0 | [`junit-api.xml`](preuves/v1.0/junit-api.xml) |
| Contrat | TA-28 (Schemathesis) | 25 | 25 | 0 | 0 | [`junit-contract.xml`](preuves/v1.0/junit-contract.xml) |
| Sécurité | SEC-01, SEC-03, SEC-04 | 8 | 8 | 0 | 0 | [`junit-security.xml`](preuves/v1.0/junit-security.xml) |
| Fiabilité (pytest) | REL-03, REL-04, contrat 503 | 3 | 3 | 0 | 0 | [`junit-reliability.xml`](preuves/v1.0/junit-reliability.xml) |
| E2E dans Docker (chromium, firefox, mobile) | E2E-01 à E2E-05, SEC-02, UX-01 | 24 | 20 | 0 | 4 | [`junit-e2e-docker.xml`](preuves/v1.0/junit-e2e-docker.xml) |
| E2E sur le poste (chromium, mobile) | idem | 16 | 14 | 0 | 2 | [`junit-e2e.xml`](preuves/v1.0/junit-e2e.xml) |

Les tests ignorés sont les audits d'accessibilité limités volontairement au projet chromium (un audit par page
suffit) ; aucun test n'a été désactivé pour faire passer la campagne.

Mesures hors pytest/Playwright : PERF-01 à PERF-03 (k6), REL-01 et REL-02 (sonde sous panne), SAST/SCA/DAST,
mutation, complexité, couches, installation propre — résultats au [§4](#4-critères-de-sortie).

Non exécutés : **UX-02** et **UX-03** (séances avec participants le 20/11/2026, décision du groupe) et **PORT-02**
(installation sur une seconde machine par un coéquipier). Ils restent « en attente » dans le cahier et la matrice.

## 3. Défauts trouvés et corrigés

| Type | Nombre | Identifiants | État |
| --- | --- | --- | --- |
| Défauts du produit, gravité majeure | 5 | ANO-01, ANO-02, ANO-07, ANO-09, ANO-10 | tous corrigés, test de confirmation et non-régression réussis |
| Défauts du produit, gravité mineure | 4 | ANO-03, ANO-04, ANO-05, ANO-08 | tous corrigés |
| Constat non retenu | 1 | ANO-06 (règles inter-champs signalées par Schemathesis) | faux positif justifié |
| Défauts de test | 2 | DT-01 (TA-13 ne pouvait pas échouer), DT-02 (base supposée vide) | corrigés |
| Constats d'environnement | 2 | ENV-01 (redirection de port de Docker Desktop), ENV-02 (Firefox sous Windows) | contournés : exécution dans le réseau Compose et en conteneur |

Origine des défauts du produit : Schemathesis en a trouvé 5 (ANO-01 à ANO-05 : erreurs 500 sur identifiant hors
plage et caractère NUL, types JSON, en-tête `Allow`, codes non documentés) ; le projet E2E mobile 2 (ANO-07, ANO-10) ;
la base chargée par les essais de fiabilité 1 (ANO-09, liste des commandes non paginée) ; radon 1 (ANO-08,
complexité 11). Défauts de sécurité corrigés pendant le tri (registre [`securite/triage.md`](securite/triage.md)) :
images Docker (3 Critical et 118 High → 0), en-têtes HTTP manquants (5 alertes Low ZAP → 0), 19 constats Semgrep
(17 actions CI non épinglées, parseur XML, en-tête `Host`). Après relance : 3 ERROR Semgrep justifiées (S20 à S22,
outils locaux) ; gitleaks : 4 jetons de test expirés dans les résumés k6 (G3, corrigé pour les prochaines mesures,
résidu — ces 4 jetons dans `perf/smoke.json` et `perf/load.json` des preuves et dans l'historique Git local — accepté par le groupe le 20/11/2026).

Aucune anomalie bloquante ou majeure n'est ouverte.

## 4. Critères de sortie

| # | Critère (plan §4) | Mesuré | Verdict |
| --- | --- | --- | --- |
| 1 | 100 % des FR et BR P0 au PASS | 19/19 au PASS (matrice) | atteint |
| 2 | Chaque cible QR atteinte ou écart documenté | 12/14 QR au PASS ; QR-US-02 et QR-PO-01 au PARTIAL, écarts documentés dans [`conformite.md` § 11](conformite.md#11-écarts) | atteint (avec écarts documentés) |
| 3 | Sécurité : 0 High, 0 Medium non justifiée, Low justifiées, après relance | 0 High non traitée : ZAP 40018 faux positif prouvé par test SEC-01-zap-40018, 3 ERROR Semgrep (S20 à S22) faux positifs justifiés ; 0 Medium, 0 Low ; 0 vulnérabilité de dépendance ou d'image ([`securite-synthese.md`](preuves/v1.0/securite-synthese.md)) | atteint |
| 4 | Aucune anomalie bloquante ou majeure ouverte | 0 ouverte | atteint |
| 5 | Chaque nombre figure dans un fichier brut de `preuves/v1.0/` | preuves gelées avec empreintes SHA-256 ; vérification indépendante par le sous-agent `evidence-auditor` en deux passes, constats et corrections consignés dans [`journal.md`](journal.md) (phase 10 ; revue de code, pas un résultat d'outil) | atteint |

Indicateurs principaux : couverture `app/services` 99,4 % (388/391 instructions, 96/96 branches) ; mutation 96 %
(128/133, 5 survivants justifiés) ; complexité maximale 9 ; p95 77,39 ms (liste), 49,41 ms (détail), 64,32 ms
(recherche), 0 % d'erreurs ; reprise après panne 3,15 s et 3,27 s, 0 commande perdue ; axe-core 0 violation ;
installation propre 29 s ; couverture de l'API 25/25 opérations, 74/119 codes de réponse documentés exercés
([`api-coverage.md`](preuves/v1.0/api-coverage.md)).

**Décision de clôture** : la campagne peut être clôturée pour la version 1.0 avec deux réserves — la recette
utilisateur (QR-US-02) et l'installation sur une seconde machine (QR-PO-01) — qui seront ajoutées aux preuves dès
leur exécution, sans modifier les autres résultats.

## 5. Leçons apprises

1. **Le test de contrat paie tôt.** Schemathesis a trouvé à lui seul la moitié des défauts du produit, dont les deux
   erreurs 500 ; à lancer dès que l'API existe, pas en fin de campagne.
2. **Un test qui ne peut pas échouer ne prouve rien.** DT-01 n'a été vu qu'en cassant la règle volontairement
   (`tools/break_rules.py`) ; la mutation (102/133 au premier passage, noté dans [`journal.md`](journal.md) — rapport brut non conservé — puis 128/133) a ensuite montré des assertions trop vagues. Casser la règle
   fait désormais partie de l'écriture de chaque test.
3. **Les données réalistes révèlent d'autres défauts.** ANO-09 et DT-02 n'apparaissaient pas sur une base presque
   vide ; les E2E sont rejoués sur la base volumineuse (50 000 produits, plusieurs milliers de commandes).
4. **Le téléphone est un navigateur à part entière.** ANO-07 et ANO-10 ne se voyaient qu'avec le projet mobile.
5. **Séparer l'environnement du produit.** ENV-01 et ENV-02 ont été isolés et documentés au lieu d'être pris pour
   des défauts ; les mesures sont faites dans le réseau Compose pour ne pas mesurer Docker Desktop.
6. **Geler les preuves « avant » dès le premier scan.** Les relances avaient écrasé les rapports initiaux ; ils ont dû
   être régénérés depuis le commit `80e8c79`.
7. **Prévoir les personnes dans le calendrier.** Les deux réserves de clôture dépendent de participants et d'un
   coéquipier, pas de l'outillage.
