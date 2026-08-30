# Fault-Tolerant P2P Distributed Storage System with Automatic Replica Recovery

## Abstract
A fault-tolerant peer-to-peer (P2P) distributed storage prototype that combines heartbeat-based
failure detection and automatic standby promotion, chunk-level Merkle-tree integrity verification
over AES-encrypted, SHA-256-hashed chunks, and a lightweight hash-chained tamper-evident audit
log — without relying on blockchain consensus.

## Problem Statement
Traditional storage nodes suffer unannounced crashes (single points of failure) and uncoordinated
outages that orphan data chunks without triggering failover. Whole-file hashing cannot isolate a
specific corrupted chunk, forcing full-file re-downloads. Conventional database-backed recovery
logs can be modified or deleted after the fact, undermining auditability.

## Proposed Solution
A hybrid architecture: a centralized Flask/SQLite metadata coordinator paired with a decentralized
P2P data plane (Python TCP sockets) across a 3-node cluster (2 active + 1 standby). Chunks are
deterministically placed via `hash(chunk_id) mod N` with a replication factor of 2. On heartbeat
failure detection, the standby node is automatically promoted and the failed node's chunks are
re-synchronized and Merkle-verified. Recovery and integrity events are recorded in a SHA-256
hash-chained audit log.

## Architecture
See `docs/architecture.drawio` (draw.io source) and the compiled `architecture.png`, referenced
as Fig. 1 in `docs/first_review.pdf`. Components: Web Client → Flask API Server → SQLite Metadata
DB + P2P Data Network (Node 1 Active, Node 2 Active, Node 3 Standby) → Failure Detection
(Heartbeat) → Standby Promotion → Replica Recovery → Integrity Audit module.

## Technologies Used
| Feature | Technology |
|---|---|
| File Upload & Retrieval | HTML, CSS, JavaScript |
| API Request Processing | Python, Flask |
| Metadata Management | SQLite |
| P2P Communication | Python TCP Sockets |
| Distributed Storage | 3-Node P2P Cluster (2 Active, 1 Standby) |
| File Chunking & Encryption | Python, AES |
| Integrity Verification | SHA-256, Merkle Tree |
| Failure Detection | Heartbeat Monitoring |
| Standby Promotion | Python Failover Logic |
| Audit & Traceability | Hash-Chained Audit Log |

## Project Structure
```
project/
├── README.md
├── docs/
│   ├── first_review.pdf
│   ├── architecture.drawio
│   └── presentation.pptx
├── src/
│   ├── api/            # Flask API server, routes, request handling
│   ├── node/            # P2P storage node (socket server, heartbeat, chunk store)
│   ├── coordinator/     # Failure detection, standby promotion, recovery logic
│   ├── integrity/       # AES encryption, SHA-256 hashing, Merkle tree
│   └── audit/           # Hash-chained audit log
├── experiments/
│   ├── test_cases.md    # TC-01 .. TC-05
│   └── results/         # Raw experiment outputs (logs, timings)
├── graphs/
│   ├── upload_retrieval_latency.png
│   ├── failure_recovery_time.png
│   └── chunk_availability.png
├── requirements.txt
└── overleaf/
    └── main.tex          # First-review IEEE paper source
```
[TO BE FILLED: adjust the above structure to match the actual repository layout.]

## Installation
```
git clone [GITHUB REPO URL]
cd project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to Run
```
# Start the 3 storage nodes (2 active + 1 standby)
python src/node/node.py --id 1 --role active
python src/node/node.py --id 2 --role active
python src/node/node.py --id 3 --role standby

# Start the Flask coordinator/API
python src/api/app.py
```
[TO BE FILLED: exact ports, config file, and startup order once finalized.]

## Experimental Setup
3-node cluster (2 active, 1 standby) run as separate Python processes on a local/LAN test
environment, coordinated by a single Flask instance. Test cases TC-01–TC-05 cover upload/
placement, heartbeat failure detection, automatic replica recovery, Merkle integrity verification
on retrieval, and audit-log tamper detection.

## Results
[ACTUAL UPLOAD LATENCY], [ACTUAL RETRIEVAL LATENCY], [ACTUAL RECOVERY TIME],
[ACTUAL AVAILABILITY %] — to be filled in from executed test runs (see `experiments/results/`).

## Performance Analysis
Upload latency is expected to scale with file size due to chunking, AES encryption, SHA-256
hashing, and multi-node socket transfer overhead; recovery duration scales with the number of
chunks owned by the failed node. See Section III of `docs/first_review.pdf` for details, to be
updated with measured figures.

## Team Members
- Yashika V — 2024503008
- Ashwinee S S — 2024503066
- Sandhiya K — 2024503028

B.E. Computer Science and Engineering, Madras Institute of Technology, Anna University, Chennai.
Academic Year 2024–2025.

## References
See the References section of `docs/first_review.pdf` for the full IEEE-formatted list
(12 references, prioritizing IEEE ICC, GLOBECOM, and CCNC publications).

## GitHub / Project Repository
[GITHUB REPO URL TO BE FILLED]
