"""Run a tool and save its raw standard output, unmodified, as a report file (golden rule: tools write evidence).

Usage: python tools/capture.py --out reports/sca/hadolint-backend.json -- docker run --rm -i hadolint/hadolint ...
       python tools/capture.py --out FILE --stdin backend/Dockerfile -- <command>   (feed a file on stdin)
The exit code of the tool is printed and returned, so a failing scan stays visible; stderr is passed through.
Options: --with-stderr saves stderr after stdout (tools such as xenon report only on stderr);
         --status saves the command, exit code and UTC time to OUT.status.json (proof that a silent tool ran).
"""

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--stdin")
    parser.add_argument("--with-stderr", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    command[0] = shutil.which(command[0]) or command[0]  # resolve like a shell (Windows needs the .exe)
    stdin = Path(args.stdin).read_bytes() if args.stdin else None
    started = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    stderr = subprocess.PIPE if args.with_stderr else None
    run = subprocess.run(command, input=stdin, stdout=subprocess.PIPE, stderr=stderr, check=False)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(run.stdout + (run.stderr or b""))
    if args.status:
        status = {"command": [Path(command[0]).name, *command[1:]], "exit_code": run.returncode, "started_utc": started}
        Path(f"{out}.status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{' '.join(command[:4])}... -> {out} ({len(run.stdout)} bytes), exit code {run.returncode}")
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
