"""Traceability matrix (fiche 1): exigence -> condition -> scénario -> cas -> script -> outil -> verdict -> preuve.

Reads docs/exigences.yaml, docs/cahier-de-test.md and the raw reports in reports/ (JUnit from pytest and Playwright,
k6 summaries, reliability measurements, coverage, SAST/SCA/DAST JSON, complexity, layer contracts, install logs,
manual records in docs/preuves/manuel/). Writes <out>/matrice.csv and <out>/matrice.md.
Exit code 1 if a P0 requirement is NOT RUN or FAIL (a documented deviation must then explain it).

Usage: backend/.venv/Scripts/python tools/trace.py --requirements docs/exigences.yaml --reports reports \
           --out docs/tracabilite
"""

import argparse
import csv
import fnmatch
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from defusedxml import ElementTree as ET

CASE_RE = re.compile(r"\b((?:CT|IT|TA|E2E|SEC|PERF|REL|UX|MA|PORT)-\d+)")
PASS, FAIL, NOT_RUN, PARTIAL = "PASS", "FAIL", "NOT RUN", "PARTIAL"


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else []


# ---------------------------------------------------------------- JUnit (pytest and Playwright)
def junit_results(reports: Path) -> dict[str, list[dict]]:
    """case id -> list of {script, tool, ok, skipped, file}."""
    out: dict[str, list[dict]] = defaultdict(list)
    for f in sorted(reports.glob("junit-*.xml")):
        tool = "Playwright" if "e2e" in f.name else "pytest"
        for tc in ET.parse(f).iter("testcase"):
            name = tc.get("name", "")
            props = {p.get("name"): p.get("value") for p in tc.iter("property")}
            ids = set(CASE_RE.findall(name)) | ({props["case"]} if props.get("case") else set())
            failed = tc.find("failure") is not None or tc.find("error") is not None
            skipped = tc.find("skipped") is not None
            for case in ids:
                out[case].append(
                    {
                        "script": f"{tc.get('classname', '')}::{name}"[:160],
                        "tool": tool,
                        "ok": not failed,
                        "skipped": skipped,
                        "file": f"reports/{f.name}",
                    }
                )
    return out


# ---------------------------------------------------------------- tool-based cases
def k6_case(reports: Path, name: str) -> tuple[str, str, str]:
    data = load_json(reports / "perf" / f"{name}.json")
    if not data:
        return NOT_RUN, "k6 : rapport absent", f"reports/perf/{name}.json"
    thresholds = {f"{m}: {expr}": t["ok"] for m, v in data["metrics"].items() for expr, t in (v.get("thresholds") or {}).items()}
    ok = bool(thresholds) and all(thresholds.values())
    detail = []
    for m in (
        "http_req_duration{name:list}",
        "http_req_duration{name:detail}",
        "http_req_duration{name:search}",
        "http_req_duration",
    ):
        if m in data["metrics"] and "p(95)" in data["metrics"][m]["values"]:
            detail.append(f"{m.replace('http_req_duration', 'p95')} = {data['metrics'][m]['values']['p(95)']:.0f} ms")
    if "http_req_failed" in data["metrics"]:
        detail.append(f"erreurs = {data['metrics']['http_req_failed']['values']['rate'] * 100:.2f} %")
    return (PASS if ok else FAIL), "k6 : " + "; ".join(detail[:3]), f"reports/perf/{name}.json"


def reliability_case(reports: Path, name: str) -> tuple[str, str, str]:
    r = load_json(reports / "reliability" / f"{name}.json")
    if not r:
        return NOT_RUN, "mesure absente", f"reports/reliability/{name}.json"
    ok = (
        r.get("recovery_seconds_from_fault") is not None
        and r["recovery_seconds_from_fault"] < 60
        and r["http_500_outside_outage_window"] == 0
        and r["orders_acknowledged_201"] == r["orders_acknowledged_found_in_database"]
        and all(v == 0 for v in r["consistency"].values())
    )
    detail = (
        f"reprise {r.get('recovery_seconds_from_fault')} s ; 500 hors panne : {r['http_500_outside_outage_window']} ; "
        f"commandes 201 retrouvées : {r['orders_acknowledged_found_in_database']}/{r['orders_acknowledged_201']}"
    )
    return (PASS if ok else FAIL), detail, f"reports/reliability/{name}.json"


