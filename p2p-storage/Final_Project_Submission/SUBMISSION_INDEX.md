# Final Project Submission Index

Project: Fault Tolerant P2P Distributed Storage System

- 01_Final_Presentation/Fault_Tolerant_P2P_Distributed_Storage_System.pptx — 24-slide widescreen deck.
- 01_Final_Presentation/presentation_notes.md — slide notes and viva terms.
- 01_Final_Presentation/diagrams/ — architecture and workflow PNG/SVG.
- 03_Data_Associated_For_The_Paper/ — CSV schemas, inventory, manifest, JSON environment, methodology, limitations, raw-results folder, `analysis/analyze_benchmarks.py`, and header-only `analysis/benchmark_summary.csv`. No fabricated measurement rows or plots.
- 04_Implementation_Manual/Implementation_Manual.docx and .pdf — equivalent 20-chapter manuals.
- Manual README, configuration reference, troubleshooting, diagrams.

Prior repository audit reported 11 unit tests passing. They were not rerun here. Benchmark and end-to-end fault-recovery experiments remain unexecuted. No plots are appropriate without measured data. Personal fields are placeholders. Static demo key, missing auth/TLS, single coordinator/SQLite, and no automatic node reintegration are known limits.

`validation_report.json` records automated structural checks. `generate_submission.py` is the reproducible artifact generator; its isolated tool environment is stored in `.docenv/`.
