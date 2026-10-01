# Fault-Tolerant P2P Distributed Storage System

> **Course Project -- Computer Networks**

A fault-tolerant distributed storage system designed to provide **automatic failure detection, standby-node promotion, selective replica recovery, data integrity verification, encryption, and tamper-evident audit logging** in a small peer-to-peer storage cluster.

---

## 1. Project Overview

Distributed storage systems must remain available even when individual storage nodes fail. This project implements a lightweight fault-tolerant storage architecture in which files are divided into chunks, replicated across multiple storage nodes, and automatically recovered when an active node fails.

The system uses a **3-node cluster** consisting of:

* **N1** — Active storage node
* **N2** — Active storage node
* **N3** — Standby node

A **replication factor of 2** is used so that each chunk has two copies distributed across the active nodes.

When an active node fails, the system:

1. Detects the failure using heartbeat monitoring.
2. Promotes the standby node.
3. Identifies only the chunks affected by the failed node.
4. Recovers the required replicas.
5. Verifies recovered chunks using SHA-256.
6. Updates the metadata mapping only after successful verification.
7. Maintains data availability during the recovery process.

The system also provides **AES-based chunk encryption, SHA-256 integrity verification, Merkle-tree based file integrity, and a hash-chained audit log**.

---

## 2. Objectives

The primary objectives of this project are:

* To design a fault-tolerant distributed storage system.
* To provide automatic storage-node failure detection.
* To minimize data loss during node failures.
* To automatically promote a standby node after failure.
* To recover only the replicas affected by a failed node.
* To use deterministic chunk placement for predictable replica mapping.
* To provide chunk-level encryption.
* To verify chunk integrity using SHA-256.
* To provide file-level integrity verification using Merkle trees.
* To maintain a tamper-evident audit trail.
* To evaluate upload, retrieval, failure detection, and recovery performance.

---

## 3. Key Features

### 3.1 Distributed File Chunking

Uploaded files are divided into fixed-size chunks.

Each chunk is assigned a unique identifier and processed independently for storage and replication.

This allows the system to:

* distribute large files across storage nodes,
* replicate individual chunks,
* recover only affected chunks,
* avoid unnecessarily reconstructing complete files.

---

### 3.2 Deterministic Chunk Placement

The system uses deterministic hash-based placement to determine where each chunk should be stored.

For a chunk `c`:

```text
p(c) = h(chunk_id) mod |A|
```

where:

* `h(chunk_id)` is the hash of the chunk identifier.
* `|A|` is the number of active storage nodes.
* `p(c)` determines the primary placement position.

With replication factor `R = 2`, the replica set is:

```text
M(c) = { A[p(c)], A[(p(c) + 1) mod |A|] }
```

This provides deterministic and predictable replica placement.

---

### 3.3 Replication

Every chunk is stored with two replicas.

Replication improves availability because the system can retrieve a chunk from another replica if one storage node becomes unavailable.

The system uses a centralized coordinator to maintain metadata about:

* files,
* chunks,
* replica locations,
* active nodes,
* node health,
* recovery state.

---

### 3.4 Heartbeat-Based Failure Detection

Active nodes periodically send heartbeat messages to the coordinator.

A node is considered failed when the time since its last successful heartbeat exceeds the configured timeout:

```text
t_now - t_last > τ
```

where:

* `t_now` = current time
* `t_last` = timestamp of the last heartbeat
* `τ` = failure-detection timeout

This enables automatic detection without requiring manual intervention.

---

### 3.5 Automatic Standby Promotion

The system maintains a standby node that can replace a failed active node.

When an active node `f` fails:

```text
A(t+1) = (A(t) \ {f}) ∪ {S}
```

where:

* `A(t)` = current active-node set
* `f` = failed node
* `S` = standby node

The standby node is promoted to maintain the required active storage capacity.

---

### 3.6 Selective Replica Recovery

The system does not unnecessarily recover every chunk after a node failure.

Instead, it identifies only the chunks whose replica mapping contains the failed node:

```text
C_f = { c ∈ C | f ∈ M(c) }
```

Only these affected chunks are resynchronized.

This reduces recovery overhead and improves recovery efficiency.

