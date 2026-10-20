# Speaker Notes

> Presenter notes are stored in this Markdown file. They are not embedded in the PPTX because python-pptx does not provide reliable native notes-slide authoring.

## Slide 01 — Title Slide

Introduce this as an educational prototype for studying reliable file storage, not as a production platform. Its design combines a Flask API, SQLite metadata, and local TCP storage-node processes. The repository configures N1 and N2 as active and N3 as standby. The subtitle states the project’s design motivation, not an experimental result. Leave every personal field unchanged until accurate student and institution details are supplied. The hero graphic is original vector-style artwork; it summarizes networked storage but should not be mistaken for a screenshot or a live deployment.

**Presenter handoff:** Presentation Overview

## Slide 02 — Presentation Overview

Use this roadmap to tell the evaluation panel how the argument will proceed. First establish the storage problem and goals. Then explain the current design and implementation, including how data moves and how integrity is checked. Finally, distinguish component test evidence from the unexecuted performance and end-to-end recovery experiments. The sequence matters: mechanisms are introduced before any claim about their evidence. Transition by asking what new coordination challenges appear when data is spread among machines rather than placed on a single disk.

**Presenter handoff:** Introduction to Distributed Storage Systems

## Slide 03 — Introduction to Distributed Storage Systems

A distributed storage system places data across computers and presents a service to clients. It can provide a path to expand capacity or use multiple resources, but distribution alone does not create reliability. A node may fail, messages may be delayed, and coordination metadata may become unavailable. Replication creates alternate copies but consumes additional space and network bandwidth. This project is a small local prototype for investigating storage, monitoring, integrity, and recovery together. Emphasize that these mechanisms need explicit design and verification; distribution by itself does not guarantee availability, confidentiality, or correctness.

**Presenter handoff:** Problem Statement

## Slide 04 — Problem Statement

The central problem is that a file with only one accessible copy can become unavailable when its host fails. Once copies are distributed, the system also needs metadata that identifies which node has which chunk, monitoring that estimates node availability, and a recovery procedure that can use a surviving copy. Integrity matters because a returned file must be checked, not merely fetched. The illustration is a conceptual one-node-loss scenario. In the implementation, downloads try replica mappings and skip nodes marked DOWN, but no live end-to-end failure run was conducted for this presentation.

**Presenter handoff:** Objectives of the Project

## Slide 05 — Objectives of the Project

These four objective groups explain what the project set out to explore. Storage objectives correspond to the implemented upload and download routes and chunking. Reliability objectives map to factor-two placement, heartbeats, and a standby repair routine. Security and integrity objectives map to AES-GCM, SHA-256, Merkle roots, and a hash-linked audit table. Evaluation objectives require more than code: tests and experiments must be run and their evidence retained. The previous audit reported eleven unit tests passing, but the benchmark harnesses and full recovery scenario remain unexecuted. Later slides will make that status explicit.

**Presenter handoff:** Existing Approaches and Their Trade-offs

## Slide 06 — Existing Approaches and Their Trade-offs

This comparison describes general trade-offs, not a claim that centralized storage cannot be redundant. Centralized services can employ replication and high availability, though their control plane may remain an operational dependency. Distributed storage without replication spreads data but may lose access to a portion when a node fails. Replication adds alternate copies with extra capacity and coordination cost. This project demonstrates selected mechanisms on one host and does not benchmark against commercial platforms. Use the table to motivate the design rather than to claim superiority over existing systems.

**Presenter handoff:** Proposed System

## Slide 07 — Proposed System

The proposed system uses Flask routes for the client-facing API, a coordinator workflow that accesses SQLite metadata, and TCP requests to storage nodes. The configuration defines three nodes, two active at startup and one standby, with a replication factor of two. Data is split into 1 MiB chunks and AES-GCM encrypted before storage. SHA-256 and Merkle checks support verification, while heartbeats trigger a repair attempt after an active node becomes stale. These features are present in code. Whether recovery is complete for a particular failure depends on a surviving copy and successful node communication.

