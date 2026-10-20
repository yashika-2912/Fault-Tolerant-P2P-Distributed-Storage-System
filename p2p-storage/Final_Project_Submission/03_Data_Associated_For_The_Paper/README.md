# Experimental data package

This package contains genuine observations from the isolated project run `isolated_project_20261021_000718`. The upload/download harness ran four sizes (102,400; 1,048,576; 5,242,880; 10,485,760 bytes) with three trials each. All 12 uploads and downloads returned successfully and matched the original in-memory payload byte for byte. The controlled N1 failure harness ran three trials. A separate corruption probe altered one encrypted primary chunk only in the isolated copy and verified alternate-replica retrieval.

## Files

`benchmark_results.csv`, `upload_results.csv`, `download_results.csv`, `fault_tolerance_results.csv`, `integrity_verification_results.csv`, and `replication_results.csv` contain observations. `test_file_manifest.csv` documents ephemeral payload generation; payloads were not retained and their original checksums were not captured. `environment_details.json` records known environment information. `experimental_results.xlsx` mirrors the tables. `analysis/benchmark_summary.csv` has means, medians and sample standard deviations. `plots/` contains charts generated only from these measurements. `dataset_inventory.csv` indexes the data. Exact raw harness CSV/JSON output and isolated databases/chunks are under `raw_results/`.

## Measurement definitions

Request latency is `time.perf_counter()` elapsed around synchronous Python Requests calls to `POST /files` or `GET /files/<file_id>`. Throughput is effective client-observed decimal Mbps: `file_size_bytes × 8 / (elapsed_ms / 1000) / 1,000,000`; it includes HTTP, coordinator, crypto, SQLite, TCP and local scheduling costs and is not link capacity. Each transfer trial is success only after byte-for-byte comparison. Error bars show sample standard deviation across three trials. Failure status was polled every 100 ms, so detection/recovery boundaries are sampling approximations.

## Reproduction and safety

The repository scripts write to `experiments/results`, delete their named SQLite database files, and node processes write under `node_data`. Run only in a disposable copy after checking ports 5000, 6001–6003 and 6100 are free. The retained copy is under `raw_results/isolated_project_20261021_000718`.

## Evidence and limitations

Post-run inspection confirmed two copies for each of 51 benchmark chunks on N1/N2, with file bytes matching SQLite SHA-256 metadata. Each of three failure runs ended with N1 DOWN, N3 ACTIVE and replicas mapped to N2/N3; chunk files and hashes were checked and retrieved content matched. One corruption case detected the altered N1 chunk and returned original bytes from the alternate N2 copy. The corrupted copy was not repaired. Prior repository audit reported 11 unit tests passed; they were not rerun during this data collection. Runs were on one Windows host via loopback and are not production or multi-host benchmarks. The original harness did not record per-trial UTC timestamps; these fields are blank.
