# Raw results

`upload_retrieval_raw.csv` and `failure_recovery_raw.csv` are direct harness outputs; `integrity_probe.json` is the controlled corruption record. The isolated project workspace contains separate SQLite databases, temporary node chunks and logs. It is retained as raw experiment evidence. An earlier probe attempt failed while logging due to import path and is inconclusive; it is excluded from result tables. The successful retry used `integrity_probe_retry.db`.
