# PostToolUse: format and lint-fix a Python file right after Claude edits it.
# Uses the backend virtualenv's ruff first, then ruff on PATH; skips silently if neither exists.
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
candidates = [
    root / "backend" / ".venv" / "Scripts" / "ruff.exe",  # Windows
    root / "backend" / ".venv" / "bin" / "ruff",  # macOS / Linux
]
ruff = next((str(c) for c in candidates if c.exists()), None) or shutil.which("ruff")
if ruff:
    for args in (["format", "--quiet", path], ["check", "--fix", "--quiet", path]):
        try:
            subprocess.run([ruff, *args], check=False, timeout=30, cwd=root / "backend",
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired):
            pass  # make check still catches it
sys.exit(0)
