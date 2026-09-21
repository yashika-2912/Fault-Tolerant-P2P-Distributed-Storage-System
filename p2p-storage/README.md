# Fault-Tolerant P2P Distributed Storage System

This is a local educational distributed-storage prototype. A Flask coordinator encrypts a file, splits it into 1 MiB chunks, stores each encrypted chunk on two TCP storage nodes, and records metadata in SQLite. A third node is a standby; the coordinator detects a missed heartbeat, promotes it, and copies replicas from the survivor.

It is not a production P2P system: the static AES key, local SQLite database, unauthenticated protocol, and lack of deletion/garbage collection are intentional limitations.

## Prerequisites and clean setup

Use Python 3.10+ and a virtual environment. From a clean clone:

```bash
cd p2p-storage
python3 -m venv .venv
. .venv/bin/activate                 # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest -q
```

The requirements file lists every non-standard runtime/test dependency: Flask, PyCryptodome, Requests, Matplotlib, and pytest. Generated node data, SQLite databases, virtual environments, benchmark CSVs, and plots are ignored.

## Run the system

Use four terminals from the repository root, with the environment activated:

```bash
python coordinator/app.py
python node/node_process.py --node-id N1 --port 6001
python node/node_process.py --node-id N2 --port 6002
python node/node_process.py --node-id N3 --port 6003
```

The coordinator HTTP API is `http://127.0.0.1:5000`; heartbeat traffic uses TCP port 6100. Nodes use ports 6001–6003. Wait briefly for heartbeats, then:

```bash
python client/cli_client.py upload path/to/file
python client/cli_client.py download FILE_ID recovered-file
python client/cli_client.py status
```

The HTTP equivalents are `POST /files` (multipart field `file`), `GET /files/<file_id>`, and `GET /status`.

## Verification and benchmarks

Run unit tests with `pytest -q`. To demonstrate recovery, upload a file, stop N1, wait a little more than the 4-second heartbeat timeout, then download with the same file ID. N3 is promoted and receives N1's replicas.

The benchmark commands start and clean up their own coordinator and nodes. Ensure no manually started copy occupies ports 5000, 6001–6003, or 6100:

```bash
python experiments/bench_upload_retrieval.py
python experiments/bench_failure_recovery.py
```

They print measured summaries and write raw CSV, aggregate CSV, and PNG plot files under `experiments/results/`. Matplotlib uses the headless `Agg` backend.

| Parameter | Value |
| --- | --- |
| Chunk size | 1 MiB |
| Replication factor | 2 |
| Heartbeat interval / timeout | 1 s / 4 s |
| Encryption | AES-256-GCM, random 12-byte nonce, 16-byte tag |
| Integrity | SHA-256 hashes and an odd-leaf-duplicating Merkle root |
| Placement | SHA-256 chunk-ID prefix modulo sorted active nodes |

See [the design document](docs/DESIGN_DOCUMENT.md) for architecture and limitations.