**Presenter handoff:** Functional and Non-Functional Requirements

## Slide 08 — Functional and Non-Functional Requirements

Functional requirements define operations the application exposes: upload, download, status inspection, and TCP chunk storage. Quality requirements describe properties we want, such as integrity detection and availability after a selected failure. The source implements mechanisms that address some of those requirements, but implementation presence is not equivalent to proven quality. The prior unit suite provides selected component evidence. There is no measured throughput, recovery latency, or fault-success rate. Explain the badges as evidence categories: code present, unit-tested behavior, and still requiring system-level verification.

**Presenter handoff:** High-Level System Architecture

## Slide 09 — High-Level System Architecture

Read this architecture by following the data plane and the control plane separately. The client reaches Flask at HTTP port 5000. The coordinator applies the storage workflow, consults SQLite, and sends length-prefixed JSON TCP STORE or FETCH requests to node ports 6001 through 6003. Heartbeats use a separate TCP listener on port 6100. N1 and N2 start ACTIVE, while N3 starts STANDBY. Recovery uses the coordinator to fetch a surviving copy and store it on the standby. Despite the project title, the inspected code has no peer discovery or node-to-node coordination; nodes are controlled by the coordinator.

**Presenter handoff:** Major Modules and Source Responsibilities

## Slide 10 — Major Modules and Source Responsibilities

The module map uses actual repository files. The Flask routes are in coordinator/app.py; upload and retrieval orchestration are in coordinator/storage.py. SQLite schema and metadata helpers are in db.py. TCP framing and requests live in node_client.py, and node_process.py implements the storage server and heartbeat sender. The data and integrity helpers are chunking.py, crypto.py, merkle.py, and audit.py. heartbeat_monitor.py marks stale ACTIVE nodes DOWN and invokes recovery.py. Connect these modules verbally as a call path rather than implying each is an independently deployed service.

**Presenter handoff:** File Upload and Storage Workflow

## Slide 11 — File Upload and Storage Workflow

The upload endpoint expects multipart field file at POST /files. The handler passes its bytes to upload_bytes, which requires at least two ACTIVE nodes. It chunks at one MiB, encrypts each chunk with AES-GCM, calculates the Merkle root over encrypted chunks, and derives a deterministic pair of destinations. The coordinator sends each encrypted blob to both nodes and waits for acknowledgements. It writes file, chunk, replica, and audit metadata only after all replica writes acknowledge. A mid-upload failure can leave an orphaned node file, but the incomplete upload is not made visible in metadata.

**Presenter handoff:** File Retrieval and Reconstruction

## Slide 12 — File Retrieval and Reconstruction

Retrieval begins at GET /files/<file_id>. Metadata gives the ordered chunks and candidate replica locations. For each chunk, the coordinator skips nodes marked DOWN, fetches from another candidate, and compares the encrypted bytes against the stored SHA-256 digest. It then decrypts and authenticates with AES-GCM. After the chunk loop it recomputes the Merkle root over the encrypted chunks, reassembles plaintext in order, checks original size, and appends an audit event. Missing usable replicas or failed authentication or verification cause an error response instead of returning a reconstructed file.

**Presenter handoff:** Chunking, Encryption, and Integrity Processing

## Slide 13 — Chunking, Encryption, and Integrity Processing

Chunking creates pieces of at most 1 MiB; a final partial chunk is kept as-is, and an empty file yields no chunks. Each chunk uses AES-256-GCM with a random 12-byte nonce and 16-byte tag. The implementation stores nonce, ciphertext, and tag together. SHA-256 is computed over encrypted chunk bytes and compared during retrieval. The Merkle root aggregates those encrypted bytes’ digests. These mechanisms have different jobs: encryption provides confidentiality, GCM also authenticates ciphertext, and hashing supports comparison. The demo key is hard-coded in source, so this setup is not suitable for protecting real user data.

