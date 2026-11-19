# Soutenance — script de démonstration (12 minutes)

Cahier §8 : démonstration live de l'application et d'au moins deux couches de test en exécution. Ce script en montre
trois (E2E Playwright, performance k6, contrat ou sécurité) et suit une exigence jusqu'à son rapport brut.

## Préparation (avant d'entrer dans la salle, 5 min)

```bash
docker compose up -d --build --wait          # pile complète, base de démonstration
./scripts/smoke.sh                           # BASE=http://127.0.0.1:8080/api : vérifie la chaîne complète
```

Ouvrir à l'avance : l'application (http://localhost:8080), `docs/tracabilite/matrice.md`, `docs/conformite.md`,
`docs/anomalies.md`, un terminal dans le dépôt. Fermer les autres programmes (mesures de performance).

## Déroulé

| Temps | Séquence | Ce qu'on montre | Commande / action | Message à faire passer |
| --- | --- | --- | --- | --- |
| 0:00–1:00 | Contexte | Domaine, pile, 8 caractéristiques | `README.md` | « Chaque affirmation du rapport renvoie à un fichier produit par un outil. » |
| 1:00–3:30 | Parcours métier avec changement de rôle | Client : recherche « mug », fiche, panier de 3 × 40 €, remise 5 %, commande. Personnel : la même commande passe à Payée puis Expédiée ; seules les transitions permises apparaissent. Tableau de bord filtré. | Navigateur : `demo@example.com / demo1234`, puis `staff@example.com / staff1234` | BR-04 (remise), BR-05 (workflow), FR-09 ; l'interface masque, l'API refuse (403/409) |
| 3:30–4:30 | Protection contre les erreurs | Suppression d'un produit : boîte de confirmation ; message d'erreur sous le champ prix | Back-office Produits | Utilisabilité (Chapitre I) ; ANO-07 corrigée sur téléphone |
| 4:30–6:30 | **Couche E2E en direct** | Playwright sur chromium et firefox, en mode visible | `cd web && npx playwright test --project=chromium --project=firefox --headed -g "E2E-0[13]"` (sous Windows, Firefox : `./scripts/e2e-docker.sh firefox`, voir ENV-02) | QR-CO-01 : deux navigateurs, mêmes parcours |
| 6:30–8:00 | **Couche performance en direct** | k6, 1 minute, seuils p95 affichés en vert | `backend/.venv/Scripts/python tools/perf_run.py load --env DURATION=1m` | QR-PE-01 : p95 < 500 ms à 20 utilisateurs ; résultat écrit par k6 dans `reports/perf/load.json` |
| 8:00–9:30 | Une ligne de la matrice jusqu'à sa preuve | BR-04 → CT-17 (arrondi 5,005 → 5,01 €) → `test_pricing.py::test_discount[CT-17]` → `reports/junit-unit.xml` → commit | `docs/tracabilite/matrice.md`, puis ouvrir le XML et chercher `CT-17` | Chaîne exigence → cas → script → verdict → preuve (fiche 1) |
| 9:30–10:30 | Sécurité | Tri ZAP : une alerte High « SQL Injection » prouvée faux positif par un test ; images Docker de 3 Critical + 118 High à 0 | `docs/securite/triage.md` (Z4), `reports/securite-synthese.md` | Fiche 4 : trier, corriger, relancer, justifier par écrit |
| 10:30–11:30 | Un écart expliqué | ENV-01 : blocages en parallèle sous Windows, cause isolée par mesures, résolue dans le réseau Docker | `docs/anomalies.md` (ENV-01) | « Un écart honnête vaut mieux qu'un succès non prouvé. » |
| 11:30–12:00 | Conclusion | Matrice : verdicts par exigence ; limites | `docs/conformite.md` § Écarts | Ce qui est prouvé, ce qui ne l'est pas encore |

## Plan B (si quelque chose casse en direct)

| Problème | Repli |
| --- | --- |
| La pile ne démarre pas | Montrer `reports/portabilite/installation-*.log` (installation propre chronométrée) et `docker compose ps` |
| Playwright échoue en direct | Montrer `reports/junit-e2e-docker.xml` et la trace HTML du dernier passage |
| k6 lent (machine chargée) | Montrer `reports/perf/load.json` (mesure de référence) et `reports/perf/environnement.txt` |
| Pas de réseau | Tout est local : aucune dépendance réseau pendant la démonstration |

## Questions probables

- *Pourquoi croire vos chiffres ?* — Ils sont dans des fichiers écrits par les outils ; un sous-agent indépendant a
  vérifié chaque nombre du rapport de conformité contre son fichier (phase 10).
- *Vos tests peuvent-ils échouer ?* — `tools/break_rules.py` casse 18 règles exprès : chacune fait échouer au moins un
  cas nommé (`reports/unit/regles-cassees.txt`, `reports/api/regles-cassees.txt`).
- *Pourquoi l'IA ?* — Section « Utilisation de Claude Code » de `docs/conception.md` : règles imposées, garde-fous,
  revues indépendantes, décisions laissées au groupe.
