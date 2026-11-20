"""Freeze reports/ into docs/preuves/<version>/ with a manifest and SHA-256 sums.

Tool versions come from the tools themselves: `--version` of the native tools, and the version each
containerised tool wrote into its own report. Nothing is typed by hand.

Usage: python tools/freeze_evidence.py v1.0
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
VENV = ROOT / "backend" / ".venv" / "Scripts"

NATIVE = {
    "python": [str(VENV / "python"), "--version"],
    "pytest": [str(VENV / "pytest"), "--version"],
    "ruff": [str(VENV / "ruff"), "--version"],
    "node": ["node", "--version"],
    "playwright": ["npx", "--prefix", "web", "playwright", "--version"],
    "docker": ["docker", "--version"],
}


def run(cmd: list[str]) -> str:
    exe = shutil.which(cmd[0]) or cmd[0]
    try:
        out = subprocess.run([exe, *cmd[1:]], check=False, capture_output=True, text=True, timeout=60, cwd=ROOT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"non disponible ({exc.__class__.__name__})"
    text = (out.stdout or out.stderr).strip().splitlines()
    return text[0] if text else "non disponible"


def from_reports() -> dict[str, str]:
    found: dict[str, str] = {}

    def load(rel: str):
        p = REPORTS / rel
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    semgrep = load("sast/semgrep.json")
    if semgrep and semgrep.get("version"):
        found["semgrep"] = semgrep["version"]
    zap = load("dast/zap-api.json")
    if zap and zap.get("@version"):
        found["zap"] = zap["@version"]
    for name in ("sca/sbom-api.cdx.json", "sca/sbom.cdx.json"):
        sbom = load(name)
        if sbom:
            tools = sbom.get("metadata", {}).get("tools", {})
            comps = tools.get("components", tools) if isinstance(tools, dict) else tools
            for t in comps or []:
                if t.get("name") and t.get("version"):
                    found[t["name"]] = t["version"]
            break
    for rel in ("perf/environnement.txt", "maintenabilite/mutmut-run.txt"):
        p = REPORTS / rel
        if p.exists():
            for m in re.finditer(r"\b(k6|mutmut|trivy|syft|Docker)\b[^\n]*?v?(\d+\.\d+\.\d+)", p.read_text(encoding="utf-8")):
                found.setdefault(m.group(1).lower(), m.group(2))
    return found


def git(*args: str) -> str:
    return run(["git", *args])


def main(version: str) -> int:
    dest = ROOT / "docs" / "preuves" / version
    if dest.exists():
        print(f"{dest} existe déjà : un gel ne s'écrase pas.", file=sys.stderr)
        return 1
    shutil.copytree(REPORTS, dest)
    files = sorted(p for p in dest.rglob("*") if p.is_file())
    manifest = {
        "version": version,
        "frozen_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "commit_short": git("rev-parse", "--short", "HEAD"),
        "code_changes_since_commit": git("status", "--porcelain", "--", "backend", "web", "db", "docker-compose.yml"),
        "source": "reports/",
        "file_count": len(files),
        "tools_native": {k: run(v) for k, v in NATIVE.items()},
        "tools_from_reports": from_reports(),
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(dest).as_posix()}" for p in files]
    (dest / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(files)} fichiers gelés dans {dest.relative_to(ROOT)} (commit {manifest['commit_short']})")
    print(json.dumps(manifest["tools_native"] | manifest["tools_from_reports"], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "v1.0"))