def sast_case(reports: Path, justified: dict) -> tuple[str, str, str]:
    bandit, semgrep, leaks = (load_json(reports / "sast" / n) for n in ("bandit.json", "semgrep.json", "gitleaks.json"))
    if bandit is None or semgrep is None or leaks is None:
        return NOT_RUN, "rapport SAST absent", "reports/sast/"
    allowed = {(j["rule"], j["path"]) for j in justified.get("semgrep", [])}
    blocking = [r for r in semgrep["results"] if (r["check_id"].split(".")[-1], r["path"]) not in allowed]
    high = [r for r in bandit["results"] if r["issue_severity"] in ("HIGH", "MEDIUM")]
    leak_rules = justified.get("gitleaks", [])
    open_leaks = [
        x for x in leaks if not any(x["RuleID"] == j["rule"] and fnmatch.fnmatch(x["File"], j["path"]) for j in leak_rules)
    ]
    ok = not blocking and not high and not open_leaks
    justified_count = len(semgrep["results"]) - len(blocking)
    detail = (
        f"Bandit {len(bandit['results'])}, Semgrep {len(semgrep['results'])} ({justified_count} justifié), "
        f"gitleaks {len(leaks)} ({len(leaks) - len(open_leaks)} justifié)"
    )
    return (PASS if ok else FAIL), detail, "reports/sast/"


def sca_case(reports: Path) -> tuple[str, str, str]:
    pip = load_json(reports / "sca" / "pip-audit.json")
    npm = load_json(reports / "sca" / "npm-audit.json")
    images = [load_json(reports / "sca" / f"trivy-image-{i}.json") for i in ("api", "web")]
    fs = load_json(reports / "sca" / "trivy-fs.json")
    if None in (pip, npm, fs) or None in images:
        return NOT_RUN, "rapport SCA absent", "reports/sca/"
    pip_v = sum(len(d.get("vulns", [])) for d in pip["dependencies"])
    npm_v = npm.get("metadata", {}).get("vulnerabilities", {})
    sev = [v["Severity"] for t in [*images, fs] for res in t.get("Results", []) for v in res.get("Vulnerabilities") or []]
    blocking = (
        pip_v
        + npm_v.get("high", 0)
        + npm_v.get("critical", 0)
        + npm_v.get("moderate", 0)
        + sum(s in ("HIGH", "CRITICAL", "MEDIUM") for s in sev)
    )
    detail = (
        f"pip-audit {pip_v} ({len(pip['dependencies'])} paquets), npm {npm_v.get('total', 0)}, Trivy {len(sev)} (images + dépôt)"
    )
    return (PASS if blocking == 0 else FAIL), detail, "reports/sca/"


def dast_case(reports: Path, justified: dict) -> tuple[str, str, str]:
    allowed = {j["pluginid"] for j in justified.get("zap", [])}
    found, blocking = 0, 0
    for name in ("zap-baseline.json", "zap-api.json"):
        z = load_json(reports / "dast" / name)
        if z is None:
            return NOT_RUN, "rapport ZAP absent", "reports/dast/"
        for site in z["site"]:
            for a in site["alerts"]:
                found += 1
                if a["riskcode"] in ("3", "2") and a["pluginid"] not in allowed:
                    blocking += 1
    detail = f"ZAP : {found} alertes, {blocking} High/Medium non justifiée"
    return (PASS if blocking == 0 else FAIL), detail, "reports/dast/"


