# Synthèse des analyses de sécurité (générée)

Générée par `tools/security_summary.py` le 2026-11-20T07:29:54+00:00 à partir des rapports bruts. « aucun » = l'outil a tourné et n'a rien signalé.

| Famille | Outil | Cible | Constats par gravité | Rapport brut |
| --- | --- | --- | --- | --- |
| SAST | Bandit | backend/app | aucun | `reports/sast/bandit.json` |
| SAST | Semgrep (owasp-top-ten, python, typescript) | dépôt | ERROR : 3 | `reports/sast/semgrep.json` |
| Secrets | gitleaks | historique Git complet | findings : 242 | `reports/sast/gitleaks.json` |
| SCA | pip-audit | 31 paquets Python | aucun | `reports/sca/pip-audit.json` |
| SCA | npm audit --omit=dev | dépendances web | aucun | `reports/sca/npm-audit.json` |
| SCA | Trivy fs (dépôt) | /repo | aucun | `reports/sca/trivy-fs.json` |
| SCA | Trivy image shop-api | shop-api | aucun | `reports/sca/trivy-image-api.json` |
| SCA | Trivy image shop-web | shop-web | aucun | `reports/sca/trivy-image-web.json` |
| Config | Hadolint | backend/Dockerfile | aucun | `reports/sca/hadolint-backend.json` |
| Config | Hadolint | web/Dockerfile | aucun | `reports/sca/hadolint-web.json` |
| SBOM | Syft (CycloneDX) | sbom-api | composants : 995 | `reports/sca/sbom-api.cdx.json` |
| SBOM | Syft (CycloneDX) | sbom-web | composants : 1282 | `reports/sca/sbom-web.cdx.json` |
| DAST | OWASP ZAP baseline | pile locale | Informational : 2 | `reports/dast/zap-baseline.json` |
| DAST | OWASP ZAP api | pile locale | High : 1, Informational : 3 | `reports/dast/zap-api.json` |
