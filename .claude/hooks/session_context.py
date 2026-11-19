# SessionStart: print the journal tail and last commits so a new session resumes the plan.
import os
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", pathlib.Path(__file__).resolve().parents[2]))
journal = root / "docs" / "journal.md"
if journal.exists():
    print("== docs/journal.md (last 30 lines) ==")
    print("\n".join(journal.read_text(encoding="utf-8").splitlines()[-30:]))
try:
    log = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True,
                         timeout=10, cwd=root).stdout
    if log:
        print("== last commits ==\n" + log)
except (OSError, subprocess.TimeoutExpired):
    pass
