# Presentation Validation Report

## Deliverable

- PowerPoint: `Fault-Tolerant-P2P-Distributed-Storage-System.pptx`
- Notes: `presentation_notes.md` (25 slide sections; 82–104 words per slide)
- References: `presentation_references.md`
- Editable technical diagrams: native PowerPoint shapes on slides 9, 11, 12, 14–18
- Supporting assets: `diagrams/` and `images/`

## Checks performed

- Confirmed that the PPTX exists and opens through `python-pptx` parsing.
- Confirmed exactly 25 slides and approximately 16:9 dimensions (13.333 × 7.5 inches).
- Confirmed all slides contain text and the title slide includes the required project title and student/institution placeholders.
- Confirmed all slide shapes lie within the slide boundaries; no out-of-bounds shapes were found.
- Confirmed speaker notes contain sections for all 25 slides, each between 80 and 140 words.
- Confirmed three original generated illustrations are embedded in the deck and their PNG/SVG source files exist in `images/`.
- Confirmed the diagram asset files exist and correspond to implementation flows; the principal PowerPoint diagrams use editable native shapes.
- Checked cited official URLs for Flask, SQLite, Python sockets, NIST AES/SHA standards, and PyCryptodome. Project-specific statements are attributed to the inspected repository files.
- Inspected the generated network illustration. The architecture illustration shows the configured three nodes and coordinator-mediated paths.

## Repository findings reflected in the deck

- Flask routes: `POST /files`, `GET /files/<file_id>`, and `GET /status`.
- SQLite tables: `files`, `chunks`, `nodes`, `replicas`, and `audit_log`.
- N1 and N2 begin ACTIVE; N3 begins STANDBY; replication factor is 2.
- Chunk size is 1 MiB. AES-256-GCM stores nonce, ciphertext, and tag together; SHA-256 checks encrypted chunk bytes; the Merkle root is built over encrypted chunks.
- Heartbeats are configured for 1 second and the stale ACTIVE-node timeout is 4 seconds. The detector ignores nodes before their first heartbeat.
- Recovery attempts to copy affected chunks from a surviving replica, updates a mapping after STORE acknowledgement, and promotes the standby. Promotion does not guarantee every affected chunk was repaired.
- Audit entries link event, timestamp, and prior hash. The repository includes component tests for Merkle and audit tampering.
- The previous audit reported 11 unit tests passing. Tests were not rerun for this presentation.
- Benchmark scripts and end-to-end failure recovery remain unexecuted; no metrics or result charts are claimed.

## Checks unavailable or not performed

- No PowerPoint, LibreOffice, or PDF slide-rendering tool was available, so the complete deck was not exported to page images for visual inspection. Layout was checked by shape bounds and content sizing; supporting artwork was visually inspected separately.
- `python-pptx` does not author native presenter notes reliably in this workflow. Notes are provided in `presentation_notes.md` and are not embedded in the PPTX.
- Text clipping and visual overlap cannot be fully ruled out without a rendered-slide review.

## Remaining placeholders and limitations

Student, roll number, department, institution, guide, academic year, and acknowledgements remain placeholders. Fill them with verified details before submission. Performance benchmarks and end-to-end fault-recovery experiments remain future work. The deck describes the inspected prototype, not a production-grade storage service.
