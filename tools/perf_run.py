"""Run one k6 script on the Compose network and sample `docker stats` every N seconds meanwhile (PERF-01..03).

k6 writes reports/perf/<script>.json itself (handleSummary); this tool writes the resource samples to
reports/perf/ressources-<script>.csv and the machine description to reports/perf/environnement.txt.
Usage: backend/.venv/Scripts/python tools/perf_run.py load [--interval 10] [--env DURATION=5m]
"""

import argparse
import csv
import platform
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "perf"


def docker_path(p: Path) -> str:
    """Absolute path Docker Desktop understands on Windows (C:/...), unchanged elsewhere."""
    return p.resolve().as_posix()


def environment() -> str:
    def run(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
        except OSError:
            return "non disponible"

    info = run(["docker", "info", "--format", "{{.NCPU}} CPU, {{.MemTotal}} bytes RAM for Docker, {{.OperatingSystem}}"])
    return "\n".join(
        [
            f"Date (UTC): {datetime.now(UTC).isoformat(timespec='seconds')}",
            f"Host: {platform.node()} — {platform.system()} {platform.release()} ({platform.machine()})",
            f"Host CPU: {platform.processor()}",
            f"Docker: {run(['docker', 'version', '--format', '{{.Server.Version}}'])} — {info}",
            f"k6 image: {run(['docker', 'image', 'inspect', '--format', '{{index .RepoDigests 0}}', 'grafana/k6'])}",
            "Target: Docker Compose stack (db, api, web), k6 container on the same network, BASE_URL=http://web:8080",
            "",
        ]
    )


def sample(stop: threading.Event, interval: int, rows: list) -> None:
    while not stop.is_set():
        out = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.Name}};{{.CPUPerc}};{{.MemUsage}};{{.NetIO}};{{.BlockIO}}"],
            capture_output=True,
            text=True,
        ).stdout
        stamp = datetime.now(UTC).isoformat(timespec="seconds")
        for line in out.strip().splitlines():
            if line.startswith("shop-") and not line.startswith("shop-install"):
                rows.append([stamp, *line.split(";")])
        stop.wait(interval)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", choices=["smoke", "load", "search"])
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--network", default="shop_default")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "environnement.txt").write_text(environment(), encoding="utf-8")

    rows: list = []
    stop = threading.Event()
    sampler = threading.Thread(target=sample, args=(stop, args.interval, rows), daemon=True)
    sampler.start()
    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        args.network,
        "-v",
        f"{docker_path(ROOT / 'perf' / 'k6')}:/scripts:ro",
        "-v",
        f"{docker_path(OUT)}:/out",
    ]
    for e in args.env:
        cmd += ["-e", e]
    cmd += ["grafana/k6", "run", "--quiet", f"/scripts/{args.script}.js"]
    start = time.perf_counter()
    code = subprocess.run(cmd).returncode
    stop.set()
    sampler.join(timeout=30)

    with open(OUT / f"ressources-{args.script}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_utc", "container", "cpu", "memory", "net_io", "block_io"])
        w.writerows(rows)
    print(
        f"k6 {args.script}: exit code {code} (99 = a threshold failed) in {time.perf_counter() - start:.0f}s; "
        f"{len(rows)} resource samples"
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
