# Journal des anomalies

Chaque anomalie suit la méthode de la fiche 1 : constat → cause (erreur → défaut → défaillance) → correction →
**test de confirmation** (le test qui avait échoué, rejoué) → **non-régression** (`make check` complet).
Les résultats cités proviennent des sorties réelles des outils (fichiers dans `reports/`).

## Synthèse

| ID | Date | Exigence | Détectée par | Gravité | Statut |
| --- | --- | --- | --- | --- | --- |
| ANO-01 | 19/11/2026 | QR-CO-02 | TA-28 (Schemathesis) | majeure | Corrigée |
| ANO-02 | 19/11/2026 | QR-CO-02, FR-01 | TA-28 (Schemathesis) | majeure | Corrigée |
| ANO-03 | 19/11/2026 | QR-CO-02, FR-04, FR-09 | TA-28 (Schemathesis, ST201) | mineure | Corrigée |
| ANO-04 | 19/11/2026 | QR-CO-02 | TA-28 (Schemathesis, ST205) | mineure | Corrigée |
| ANO-05 | 19/11/2026 | QR-CO-02 | TA-28 (Schemathesis, ST103, ST108) | mineure | Corrigée |
| ANO-06 | 19/11/2026 | QR-CO-02 | TA-28 (Schemathesis, ST202) | — | Faux positif justifié |
| DT-01 | 19/11/2026 | BR-01, QR-RE-02 | `tools/break_rules.py --suite api` | majeure (défaut de test) | Corrigée |

## ANO-01 — Identifiant hors plage : erreur 500