def coverage_case(reports: Path) -> tuple[str, str, str]:
    path = reports / "coverage.xml"
    if not path.exists():
        return NOT_RUN, "coverage.xml absent", "reports/coverage.xml"
    lines_valid = lines_covered = branches_valid = branches_covered = 0
    for cls in ET.parse(path).iter("class"):
        if cls.get("filename", "").replace("\\", "/").startswith("app/services/"):
            for line in cls.iter("line"):
                lines_valid += 1
                lines_covered += int(line.get("hits", "0")) > 0
                if line.get("branch") == "true":
                    cov = re.match(r"(\d+)% \((\d+)/(\d+)\)", line.get("condition-coverage", "0% (0/0)"))
                    if cov:
                        branches_covered += int(cov.group(2))
                        branches_valid += int(cov.group(3))
    total = (lines_covered + branches_covered) / max(1, lines_valid + branches_valid)
    detail = (
        f"app/services : instructions {lines_covered}/{lines_valid}, "
        f"branches {branches_covered}/{branches_valid}, total {total * 100:.1f} %"
    )
    return (PASS if total >= 0.8 else FAIL), detail, "reports/coverage.xml"


def mutation_case(reports: Path, junit: dict) -> tuple[str, str, str]:
    stats = load_json(reports / "maintenabilite" / "mutmut-stats.json")
    props = junit.get("MA-02", [])
    if not stats and not props:
        return NOT_RUN, "mutation et propriété non exécutées", "reports/maintenabilite/"
    props_ok = bool(props) and all(r["ok"] for r in props)
    if stats:
        killed, total = stats.get("killed", 0), stats.get("total", 0)
        score = f"mutants tués {killed}/{total} ({killed / max(1, total) * 100:.0f} %)"
    else:
        score = "mutation : non disponible"
    return (
        (PASS if props_ok and stats else PARTIAL if props_ok else FAIL),
        f"Hypothesis {'OK' if props_ok else 'KO'} ; {score}",
        "reports/maintenabilite/",
    )


def complexity_case(reports: Path) -> tuple[str, str, str]:
    radon = load_json(reports / "maintenabilite" / "radon-cc.json")
    if radon is None:
        return NOT_RUN, "radon absent", "reports/maintenabilite/radon-cc.json"
    blocks = [b["complexity"] for bs in radon.values() for b in bs]
    return (
        (PASS if max(blocks) <= 10 else FAIL),
        f"radon : {len(blocks)} blocs, maximum {max(blocks)}",
        "reports/maintenabilite/radon-cc.json",
    )