A replica mapping is updated only after the recovered chunk has been successfully copied and verified.

---

### 3.7 AES-Based Chunk Encryption

Before storage, chunks are encrypted using AES-based encryption.

Encryption is performed at the chunk level so that individual stored chunks are protected independently.

The architecture separates:

```text
File
  ↓
Chunks
  ↓
Encryption
  ↓
Integrity Hash
  ↓
Replication
  ↓
Storage Nodes
```

---

### 3.8 SHA-256 Integrity Verification

SHA-256 is used to generate integrity hashes for chunks.

During retrieval and recovery, the calculated hash can be compared with the expected hash.

Conceptually:

```text
Stored Hash = SHA-256(chunk)
Received Hash = SHA-256(retrieved chunk)

If Stored Hash == Received Hash
        → Chunk is valid
Else
        → Integrity failure
```

This prevents corrupted data from being silently accepted.

---

### 3.9 Merkle Tree Integrity Verification

The system maintains a Merkle tree for file-level integrity verification.

The SHA-256 hashes of individual chunks form the leaf nodes of the Merkle tree.

Parent nodes are calculated from pairs of child hashes:

```text
Parent = SHA-256(Left Hash || Right Hash)
```

If a level contains an odd number of hashes, the final hash is duplicated before calculating the next level.

The final hash at the root represents the integrity state of the complete file.

A change to any chunk propagates through the tree and results in a different Merkle root.

---

### 3.10 Tamper-Evident Audit Logging

Important system events are recorded in a hash-chained audit log.

Each audit entry depends on the hash of the previous entry:

```text
H_i = SHA-256(H_(i-1) || E_i)
```

The chain starts from a fixed genesis value.

This creates a tamper-evident sequence of events.

If an existing audit entry is modified or removed, subsequent hash relationships no longer match, allowing the system to detect tampering.

---

## 4. System Architecture

The project uses two logical planes.

### Control Plane

The control plane is implemented using:

* Flask
* SQLite
* Coordinator services

It manages:

* metadata,
* node status,
* heartbeat monitoring,
* replica mappings,
* failure detection,
* recovery,
* audit verification.

### Data Plane

The data plane uses:

* TCP sockets
* storage nodes
* chunk transfer operations

It handles:

* storing chunks,
* retrieving chunks,
* replication,
* node-to-coordinator data transfer.

### High-Level Architecture

```text
                         ┌─────────────────────┐
                         │       Client        │
                         │    CLI / REST API   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Coordinator     │
                         │      Flask API      │
                         ├─────────────────────┤
                         │ Metadata / SQLite   │
                         │ Placement           │
                         │ Heartbeat Monitor   │
                         │ Recovery            │
                         │ Merkle Verification│
                         │ Audit Log           │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │    N1    │    │    N2    │    │    N3    │
              │  Active  │    │  Active  │    │ Standby  │
              └──────────┘    └──────────┘    └──────────┘
                    │               │
                    └───────┬───────┘
                            │
                       Chunk Replicas
```

---

## 5. Data Flow

### Upload

```text
Client
  ↓
Flask Coordinator
  ↓
File Chunking
  ↓
AES Encryption
  ↓
SHA-256 Hashing
  ↓
Deterministic Placement
  ↓
Replica Storage
  ↓
Metadata Update
  ↓
Audit Entry
```

### Download

```text
Client
  ↓
Coordinator
  ↓
Locate Chunk Replicas
  ↓
Fetch Chunk
  ↓
SHA-256 Verification
  ↓
Decrypt Chunk
  ↓
Reconstruct File
  ↓
Return File
```

### Failure Recovery

```text
Active Node Failure
        ↓
Heartbeat Timeout
        ↓
Failure Detection
        ↓
Standby Promotion
        ↓
Identify Affected Chunks
        ↓
Recover Missing Replicas
        ↓
SHA-256 Verification
        ↓
Update Replica Mapping
        ↓
Recovery Complete
```

---

## 6. Communication Protocol

The system uses a lightweight TCP-based wire protocol.

Messages use a:

```text
4-byte big-endian length prefix
+
JSON payload
```

Supported message types include:

| Message         | Purpose                              |
| --------------- | ------------------------------------ |
| `STORE`         | Store a chunk on a node              |
| `STORE_ACK`     | Confirm successful storage           |
| `FETCH`         | Request a chunk                      |
| `FETCH_RESULT`  | Return requested chunk               |
| `HEARTBEAT`     | Report node liveness                 |
| `HEARTBEAT_ACK` | Confirm heartbeat                    |
| `REGISTER`      | Register a node with the coordinator |

The implementation uses short-lived TCP connections with a configured timeout. Store operations can be retried once if necessary, while retrieval can fall back to another replica.

---

## 7. REST API

The coordinator exposes the following endpoints.

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| `POST` | `/upload`             | Upload a file            |
| `GET`  | `/download/<file_id>` | Download a stored file   |
| `GET`  | `/status`             | View cluster/node status |
| `GET`  | `/recovery/status`    | View recovery status     |
| `GET`  | `/audit/verify`       | Verify the audit chain   |

---

## 8. Project Structure

```text
p2p-storage/
│
├── coordinator/
│   ├── app.py
│   ├── config.py
│   ├── chunking.py
│   ├── crypto.py
│   ├── merkle.py
│   ├── placement.py
│   ├── db.py
│   ├── node_client.py
│   ├── heartbeat_monitor.py
│   ├── recovery.py
│   ├── audit.py
│   └── storage.py
│
├── node/
│   └── node_process.py
│
├── client/
│   └── cli_client.py
│
├── tests/
│   ├── test_chunking.py
│   ├── test_crypto.py
│   ├── test_merkle.py
│   ├── test_placement.py
│   ├── test_recovery.py
│   └── test_merkle_audit.py
│
├── experiments/
│   ├── bench_upload_retrieval.py
│   ├── bench_failure_recovery.py
│   └── results/
│
├── node_data/
│
├── docs/
│   └── DESIGN_DOCUMENT.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 9. Technologies Used

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python                |
| REST API             | Flask                 |
| Metadata Store       | SQLite                |
| Node Communication   | TCP Sockets           |
| Serialization        | JSON                  |
| Encryption           | AES                   |
| Integrity Hashing    | SHA-256               |
| File Integrity       | Merkle Tree           |
| Audit Integrity      | SHA-256 Hash Chain    |
| Testing              | Python Test Framework |
| Version Control      | Git / GitHub          |

---

## 10. Installation

### Prerequisites

Install:

* Python 3.x
* Git
* pip

Clone the repository:

```bash
git clone <repository-url>
cd Fault-Tolerant-P2P-Distributed-Storage-System/p2p-storage
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Activate it on Linux/WSL:

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 11. Running the System

Start the coordinator:

```bash
python coordinator/app.py
```

Start the required storage-node processes using the node configuration:

```bash
python node/node_process.py
```

The client can then be used to interact with the storage system.

For the exact runtime configuration and node startup parameters, refer to:

```text
docs/DESIGN_DOCUMENT.md
```

---

## 12. Testing

The project contains unit tests for the major components.

Run the complete test suite from the project directory:

```bash
python -m pytest
```

The test suite covers areas including:

* chunking,
* cryptographic operations,
* Merkle-tree generation,
* deterministic placement,
* recovery,
* audit integrity.

---

## 13. Experimental Evaluation

The project evaluates the system using multiple test cases.

### TC-01 — Upload Performance

Measures upload latency for files ranging from:

```text
1 MB – 100 MB
```

Multiple repetitions are performed for each tested file size.

### TC-02 — Failure Detection

An active node is terminated and the time required for the coordinator to detect the failure is measured.

### TC-03 — Standby Promotion

Measures the time and correctness of promoting the standby node after an active-node failure.

### TC-04 — Replica Recovery

Measures the time required to recover replicas affected by the failed node.

### TC-05 — Retrieval and Integrity

Tests file retrieval and verifies the integrity of the retrieved data.

### TC-06 — Audit Tamper Detection

Modifies an audit-log entry and verifies that the hash chain detects the tampering.

---

## 14. Performance Metrics

The project evaluates:

* Upload latency
* Retrieval latency
* Failure-detection latency
* Recovery latency
* Availability
* Integrity verification correctness
* Audit tamper-detection correctness

