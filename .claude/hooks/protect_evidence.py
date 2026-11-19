# PreToolUse: exit code 2 blocks the edit and tells Claude why (règle d'or du cahier des charges).
import json
import sys

sys.stderr.reconfigure(encoding="utf-8")
data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = (tool_input.get("file_path") or tool_input.get("notebook_path") or "").replace("\\", "/")
if path.startswith("reports/") or "/reports/" in path or "docs/preuves/" in path:
    print("Evidence is written by the tools only (règle d'or du cahier des charges).", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
