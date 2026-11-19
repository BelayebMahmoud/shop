# Gestion commerciale — projet ISO/IEC 25010

Application de gestion commerciale (clients, catalogue, stock, commandes, tableau de bord, journal d'audit) :
FastAPI + PostgreSQL + React/TypeScript, conteneurisée avec Docker Compose. Le projet démontre la conformité aux
8 caractéristiques de qualité ISO/IEC 25010 avec des preuves d'exécution réelles (`reports/`).

## Démarrage rapide

```bash
cp .env.example .env          # puis mettre une valeur longue et aléatoire dans JWT_SECRET
docker compose up -d --build --wait
```

Application : http://localhost:8080 · Documentation de l'API : http://localhost:8000/docs

Guide complet (prérequis, tests, dépannage) : [docs/installation.md](docs/installation.md).

## Documents

| Document | Rôle |
| --- | --- |
| [docs/exigences.yaml](docs/exigences.yaml), [docs/exigences.md](docs/exigences.md) | Exigences FR, BR, QR et scénarios Soit/Quand/Alors |
| [docs/plan-de-test.md](docs/plan-de-test.md), [docs/cahier-de-test.md](docs/cahier-de-test.md) | Plan et cahier de test |
| [docs/conception.md](docs/conception.md) | Architecture, modèle de données, matrice des droits |
| [docs/anomalies.md](docs/anomalies.md) | Journal des anomalies (confirmation et non-régression) |
| [docs/journal.md](docs/journal.md) | Déroulé des phases |
