# Configuration reference

| Name | Value/source |
|---|---|
| HEARTBEAT_INTERVAL | 1 s, config.py |
| HEARTBEAT_TIMEOUT | 4 s, config.py |
| COORDINATOR_PORT | 6100, config.py |
| HTTP port | 5000, app.py |
| CHUNK_SIZE | 1 MiB |
| REPLICATION_FACTOR | 2 |
| AES_KEY | Static demo key in source; do not expose/use for sensitive data |
| NODE_PORTS | 6001, 6002, 6003 |
| DB_PATH | coordinator/metadata.db; P2P_DB_PATH override |
| Node CLI | --node-id, --port required; --coordinator-host/port optional |

There are no environment overrides for other constants.
