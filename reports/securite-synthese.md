# Synthèse des analyses de sécurité (générée)

Générée par `tools/security_summary.py` le 2026-11-19T22:55:39+00:00 à partir des rapports bruts. « aucun » = l'outil a tourné et n'a rien signalé.

| Famille | Outil | Cible | Constats par gravité | Rapport brut |
| --- | --- | --- | --- | --- |
| SAST | Bandit | backend/app | aucun | `reports/sast/bandit.json` |
| SAST | Semgrep (owasp-top-ten, python, typescript) | dépôt | ERROR : 1 | `reports/sast/semgrep.json` |
| Secrets | gitleaks | historique Git complet | aucun | `reports/sast/gitleaks.json` |
| SCA | pip-audit | 31 paquets Python | aucun | `reports/sca/pip-audit.json` |
| SCA | npm audit --omit=dev | dépendances web | aucun | `reports/sca/npm-audit.json` |
| SCA | Trivy fs (dépôt) | /repo | aucun | `reports/sca/trivy-fs.json` |
| SCA | Trivy image shop-api | shop-api | aucun | `reports/sca/trivy-image-api.json` |
| SCA | Trivy image shop-web | shop-web | aucun | `reports/sca/trivy-image-web.json` |
| Config | Hadolint | backend/Dockerfile | aucun | `reports/sca/hadolint-backend.json` |
| Config | Hadolint | web/Dockerfile | aucun | `reports/sca/hadolint-web.json` |
| SBOM | Syft (CycloneDX) | sbom-api | composants : 995 | `reports/sca/sbom-api.cdx.json` |
| SBOM | Syft (CycloneDX) | sbom-web | composants : 1282 | `reports/sca/sbom-web.cdx.json` |