**Presenter handoff:** Replication and Deterministic Data Placement

## Slide 14 — Replication and Deterministic Data Placement

Placement is deterministic: the implementation hashes the chunk identifier, uses the first eight digest bytes as a big-endian integer, and takes the result modulo the sorted ACTIVE node count. The next circular node becomes the second destination. With the configured two ACTIVE nodes, each chunk is sent to both. The configured factor does not mean every copy is always healthy: a failed store, later disk loss, or stale metadata can reduce actual durability. Replication is also not backup. Accidental deletion or compromise can affect replicas together. Describe observed replica count only after inspecting actual metadata from a test run.

**Presenter handoff:** Heartbeat-Based Failure Detection

## Slide 15 — Heartbeat-Based Failure Detection

A node heartbeat loop attempts to connect to the coordinator every second, sends a framed heartbeat, and expects an acknowledgement. The coordinator records its own receive time to avoid node-clock skew. For ACTIVE nodes with a recorded heartbeat, the detector marks status DOWN when the last arrival is more than four seconds old. A node that has not sent any heartbeat is ignored until its first message. This is a timeout suspicion, not proof of permanent failure: network delay, packet loss, or coordinator trouble can look similar. These are configured thresholds, not measured detection times.

**Presenter handoff:** Standby Recovery and Replica Repair

## Slide 16 — Standby Recovery and Replica Repair

Recovery is called after the detector marks an ACTIVE node DOWN. The routine selects a node with STANDBY status, finds chunk mappings on the failed node, and searches for a surviving mapped replica that is not DOWN. It fetches the chunk and stores it on the standby. Only after a successful STORE acknowledgement does it replace the failed mapping. The routine then marks the standby ACTIVE and records the result. It can promote the standby even if some affected chunks were not repaired, so promotion is not proof of complete restoration. Treat the final arrangement as expected behavior until an end-to-end experiment verifies it.

**Presenter handoff:** Merkle-Tree Integrity Verification

## Slide 17 — Merkle-Tree Integrity Verification

The Merkle helper treats each encrypted chunk as a leaf hash, combines neighboring hexadecimal digests, and repeats until one root remains. If a level has an odd number of leaves, the last leaf is duplicated. The file metadata stores the resulting root, and downloads recompute it over fetched encrypted chunks. For four leaves, the first pair of parent hashes feeds a single root. The tree helps summarize integrity for the whole ordered collection, but this implementation does not provide partial proofs for retrieving only one branch. Existing unit tests verify deterministic roots and detection of a changed chunk.

**Presenter handoff:** Hash-Linked Audit Log

## Slide 18 — Hash-Linked Audit Log

Audit rows contain an event, timestamp, predecessor hash, and current hash. The genesis predecessor is a string of zeroes. Each next digest is computed over canonical JSON containing its event, previous hash, and timestamp. Verification walks the rows in insertion order and recomputes every link. A repository unit test alters an earlier event and checks that verification fails. The chain can reveal inconsistent edits when verification state is trusted, but it is not an immutable external ledger. Someone able to rewrite the database and all trusted references could recompute the chain.

**Presenter handoff:** Implementation and Technology Stack

## Slide 19 — Implementation and Technology Stack

The technology stack lists actual project dependencies and imports. Python is the implementation language. Flask supplies HTTP routes; SQLite stores local metadata; Python TCP sockets carry node and heartbeat messages. PyCryptodome implements AES-GCM, while hashlib provides SHA-256. Requests is used by the CLI; pytest is the test framework; Matplotlib is used by benchmark scripts. The repository contains no Docker, Kubernetes, Redis, or cloud deployment configuration. Loopback addresses and fixed ports make the deployment a local simulation, so do not describe it as a tested multi-host cluster.

**Presenter handoff:** Testing Strategy and Verified Test Result

## Slide 20 — Testing Strategy and Verified Test Result

