"""Count findings per tool and severity, read from the raw SAST/SCA/DAST reports (fiche 4, QR-SE-01).

Usage: backend/.venv/Scripts/python tools/security_summary.py --out reports/securite-synthese.md
Every number in docs/securite/triage.md comes from this generated file.
"""

import argparse
import collections
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

R = Path("reports")


def load(path: Path) -> Any:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else []


def rows() -> list[tuple[str, str, str, dict[str, int], str]]:
    out = []
    bandit = load(R / "sast/bandit.json")
    if bandit is not None:
        c = collections.Counter(r["issue_severity"] for r in bandit["results"])
        out.append(("SAST", "Bandit", "backend/app", dict(c), "sast/bandit.json"))
    semgrep = load(R / "sast/semgrep.json")
    if semgrep is not None:
        c = collections.Counter(r["extra"].get("severity", "?") for r in semgrep["results"])
        out.append(("SAST", "Semgrep (owasp-top-ten, python, typescript)", "dépôt", dict(c), "sast/semgrep.json"))
    gitleaks = load(R / "sast/gitleaks.json")
    if gitleaks is not None:
        out.append(
            ("Secrets", "gitleaks", "historique Git complet", {"findings": len(gitleaks)} if gitleaks else {}, "sast/gitleaks.json")
        )
    pip = load(R / "sca/pip-audit.json")
    if pip is not None:
        n = sum(len(d.get("vulns", [])) for d in pip["dependencies"])
        out.append(
            ("SCA", "pip-audit", f"{len(pip['dependencies'])} paquets Python", {"vulns": n} if n else {}, "sca/pip-audit.json")
        )
    npm = load(R / "sca/npm-audit.json")
    if npm is not None:
        meta = npm.get("metadata", {}).get("vulnerabilities", {})
        out.append(
            (
                "SCA",
                "npm audit --omit=dev",
                "dépendances web",
                {k: v for k, v in meta.items() if v and k != "total"},
                "sca/npm-audit.json",
            )
        )
    for name, label in (
        ("trivy-fs.json", "Trivy fs (dépôt)"),
        ("trivy-image-api.json", "Trivy image shop-api"),
        ("trivy-image-web.json", "Trivy image shop-web"),
    ):
        t = load(R / "sca" / name)
        if t is not None:
            c = collections.Counter(v["Severity"] for res in t.get("Results", []) for v in res.get("Vulnerabilities") or [])
            c.update(
                {
                    "misconfig": sum(
                        len([m for m in res.get("Misconfigurations") or [] if m.get("Status") == "FAIL"])
                        for res in t.get("Results", [])
                    )
                }
                if "fs" in name
                else {}
            )
            out.append(("SCA", label, t.get("ArtifactName", ""), {k: v for k, v in c.items() if v}, f"sca/{name}"))
    for name in ("hadolint-backend.json", "hadolint-web.json"):
        h = load(R / "sca" / name)
        if h is not None:
            out.append(
                (
                    "Config",
                    "Hadolint",
                    name.split("-")[1].split(".")[0] + "/Dockerfile",
                    dict(collections.Counter(x["level"] for x in h)),
                    f"sca/{name}",
                )
            )
    for name in ("sbom-api.cdx.json", "sbom-web.cdx.json"):
        s = load(R / "sca" / name)
        if s is not None:
            out.append(
                ("SBOM", "Syft (CycloneDX)", name.split(".")[0], {"composants": len(s.get("components", []))}, f"sca/{name}")
            )
    for name in ("zap-baseline.json", "zap-api.json"):
        z = load(R / "dast" / name)
        if z is not None:
            risk = {"3": "High", "2": "Medium", "1": "Low", "0": "Informational"}
            c = collections.Counter(
                risk.get(str(a.get("riskcode")), "?") for site in z.get("site", []) for a in site.get("alerts", [])
            )
            out.append(("DAST", f"OWASP ZAP {name.split('-')[1].split('.')[0]}", "pile locale", dict(c), f"dast/{name}"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    lines = [
        "# Synthèse des analyses de sécurité (générée)",
        "",
        f"Générée par `tools/security_summary.py` le {datetime.now(UTC).isoformat(timespec='seconds')} à partir des "
        "rapports bruts. « aucun » = l'outil a tourné et n'a rien signalé.",
        "",
        "| Famille | Outil | Cible | Constats par gravité | Rapport brut |",
        "| --- | --- | --- | --- | --- |",
    ]
    for family, tool, target, counts, path in rows():
        found = ", ".join(f"{k} : {v}" for k, v in sorted(counts.items())) or "aucun"
        lines.append(f"| {family} | {tool} | {target} | {found} | `reports/{path}` |")
    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[5:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
