"""Check the traceability chain between docs/exigences.yaml, docs/exigences.md and docs/cahier-de-test.md.

Usage: python tools/check_docs.py [docs-dir]. Exit code 1 if any reference is broken.
"""

import re
import sys
import pathlib
import collections
import yaml

d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
y = yaml.safe_load((d / "exigences.yaml").read_text(encoding="utf-8"))
reqs = {e["id"]: e for e in y["exigences"]}
md = (d / "exigences.md").read_text(encoding="utf-8")
cahier = (d / "cahier-de-test.md").read_text(encoding="utf-8")
problems = []
# 1. case rows in the cahier
rows = {}
for line in cahier.splitlines():
    m = re.match(r"\| ((?:CT|IT|TA|E2E|SEC|PERF|REL|UX|MA|PORT)-\d+) \|(.*)\|\s*$", line)
    if m:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if m.group(1) in rows:
            problems.append(f"duplicate case {m.group(1)}")
        rows[m.group(1)] = cells
for cid, cells in rows.items():
    if cells[-3] or cells[-2]:
        problems.append(f"{cid}: obtenu/verdict not empty")
    if cells[-1] not in ("valide", "échec attendu"):
        problems.append(f"{cid}: type '{cells[-1]}'")
    for rid in re.findall(r"\b(?:FR|BR)-\d\d\b|\bQR-[A-Z]{2}-\d\d\b", cells[2]):
        if rid not in reqs:
            problems.append(f"{cid}: unknown requirement {rid}")
# 2. yaml references
for rid, e in reqs.items():
    for c in e.get("cas", []):
        if c not in rows:
            problems.append(f"{rid}: case {c} not in cahier")
        elif rid not in rows[c][2] and not (rid.startswith("QR") or rid in rows[c][3]):
            problems.append(f"{rid}: case {c} does not cite {rid} in its règle column")
    for s in e.get("scenarios", []):
        if f"**{s} " not in md:
            problems.append(f"{rid}: scenario {s} not in exigences.md")
    if e["type"] in ("FR", "BR") and not e.get("cas"):
        problems.append(f"{rid}: no case")
    if e["caracteristique"] not in y["caracteristiques"]:
        problems.append(f"{rid}: bad caracteristique")
# 3. every BR has a valid and a refusal scenario
for rid in [r for r in reqs if r.startswith("BR")]:
    block = md.split(f"### {rid}")[1].split("###")[0]
    if "(valide" not in block or "(refus" not in block:
        problems.append(f"{rid}: missing valid or refusal scenario")
# 4. every case cites a requirement that lists it (reverse trace)
listed = {c for e in reqs.values() for c in e.get("cas", [])}
for cid in rows:
    if cid not in listed:
        problems.append(f"{cid}: not referenced by any requirement in exigences.yaml")
# 5. coverage of characteristics
chars = collections.Counter(e["caracteristique"] for e in reqs.values() if e["type"] == "QR")
for k in y["caracteristiques"]:
    if not chars[k]:
        problems.append(f"no QR for {k}")
# counts
cnt = collections.defaultdict(collections.Counter)
for cid, cells in rows.items():
    cnt[cid.split("-")[0]][cells[-1]] += 1
print(
    "requirements:",
    collections.Counter(e["type"] for e in reqs.values()),
    "questions:",
    len(y["questions"]),
)
tot = 0
for lvl in ["CT", "IT", "TA", "E2E", "SEC", "PERF", "REL", "UX", "MA", "PORT"]:
    c = cnt[lvl]
    n = sum(c.values())
    tot += n
    print(f"{lvl:5} {n:3}  valide {c['valide']:3}  échec attendu {c['échec attendu']:3}")
print("total", tot)
print(
    "NON SPÉCIFIÉ:",
    sorted(
        (c for c, cells in rows.items() if "NON SPÉCIFIÉ" in "|".join(cells)),
        key=lambda s: (s.split("-")[0], int(s.split("-")[1])),
    ),
)
print("PROBLEMS:" if problems else "no problems", *problems, sep="\n  ")
sys.exit(1 if problems else 0)
