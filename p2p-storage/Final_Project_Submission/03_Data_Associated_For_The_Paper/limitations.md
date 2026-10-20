# Limitations

- All services ran on one Windows machine over loopback; results do not characterize a multi-host network.
- Three repetitions per payload size and three identical N1 failures provide a small sample.
- Latencies include client, Flask, chunking, encryption, SQLite, TCP and scheduler overhead.
- The harness omitted per-trial UTC timestamps, resource utilization and input checksums; these are not fabricated.
- Failure times use 100 ms status polling. A zero sampled promotion interval means state changes appeared in the same polling cycle, not necessarily zero internal work.
- Only single N1 process termination with a 16 KiB file was tested. Partitions, simultaneous failures, restart/reintegration and sustained load were not tested.
- Corruption testing showed rejection/fallback retrieval; corrupted replica repair was not observed.
- Two replicas were verified only for tested chunks; this does not prove general durability or availability. Replication is not a backup.
- Key-management security, hostile tampering, scalability and production deployment were not evaluated. Unit tests previously reported as 11 passed were not rerun here.
