"""Measure real coordinator upload and download latency at several sizes."""

import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "experiments" / "results"


def _wait(url: str, seconds: float = 15) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if requests.get(url, timeout=.5).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(.1)
    raise RuntimeError(f"service did not start: {url}")


def _start_stack(db_path: Path) -> list[subprocess.Popen]:
    env = {**os.environ, "P2P_DB_PATH": str(db_path)}
    commands = [[sys.executable, "coordinator/app.py"], *[[sys.executable, "node/node_process.py", "--node-id", f"N{i}", "--port", str(6000 + i)] for i in range(1, 4)]]
    processes = [subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for command in commands]
    _wait("http://127.0.0.1:5000/status")
    time.sleep(1.2)  # allow all three heartbeats to register
    return processes


def _stop(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        process.terminate()
    for process in processes:
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="4096,65536,1048576", help="comma-separated byte sizes")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()
    sizes = [int(value) for value in args.sizes.split(",")]
    RESULTS.mkdir(parents=True, exist_ok=True)
    db_path = RESULTS / "upload_retrieval_benchmark.db"
    if db_path.exists(): db_path.unlink()
    processes = _start_stack(db_path)
    rows = []
    try:
        for size in sizes:
            payload = os.urandom(size)
            for trial in range(1, args.trials + 1):
                start = time.perf_counter()
                response = requests.post("http://127.0.0.1:5000/files", files={"file": (f"{size}.bin", payload)}, timeout=60)
                response.raise_for_status(); file_id = response.json()["file_id"]
                upload_ms = (time.perf_counter() - start) * 1000
                start = time.perf_counter(); response = requests.get(f"http://127.0.0.1:5000/files/{file_id}", timeout=60); response.raise_for_status()
                retrieval_ms = (time.perf_counter() - start) * 1000
                if response.content != payload: raise RuntimeError("retrieved bytes differ from upload")
                rows.append({"size_bytes": size, "trial": trial, "upload_ms": upload_ms, "retrieval_ms": retrieval_ms})
    finally:
        _stop(processes)
    raw = RESULTS / "upload_retrieval_raw.csv"
    with raw.open("w", newline="") as handle: writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    summary = []
    for size in sizes:
        group = [row for row in rows if row["size_bytes"] == size]
        summary.append({"size_bytes": size, "trials": len(group), "mean_upload_ms": sum(r["upload_ms"] for r in group)/len(group), "mean_retrieval_ms": sum(r["retrieval_ms"] for r in group)/len(group)})
    with (RESULTS / "upload_retrieval_summary.csv").open("w", newline="") as handle: writer = csv.DictWriter(handle, fieldnames=summary[0]); writer.writeheader(); writer.writerows(summary)
    print("size_bytes  upload_ms  retrieval_ms")
    for row in summary: print(f"{row['size_bytes']:10d}  {row['mean_upload_ms']:9.2f}  {row['mean_retrieval_ms']:12.2f}")
    plt.plot(sizes, [r["mean_upload_ms"] for r in summary], marker="o", label="upload")
    plt.plot(sizes, [r["mean_retrieval_ms"] for r in summary], marker="o", label="retrieval")
    plt.xlabel("file size (bytes)"); plt.ylabel("latency (ms)"); plt.legend(); plt.tight_layout(); plt.savefig(RESULTS / "upload_retrieval_latency.png", dpi=150)


if __name__ == "__main__": main()