The previous repository audit reported eleven passing unit tests. The inspected test suite covers chunking, crypto round trips and tampering, placement, SQLite schema, Merkle roots, audit tampering, and stale-heartbeat status changes. This is useful component-level evidence. It does not demonstrate a complete networked upload/download after a real node failure, and it does not establish performance. We did not rerun tests as part of this presentation task. The benchmark and failure-recovery harnesses exist but remain unexecuted. Do not infer coverage percentages or successful recovery scenarios from unit tests.

**Presenter handoff:** Experimental Evaluation Methodology

## Slide 21 — Experimental Evaluation Methodology

This is a proposed measurement plan rather than a result slide. Upload and download latency should be timed around successful client requests, with file size and repetitions recorded. Throughput can be expressed as successfully transferred bytes divided by elapsed time. Replication overhead compares additional replica bytes with original size. Detection time should measure node-stop to DOWN status; repair time should separately measure the repair phase and promotion. A sound study records trial counts, workload sizes, hardware, software, and network setup, and retains failed trials. No measurements are currently available, so formulas are provided without values.

**Presenter handoff:** Results and Current Implementation Evidence

## Slide 22 — Results and Current Implementation Evidence

This evidence matrix separates what source code implements from what tests or experiments establish. The previous audit reported eleven unit tests passing, while code inspection confirms upload/download, cryptography, metadata, heartbeat, Merkle, audit, and repair components exist. The test report is limited to unit cases and does not prove production reliability. No benchmark data or end-to-end failover outcomes are available. Use the amber and gray statuses for those gaps; do not turn them into green claims. The most important academic point is transparent evidence: mechanism, verification scope, and unmeasured outcomes should be stated separately.

**Presenter handoff:** Limitations and Future Enhancements

## Slide 23 — Limitations and Future Enhancements

Discuss limitations as architectural constraints or open evaluation questions. The system has one coordinator and one local SQLite database, local loopback defaults, no peer discovery or consensus, and no network authentication or TLS. The configured key is a demo constant. Recovery assumes a surviving replica and standby; failed chunks may remain unrepaired even when the standby is promoted. A restarted DOWN node is not automatically reintegrated. Future work should run isolated benchmarks and controlled failure scenarios, then examine concurrent failures, partitions, replica consistency, key provisioning, and multi-host deployment. Do not present proposed work as already complete.

**Presenter handoff:** Conclusion and Project Contribution

## Slide 24 — Conclusion and Project Contribution

Summarize the project as an integrated prototype: Flask upload and retrieval, encrypted 1 MiB chunks over TCP, SQLite metadata, deterministic two-node placement, SHA-256 and Merkle checks, hash-linked audit events, and heartbeat-triggered repair logic. The prior unit-test result gives initial evidence for selected components. The project has not yet quantified throughput, recovery time, or end-to-end fault tolerance. The balanced conclusion is that the code provides a platform for studying resilience mechanisms, while a controlled evaluation remains necessary before claiming measured availability, performance, or production security. Close by inviting questions about design assumptions and evidence.

**Presenter handoff:** References and Acknowledgements

## Slide 25 — References and Acknowledgements

The references are authoritative documentation for the frameworks and cryptographic standards actually discussed. The project README, configuration, source files, and test suite are primary evidence for implementation-specific details. NIST FIPS 197 specifies AES, and FIPS 180-4 specifies SHA-256 among the Secure Hash Standard algorithms. Flask, SQLite, Python socket, and PyCryptodome documentation support descriptions of those tools. The custom illustrations were generated for this deck and use no external photographs or downloaded artwork. Leave acknowledgements as placeholders until accurate names are provided, then close with thanks and invite technical questions.

**Presenter handoff:** Invite questions and discussion.

## Viva prompts

- What is the difference between replication and backup?
- Why is failure detection a suspicion rather than proof?
- What do AES-GCM, SHA-256, and the Merkle root each contribute?
- What does the previous unit-test result establish, and what does it not establish?
- Which controlled experiment should be run first, and what evidence should be retained?
