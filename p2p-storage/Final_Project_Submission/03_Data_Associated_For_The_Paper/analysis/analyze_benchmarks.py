"""Summarize measured benchmark rows and plot latency only when data exist.

Run from any working directory with the documentation environment Python.
No synthetic or placeholder observations are created.
"""
from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmark_results.csv"
OUT = ROOT / "analysis"
PLOTS = ROOT / "plots"

with SOURCE.open(newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
valid = []
for row in rows:
    try:
        size = int(row["file_size_bytes"])
        upload = float(row["upload_time_ms"])
        download = float(row["download_time_ms"])
        if row["status"].lower() == "success" and size > 0 and upload > 0 and download > 0:
            valid.append((size, upload, download))
    except (KeyError, TypeError, ValueError):
        continue

summary_path = OUT / "benchmark_summary.csv"
with summary_path.open("w", newline="", encoding="utf-8-sig") as f:
    fields = ["file_size_bytes", "n_successful_trials", "mean_upload_ms", "median_upload_ms", "mean_download_ms", "median_download_ms"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for size in sorted({x[0] for x in valid}):
        group = [x for x in valid if x[0] == size]
        ups = [x[1] for x in group]
        downs = [x[2] for x in group]
        writer.writerow({"file_size_bytes": size, "n_successful_trials": len(group), "mean_upload_ms": statistics.mean(ups), "median_upload_ms": statistics.median(ups), "mean_download_ms": statistics.mean(downs), "median_download_ms": statistics.median(downs)})

if valid:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    PLOTS.mkdir(parents=True, exist_ok=True)
    sizes = sorted({x[0] for x in valid})
    means_up = [statistics.mean([x[1] for x in valid if x[0] == size]) for size in sizes]
    means_down = [statistics.mean([x[2] for x in valid if x[0] == size]) for size in sizes]
    plt.plot(sizes, means_up, marker="o", label="Upload")
    plt.plot(sizes, means_down, marker="o", label="Download")
    plt.xlabel("File size (bytes)")
    plt.ylabel("Mean latency (ms)")
    plt.title("Successful measured transfers")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS / "upload_download_latency.png", dpi=160)
    plt.close()
else:
    print("No valid successful observations; summary contains headers only and no plot was generated.")