- **Exigence** : QR-CO-02 (jamais de 500 sur une entrée invalide, fiche 2 robustesse).
- **Test** : TA-28 ; test de non-régression dédié ajouté : TA-32.
- **Étapes** : `GET /api/products/9223372036854775808` (ou tout `{id}` > 2^31 − 1 sur une route d'identifiant).
- **Attendu** : refus précis (422 ou 404). **Obtenu** : 500 `NumericValueOutOfRange: integer out of range`.
- **Erreur (humaine)** : supposer que le type Python `int` correspondait au type des colonnes.
- **Défaut** : `Mapped[int]` est lié en INTEGER (int4) par SQLAlchemy alors que les identifiants sont BIGINT
  (`app/core/db.py`) ; aucune borne sur les identifiants dans l'API.
- **Défaillance** : un client qui envoie un grand nombre reçoit une erreur serveur.
- **Correction** : `type_annotation_map = {int: BigInteger}` ; identifiants bornés à 2^53 − 1 (entier exact en
  JavaScript et en JSON) ; montants et stocks bornés à INTEGER ; `offset` borné (`app/api/types.py`).
- **Confirmation** : TA-28 rejoué → 25 opérations sur 25 sans échec (`reports/junit-contract.xml`) ; TA-32 → PASS.
- **Non-régression** : `make check` → 56 unitaires, 17 intégration, 165 API, 25 contrat passés ; couverture
  `app/services` 99,4 %.

## ANO-02 — Caractère NUL dans un texte : erreur 500

- **Exigence** : QR-CO-02, FR-01. **Test** : TA-28 ; non-régression : TA-33.
- **Étapes** : `POST /api/auth/login` avec `username=%00`.
- **Attendu** : refus précis. **Obtenu** : 500 `PostgreSQL text fields cannot contain NUL (0x00) bytes`.
- **Erreur** : ignorer que PostgreSQL refuse le caractère NUL dans un texte.
- **Défaut** : aucune validation du caractère NUL (formulaire de connexion, email, noms, SKU, description, `q`).
- **Défaillance** : erreur serveur, et la tentative de connexion n'est pas journalisée.
- **Correction** : motif `NO_NUL` sur tous les textes ; 422 `NUL_CHARACTER` à la connexion.
- **Confirmation** : TA-28 → PASS ; TA-33 → PASS. **Non-régression** : `make check` vert (voir ANO-01).

## ANO-03 — Types JSON non respectés (booléen accepté comme entier, date numérique)

- **Exigence** : QR-CO-02, FR-04, FR-09. **Test** : TA-28 (ST201) ; non-régression : TA-34.
- **Étapes** : `POST /api/products` avec `"stock": false` ; `GET /api/dashboard?date_to=0`.
- **Attendu** : 422 (le contrat exige un entier, une date ISO). **Obtenu** : 201 avec stock 0 ; 200 avec la date
  1970-01-01.
- **Erreur / défaut** : conversion permissive par défaut de Pydantic (`false` → 0, `0` → date Unix).
- **Défaillance** : des données erronées entrent silencieusement dans le catalogue.
- **Correction** : entiers au sens de JSON Schema (`5.0` accepté, `false` et `"5"` refusés) ; dates au format
  `AAAA-MM-JJ` uniquement ; bornes publiées dans le contrat en `minimum`/`maximum`.
- **Confirmation** : TA-28 → PASS ; TA-34 → PASS. **Non-régression** : `make check` vert.

## ANO-04 — En-tête `Allow` incomplet sur une réponse 405

- **Exigence** : QR-CO-02 (RFC 9110 : un 405 liste les méthodes acceptées). **Test** : TA-28 (ST205) ; TA-35.
- **Étapes** : `OPTIONS /api/categories`. **Attendu** : `Allow: GET, POST`. **Obtenu** : `Allow: GET`.
- **Défaut** : la 405 de Starlette ne cite que la première route trouvée ; une première correction lisait
  `app.routes`, qui ne contient pas les routeurs inclus (en-tête vide, détecté par TA-35).
- **Correction** : table des routes construite depuis le contrat OpenAPI (`app/api/route_table.py`).
- **Confirmation** : TA-35 → PASS (3 chemins) ; TA-28 → PASS. **Non-régression** : `make check` vert.

## ANO-05 — Codes 400 non documentés dans le contrat

- **Exigence** : QR-CO-02. **Test** : TA-28 (ST103 code non documenté, ST108 schéma de réponse).
- **Étapes** : corps JSON illisible sur une route qui attend un corps. **Obtenu** : 400 absent du contrat ; le 400
  et le 401 renvoient `detail` sous forme de texte, non conforme au modèle d'erreur déclaré.
- **Correction** : 400 documenté sur toutes les routes à corps ; modèle `MessageErrorBody` pour 400 et 401.
- **Confirmation** : TA-28 → PASS. **Non-régression** : `make check` vert.

## ANO-06 — Constat non retenu : règles inter-champs (faux positif justifié)

- **Constat** : Schemathesis (ST202) juge « valide » `min_price_cents=2147483646&max_price_cents=0`, refusé par l'API.
- **Analyse** : le refus applique la décision Q-05 (min > max → 422) ; de même Q-04 pour `date_from > date_to`.
  JSON Schema ne sait pas exprimer une contrainte entre deux paramètres : l'outil ne peut pas la connaître.
- **Décision** : vérification `positive_data_acceptance` désactivée pour ces deux seules opérations
  (`GET /api/products`, `GET /api/dashboard`) ; toutes les autres vérifications restent actives sur elles. La règle
  est couverte par IT-12 (période, y compris le 422 HTTP) et IT-14 (prix min > max).

## DT-01 — Défaut de test : TA-13 ne pouvait pas échouer

- **Détecté par** : `tools/break_rules.py --suite api` ; avec le verrou `FOR UPDATE` retiré, les 182 tests
  passaient encore (`reports/api/regles-cassees.txt`, première exécution).
- **Cause** : les deux requêtes « simultanées » de TA-13 ne se chevauchaient pas réellement dans le client de test ;
  le test ne mettait pas la règle à l'épreuve (fiche 2 : un test qui ne peut pas échouer ne prouve rien).
- **Correction** : course forcée de façon déterministe (barrière entre la lecture et l'écriture du stock, un client
  par fil d'exécution).
- **Confirmation** : verrou retiré → TA-13 échoue ; verrou présent → TA-13 passe (`reports/api/regles-cassees.txt`,
  7 mutations sur 7 détectées). **Non-régression** : `make check` vert.

Commit des corrections : commit « phase 3 » (voir `git log`).
