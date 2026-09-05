"""Day-1 locked parameters from the design document."""

HEARTBEAT_INTERVAL = 1
HEARTBEAT_TIMEOUT = 4
CHUNK_SIZE = 1 * 1024 * 1024
REPLICATION_FACTOR = 2
# Static pre-shared demo key — replace via env var before real runs.
AES_KEY = b"DAY1_DEMO_KEY_PLACEHOLDER"
NODE_PORTS = [6001, 6002, 6003]
DB_PATH = "coordinator/metadata.db"
