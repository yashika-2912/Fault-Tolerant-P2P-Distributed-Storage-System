"""Coordinator HTTP status application with heartbeat tracking."""

from flask import Flask, jsonify

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from coordinator.db import get_all_nodes, init_db
from coordinator.heartbeat_monitor import start_failure_detector, start_heartbeat_listener


app = Flask(__name__)


@app.get("/status")
def status():
    """Return persisted node status and last heartbeat timestamps."""
    conn = init_db()
    try:
        nodes = get_all_nodes(conn)
    finally:
        conn.close()
    return jsonify({"nodes": nodes}), 200


if __name__ == "__main__":
    init_db().close()
    start_heartbeat_listener()
    start_failure_detector()
    app.run(debug=True, port=5000, use_reloader=False)
