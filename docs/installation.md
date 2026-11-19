# Guide d'installation et d'exécution

Pour une personne qui découvre le projet. Exigence : **QR-PO-01** (installation reproductible, < 10 min).

## 1. Prérequis

| Outil | Version testée | Pour quoi |
| --- | --- | --- |
| Docker Desktop (Windows, macOS) ou Docker Engine + Compose v2 (Linux) | Docker 29.9, Compose v2 | **Seul prérequis pour lancer l'application** |
| Git | 2.5x | Récupérer le dépôt |
| Python | 3.13 ou plus | Lancer les tests backend (facultatif) |
| Node.js | 22 ou plus | Lancer les tests de l'interface (facultatif) |
| GNU make | 4.x | Raccourcis (facultatif ; sous Windows : `winget install ezwinports.make`) |

Ports utilisés par défaut sur la machine : **5433** (PostgreSQL), **8000** (API), **8080** (application web).
Ils se changent dans `.env` (variables `DB_PORT`, `API_PORT`, `WEB_PORT`).

## 2. Installer et lancer (5 commandes)

```bash
git clone <url-du-depot> shop && cd shop
cp .env.example .env
# éditer .env : mettre une valeur longue et aléatoire dans JWT_SECRET (32 caractères minimum)
docker compose up -d --build --wait
./scripts/smoke.sh   # BASE=http://127.0.0.1:8080/api ./scripts/smoke.sh pour passer par le serveur web
```

Ouvrir ensuite **http://localhost:8080**.

Comptes de démonstration (données d'essai, à ne pas utiliser en production) :

| Rôle | Email | Mot de passe |
| --- | --- | --- |
| Client | demo@example.com | demo1234 |
| Personnel | staff@example.com | staff1234 |
| Administrateur | admin@example.com | admin1234 |

Le premier démarrage charge 50 000 produits de démonstration (quelques secondes). Arrêter : `docker compose down` ;
tout effacer, données comprises : `docker compose down -v`.

**Vérification automatique de l'installation** (clone propre, ports isolés, chronomètre, journal dans
`reports/portabilite/`) : `./scripts/installation-propre.sh`.

## 3. Lancer chaque couche de test

Préparer une fois l'environnement de test :

```bash
python -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements-dev.txt     # Windows : backend\.venv\Scripts\pip
cd web && npm ci && npx playwright install chromium firefox && cd ..
docker compose up -d --wait db                                    # base PostgreSQL seule
```

| Couche | Commande | Rapport produit |
| --- | --- | --- |
| Qualité du code + traçabilité | `make lint docs` | sortie console |
| Unitaires | `make test-unit` | `reports/junit-unit.xml` |
| Intégration | `make test-integration` | `reports/junit-integration.xml` |
| API + matrice des droits | `make test-api` | `reports/junit-api.xml` |
| Contrat OpenAPI (Schemathesis) | `make test-contract` | `reports/junit-contract.xml` |
| Couverture + couverture de l'API | `make coverage api-coverage` | `reports/coverage.xml`, `reports/htmlcov/`, `reports/api-coverage.md` |
| Tout le backend d'un coup | `make check` | tous les rapports ci-dessus |
| E2E + accessibilité (machine locale) | `make e2e` | `reports/junit-e2e.xml`, `reports/a11y/` |
| E2E dans Docker (Firefox, parallèle) | `make stack` puis `./scripts/e2e-docker.sh` | `reports/junit-e2e-docker.xml` |
| Portabilité | `make install-check` | `reports/portabilite/installation-<machine>.log` |

Sans `make`, chaque cible du `Makefile` est une commande lisible que l'on peut copier.

## 4. Dépannage

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| `port is already allocated` | un autre programme utilise 5433, 8000 ou 8080 | changer `DB_PORT`, `API_PORT` ou `WEB_PORT` dans `.env` |
| L'API redémarre en boucle, journal « jwt_secret … at least 32 characters » | `JWT_SECRET` vide ou trop court | mettre 32 caractères ou plus dans `.env`, puis `docker compose up -d` |
| Mot de passe PostgreSQL refusé sur le port 5432 | un PostgreSQL installé sur la machine répond à la place de Docker | garder `DB_PORT=5433` (valeur par défaut) |
| Les données de démonstration manquent | le volume existait déjà avant (les migrations ne s'appliquent qu'au premier démarrage) | `docker compose down -v` puis relancer |
| Tests E2E lents ou bloqués en parallèle sous Windows | ENV-01 (`docs/anomalies.md`) | garder 1 worker (défaut) ou utiliser `./scripts/e2e-docker.sh` |
| Firefox ne démarre pas sous Windows (« spawn UNKNOWN ») | ENV-02 : bibliothèque Visual C++ manquante | `./scripts/e2e-docker.sh firefox`, ou installer le redistribuable Visual C++ |
| `python3` introuvable sous Windows | seul `python` est installé | les scripts choisissent `python` automatiquement |
