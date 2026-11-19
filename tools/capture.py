"""Run a tool and save its raw standard output, unmodified, as a report file (golden rule: tools write evidence).

Usage: python tools/capture.py --out reports/sca/hadolint-backend.json -- docker run --rm -i hadolint/hadolint ...
       python tools/capture.py --out FILE --stdin backend/Dockerfile -- <command>   (feed a file on stdin)
The exit code of the tool is printed and returned, so a failing scan stays visible; stderr is passed through.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--stdin")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    command[0] = shutil.which(command[0]) or command[0]  # resolve like a shell (Windows needs the .exe)
    stdin = Path(args.stdin).read_bytes() if args.stdin else None
    run = subprocess.run(command, input=stdin, stdout=subprocess.PIPE)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(run.stdout)
    print(f"{' '.join(command[:4])}... -> {out} ({len(run.stdout)} bytes), exit code {run.returncode}")
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
