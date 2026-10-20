"""Locked demo parameters, with a database override for isolated runs."""

import os

HEARTBEAT_INTERVAL = 1
HEARTBEAT_TIMEOUT = 4
COORDINATOR_PORT = 6100
CHUNK_SIZE = 1 * 1024 * 1024
REPLICATION_FACTOR = 2
# Static pre-shared 32-byte demo key — replace via env var before real runs.
AES_KEY = b"0123456789abcdef0123456789abcdef"
NODE_PORTS = [6001, 6002, 6003]
DB_PATH = os.environ.get("P2P_DB_PATH", "coordinator/metadata.db")
