# Autorisation de tests de sécurité

Fiche 4 et TP3 : « Ne jamais scanner un système sans autorisation écrite ». Ce document autorise les tests de
sécurité décrits ci-dessous, et seulement eux.

| Élément | Valeur |
| --- | --- |
| Propriétaire du système | Le groupe projet « Gestion commerciale » (propriétaire du code et de l'environnement) |
| Système visé | La pile Docker Compose de ce dépôt, lancée sur la machine du groupe |
| Cibles autorisées | `http://127.0.0.1:8080` / `http://localhost:8080` (web), `http://127.0.0.1:8000` (API), et les mêmes services sur le réseau Docker interne (`http://web:8080`, `http://api:8000`) |
| Cibles interdites | Tout autre hôte, toute adresse publique, tout service tiers |
| Données | Données de démonstration uniquement (aucune donnée réelle ni personnelle) |
| Types de tests | SAST (Semgrep, Bandit), détection de secrets (gitleaks), SCA (pip-audit, npm audit, Trivy, Syft), DAST passif (ZAP baseline), DAST actif (ZAP API scan), 4 attaques manuelles automatisées (injection SQL, XSS stocké, contrôle d'accès, session) |
| Période | Du 19/11/2026 au 21/11/2026 |
| Conditions | Arrêt immédiat en cas d'effet sur un autre système ; la base de démonstration peut être réinitialisée (`docker compose down -v`) |

## Signature

| Nom | Rôle | Date | Signature |
| --- | --- | --- | --- |
| | Responsable du groupe projet | | |
