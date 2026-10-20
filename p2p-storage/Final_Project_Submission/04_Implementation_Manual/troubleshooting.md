# Troubleshooting

- Install requirements in activated virtualenv for import errors.
- Inspect port owners before startup; do not terminate unknown processes.
- Node missing: verify coordinator listener and node host/port, inspect GET /status.
- Upload 503: requires at least two ACTIVE nodes and successful STORE acknowledgments.
- Download error: verify replica metadata and node availability.
- AES authentication failure means bytes/key mismatch; do not treat SHA-256 as repair.
- Keep P2P_DB_PATH consistent across coordinator and isolated processes.
- Restarted DOWN nodes are not automatically reintegrated.