def layers_case(reports: Path) -> tuple[str, str, str]:
    path = reports / "maintenabilite" / "import-linter.txt"
    if not path.exists():
        return NOT_RUN, "import-linter absent", str(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Contracts: (\d+) kept, (\d+) broken", text)
    ok = bool(m) and m.group(2) == "0"
    return (
        (PASS if ok else FAIL),
        f"import-linter : {m.group(0) if m else 'résultat illisible'}",
        "reports/maintenabilite/import-linter.txt",
    )


def install_case(reports: Path, local: bool) -> tuple[str, str, str]:
    logs = sorted((reports / "portabilite").glob("installation-*.log"))
    logs = [p for p in logs if (("machine2" not in p.name) if local else ("machine2" in p.name))]
    if not logs:
        return (
            NOT_RUN,
            "journal d'installation absent" + ("" if local else " (seconde machine : en attente)"),
            "reports/portabilite/",
        )
    text = logs[-1].read_text(encoding="utf-8", errors="replace")
    secs = re.search(r"OK in (\d+)s", text)
    ok = "VERDICT: PASS" in text
    return (PASS if ok else FAIL), f"installation en {secs.group(1) if secs else '?'} s", f"reports/portabilite/{logs[-1].name}"


def manual_case(root: Path, case: str) -> tuple[str, str, str] | None:
    path = root / "docs" / "preuves" / "manuel" / "utilisabilite.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None
    if not data or case not in data.get("verdicts", {}):
        return NOT_RUN, "sessions d'utilisabilité en attente", "docs/utilisabilite.md"
    v = data["verdicts"][case]
    return v["verdict"], v["detail"], str(path.relative_to(root)).replace("\\", "/")


TOOL_CASES = {
    "PERF-01": ("k6", lambda r, j, x, root: k6_case(r, "smoke")),
    "PERF-02": ("k6", lambda r, j, x, root: k6_case(r, "load")),
    "PERF-03": ("k6", lambda r, j, x, root: k6_case(r, "search")),
    "REL-01": ("tools/reliability.py + k6-like probe", lambda r, j, x, root: reliability_case(r, "rel-01")),
    "REL-02": ("tools/reliability.py", lambda r, j, x, root: reliability_case(r, "rel-02")),
    "SEC-05": ("Semgrep, Bandit, gitleaks", lambda r, j, x, root: sast_case(r, x)),
    "SEC-06": ("pip-audit, npm audit, Trivy, Syft", lambda r, j, x, root: sca_case(r)),
    "SEC-07": ("OWASP ZAP", lambda r, j, x, root: dast_case(r, x)),
    "MA-01": ("pytest-cov", lambda r, j, x, root: coverage_case(r)),
    "MA-02": ("Hypothesis, mutmut", lambda r, j, x, root: mutation_case(r, j)),
    "MA-03": ("radon, xenon", lambda r, j, x, root: complexity_case(r)),
    "MA-04": ("import-linter, ruff", lambda r, j, x, root: layers_case(r)),
    "PORT-01": ("scripts/installation-propre.sh", lambda r, j, x, root: install_case(r, True)),
    "PORT-02": ("docs/installation.md (seconde machine)", lambda r, j, x, root: install_case(r, False)),
    "UX-02": ("protocole + script", lambda r, j, x, root: manual_case(root, "UX-02")),
    "UX-03": ("questionnaire SUS + script", lambda r, j, x, root: manual_case(root, "UX-03")),
}


def case_verdict(case: str, junit: dict, reports: Path, justified: dict, root: Path) -> tuple[str, str, str, str, str]:
    """(verdict, script, tool, detail, proof)."""
    if case in TOOL_CASES:  # cases measured by a tool other than a test runner
        tool, fn = TOOL_CASES[case]
        verdict, detail, proof = fn(reports, junit, justified, root)
        return verdict, tool, tool, detail, proof
    runs = [r for r in junit.get(case, []) if not r["skipped"]]
    if not runs:
        return NOT_RUN, "—", "—", "aucun résultat d'exécution", "—"
    ok = all(r["ok"] for r in runs)
    tools = sorted({r["tool"] for r in runs})
    files = sorted({r["file"] for r in runs})
    script = runs[0]["script"] + (f" (+{len(runs) - 1})" if len(runs) > 1 else "")
    return (
        (PASS if ok else FAIL),
        script,
        ", ".join(tools),
        f"{sum(r['ok'] for r in runs)}/{len(runs)} exécutions réussies",
        ", ".join(files),
    )


def cahier_objectives(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| ((?:CT|IT|TA|E2E|SEC|PERF|REL|UX|MA|PORT)-\d+) \| ([^|]+)\|", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def combine(verdicts: list[str]) -> str:
    if not verdicts:
        return NOT_RUN
    if FAIL in verdicts:
        return FAIL
    if all(v == PASS for v in verdicts):
        return PASS
    if all(v == NOT_RUN for v in verdicts):
        return NOT_RUN
    return PARTIAL


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", default="docs/exigences.yaml")
    parser.add_argument("--reports", default="reports")
    parser.add_argument("--out", default="docs/tracabilite")
    args = parser.parse_args()
    root = Path(args.requirements).resolve().parents[1]
    reports, out = Path(args.reports), Path(args.out)
    spec = yaml.safe_load(Path(args.requirements).read_text(encoding="utf-8"))
    justified = yaml.safe_load((root / "docs" / "securite" / "justifications.yaml").read_text(encoding="utf-8"))
    objectives = cahier_objectives(root / "docs" / "cahier-de-test.md")
    junit = junit_results(reports)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()

    rows, req_verdict = [], {}
    for e in spec["exigences"]:
        cases = e.get("cas", [])
        case_results = []
        for case in cases:
            verdict, script, tool, detail, proof = case_verdict(case, junit, reports, justified, root)
            case_results.append(verdict)
            rows.append(
                [
                    e["id"],
                    objectives.get(case, ""),
                    ", ".join(e.get("scenarios", [])),
                    case,
                    script,
                    tool,
                    verdict,
                    detail,
                    proof,
                    commit,
                ]
            )
        req_verdict[e["id"]] = combine(case_results)
    # QR-FS-01 has no own case: it holds when every P0 FR and BR is at PASS.
    p0_functional = [e["id"] for e in spec["exigences"] if e["type"] in ("FR", "BR") and e["priorite"] == "P0"]
    fs = PASS if all(req_verdict[r] == PASS for r in p0_functional) else FAIL
    req_verdict["QR-FS-01"] = fs
    rows.append(
        [
            "QR-FS-01",
            "Toutes les FR/BR P0 au verdict PASS",
            "—",
            "—",
            "tools/trace.py",
            "matrice",
            fs,
            f"{sum(req_verdict[r] == PASS for r in p0_functional)}/{len(p0_functional)} FR/BR P0 au PASS",
            "docs/tracabilite/matrice.csv",
            commit,
        ]
    )

    out.mkdir(parents=True, exist_ok=True)
    header = [
        "exigence",
        "condition de test",
        "scénario",
        "cas de test",
        "script",
        "outil",
        "verdict",
        "mesure",
        "preuve",
        "commit de génération",
    ]
    with open(out / "matrice.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(header)
        w.writerows(rows)

    by_id = {e["id"]: e for e in spec["exigences"]}
    totals = defaultdict(int)
    for v in req_verdict.values():
        totals[v] += 1
    md = [
        "# Matrice de traçabilité (générée)",
        "",
        f"Générée par `tools/trace.py` le {datetime.now(UTC).isoformat(timespec='seconds')}, commit `{commit}`, à partir de "
        "`docs/exigences.yaml` et des rapports bruts de `reports/` (copiés à l'identique dans `docs/preuves/<version>/` "
        "au gel, avec empreintes SHA-256). La colonne « commit de génération » date la matrice, pas la mesure : le "
        "commit de chaque mesure est indiqué dans `docs/conformite.md`. Ne pas modifier à la main : relancer `/trace`.",
        "",
        "## Synthèse par exigence",
        "",
        "| Verdict | Nombre |",
        "| --- | --- |",
        *[f"| {k} | {totals[k]} |" for k in (PASS, PARTIAL, NOT_RUN, FAIL) if totals[k]],
        "",
        "| Exigence | Type | Priorité | Caractéristique | Verdict |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {rid} | {by_id[rid]['type']} | {by_id[rid]['priorite']} | {by_id[rid]['caracteristique']} | {v} |"
            for rid, v in req_verdict.items()
        ],
        "",
        "## Détail : exigence → condition → scénario → cas → script → outil → verdict → preuve",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
        *["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows],
        "",
    ]
    (out / "matrice.md").write_text("\n".join(md), encoding="utf-8")
    unknown = sorted(set(junit) - {c for e in spec["exigences"] for c in e.get("cas", [])})
    blocking = [
        rid for rid, v in req_verdict.items() if by_id.get(rid, {"priorite": "P0"})["priorite"] == "P0" and v in (NOT_RUN, FAIL)
    ]
    print("Verdicts par exigence :", dict(totals))
    print("Cas présents dans les rapports mais absents de exigences.yaml :", unknown or "aucun")
    print("Exigences P0 NOT RUN ou FAIL :", blocking or "aucune")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
