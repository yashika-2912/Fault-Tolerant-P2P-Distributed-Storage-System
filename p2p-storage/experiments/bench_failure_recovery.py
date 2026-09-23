"""Measure actual heartbeat detection and replica-recovery latency."""

import argparse
import csv
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "experiments" / "results"


def wait_http(seconds: float = 15) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if requests.get("http://127.0.0.1:5000/status", timeout=.5).ok: return
        except requests.RequestException: pass
        time.sleep(.1)
    raise RuntimeError("coordinator did not start")


def port_released(port: int, seconds: float = 5) -> bool:
    """Confirm a terminated node really released its TCP port before relaunch."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0: return True
        time.sleep(.1)
    return False


def start_stack(db_path: Path) -> list[subprocess.Popen]:
    env = {**os.environ, "P2P_DB_PATH": str(db_path)}
    commands = [[sys.executable, "coordinator/app.py"], *[[sys.executable, "node/node_process.py", "--node-id", f"N{i}", "--port", str(6000+i)] for i in range(1,4)]]
    processes = [subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for command in commands]
    wait_http(); time.sleep(1.2)
    return processes


def stop_stack(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None: process.terminate()
    for process in processes:
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait()


def status() -> dict[str, dict]:
    return {node["node_id"]: node for node in requests.get("http://127.0.0.1:5000/status", timeout=2).json()["nodes"]}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--trials", type=int, default=3); args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True); rows = []
    for trial in range(1, args.trials + 1):
        db_path = RESULTS / f"failure_recovery_trial_{trial}.db"
        if db_path.exists(): db_path.unlink()
        processes = start_stack(db_path)
        try:
            payload = os.urandom(16384)
            uploaded = requests.post("http://127.0.0.1:5000/files", files={"file": ("recovery.bin", payload)}, timeout=30); uploaded.raise_for_status()
            file_id = uploaded.json()["file_id"]
            failure_start = time.perf_counter()
            processes[1].terminate(); processes[1].wait(timeout=5)
            if not port_released(6001): raise RuntimeError("N1 port was not released after terminate")
            detected_at = recovered_at = None
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                current = status()
                elapsed = (time.perf_counter() - failure_start) * 1000
                if current["N1"]["status"] == "DOWN" and detected_at is None: detected_at = elapsed
                if current["N3"]["status"] == "ACTIVE":
                    recovered_at = elapsed; break
                time.sleep(.1)
            if detected_at is None or recovered_at is None: raise RuntimeError("failure was not detected and repaired before deadline")
            restored = requests.get(f"http://127.0.0.1:5000/files/{file_id}", timeout=30); restored.raise_for_status()
            if restored.content != payload: raise RuntimeError("data was not retrievable after recovery")
            row = {"trial": trial, "detection_ms": detected_at, "recovery_ms": recovered_at, "repair_ms": recovered_at-detected_at}
            rows.append(row); print(f"trial {trial}: detection={detected_at:.2f} ms recovery={recovered_at:.2f} ms")
        finally:
            stop_stack(processes)
    with (RESULTS / "failure_recovery_raw.csv").open("w", newline="") as handle: writer=csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    summary = {"trials": len(rows), **{f"mean_{key}": sum(row[key] for row in rows)/len(rows) for key in ("detection_ms", "recovery_ms", "repair_ms")}}
    with (RESULTS / "failure_recovery_summary.csv").open("w", newline="") as handle: writer=csv.DictWriter(handle, fieldnames=summary); writer.writeheader(); writer.writerow(summary)
    plt.bar(["detection", "total recovery", "repair after detection"], [summary["mean_detection_ms"], summary["mean_recovery_ms"], summary["mean_repair_ms"]]); plt.ylabel("latency (ms)"); plt.tight_layout(); plt.savefig(RESULTS / "failure_recovery_latency.png", dpi=150)


if __name__ == "__main__": main()
