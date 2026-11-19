"""Fill the « Obtenu » and « Verdict » columns of docs/cahier-de-test.md from docs/tracabilite/matrice.csv.

Phase 9 (fiche 1, Clôturer): results come from the generated matrix (itself built from the raw reports), never by hand.
Usage: backend/.venv/Scripts/python tools/fill_cahier.py [--cahier docs/cahier-de-test.md] [--matrix docs/tracabilite/matrice.csv]
"""

import argparse
import csv
import re
from pathlib import Path

ROW = re.compile(r"^\| ((?:CT|IT|TA|E2E|SEC|PERF|REL|UX|MA|PORT)-\d+) \|")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cahier", default="docs/cahier-de-test.md")
    parser.add_argument("--matrix", default="docs/tracabilite/matrice.csv")
    args = parser.parse_args()
    results: dict[str, tuple[str, str]] = {}
    with open(args.matrix, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            case = row["cas de test"]
            if case and case != "—":
                results[case] = (row["mesure"].replace("|", "/"), row["verdict"])

    path = Path(args.cahier)
    lines, filled = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m and m.group(1) in results:
            cells = line.strip().strip("|").split("|")
            obtained, verdict = results[m.group(1)]
            cells[-3], cells[-2] = f" {obtained} ", f" {verdict} "
            line = "|" + "|".join(cells) + "|"
            filled += 1
        lines.append(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{filled} cases filled from {args.matrix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