Representative measurements documented for the project include:

| Metric            | Measured Value |
| ----------------- | -------------: |
| Upload latency    |        1879 ms |
| Retrieval latency |     1597.62 ms |
| Failure detection |     2712.01 ms |
| Recovery          |     1739.79 ms |
| Availability      |           100% |

These values are experimental results for the project implementation and environment rather than universal performance guarantees.

---

## 15. Fault Model and Scope

The current implementation focuses on a **single active-node crash failure model**.

### Supported

* Active storage-node failure
* Heartbeat-based failure detection
* Automatic standby promotion
* Selective replica recovery
* Chunk integrity verification
* File-level integrity verification
* Tamper-evident audit verification

### Outside the Current Scope

The following are intentionally outside the current project scope:

* Byzantine failures
* Network partitions
* Coordinator failover
* Failed-node rejoining and reconciliation
* Full peer-to-peer metadata coordination
* Distributed consensus
* Complete multi-failure recovery

These limitations keep the implementation focused on the project's primary fault-tolerance objectives.

---

## 16. Design Considerations

### Why Replication Factor = 2?

A replication factor of 2 ensures that each chunk has an additional copy, allowing the system to continue retrieving data when one storage node fails.

### Why Selective Recovery?

Recovering only the chunks affected by a failure reduces unnecessary data movement and avoids rebuilding unaffected replicas.

### Why Merkle Trees?

A Merkle tree provides a compact representation of the integrity state of an entire file while being constructed from chunk-level hashes.

### Why a Hash-Chained Audit Log?

A hash chain links every audit entry to the previous entry, making unauthorized modification of historical entries detectable.

### Why SQLite?

SQLite provides a lightweight metadata store suitable for the project's centralized coordinator and experimental deployment.

---

## 17. Security and Integrity Model

The project addresses data protection at multiple levels:

```text
                 ┌───────────────────────────┐
                 │      File Integrity        │
                 │       Merkle Root         │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │      Chunk Integrity       │
                 │          SHA-256           │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │       Data Protection      │
                 │       AES Encryption       │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │      Audit Integrity       │
                 │     SHA-256 Hash Chain     │
                 └───────────────────────────┘
```

---

## 18. Project Workflow

The implementation was developed incrementally through the following stages:

### Phase 1 — Core Distributed Storage

* Project architecture
* File chunking
* Encryption
* Hashing
* Deterministic placement
* Replica storage
* Coordinator metadata

### Phase 2 — Fault Tolerance

* Heartbeat monitoring
* Failure detection
* Standby promotion
* Replica recovery

### Phase 3 — Integrity and Audit

* Merkle-tree verification
* End-to-end integrity validation
* Tamper-evident audit logging

### Phase 4 — Testing and Evaluation

* Unit testing
* End-to-end testing
* Failure experiments
* Upload/retrieval benchmarking
* Recovery benchmarking

### Phase 5 — Documentation and Finalization

* Design documentation
* Experimental results
* Configuration finalization
* Repository cleanup
* Final validation


---

## 20. Future Enhancements

Potential future improvements include:

* Coordinator replication and failover
* Failed-node rejoin and reconciliation
* Network-partition handling
* Multi-node simultaneous failure recovery
* Distributed metadata management
* More scalable metadata storage
* Peer-to-peer data transfer
* Merkle proof-based partial verification
* Improved concurrency handling
* Larger cluster evaluation
* Dynamic replica-factor management
* Production-grade key management

---

## 21. Project Outcomes

This project demonstrates the practical implementation of several distributed-systems concepts:

* Distributed data storage
* Data replication
* Deterministic partitioning
* Fault detection
* Fault recovery
* Standby-node promotion
* Data integrity
* Cryptographic hashing
* Encryption
* Merkle trees
* Tamper-evident logging
* Client-server communication
* Performance evaluation

The project combines these concepts into a working storage-system prototype rather than implementing them as isolated demonstrations.

---

## 22. Documentation

Detailed design information is available in:

```text
docs/DESIGN_DOCUMENT.md
```

The design document covers the system architecture, algorithms, communication model, recovery workflow, integrity mechanisms, experiments, and implementation details
