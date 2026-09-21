"""Coordinator HTTP status application with heartbeat tracking."""

from flask import Flask, jsonify, request

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from coordinator.db import get_all_nodes, init_db
from coordinator.heartbeat_monitor import start_failure_detector, start_heartbeat_listener
from coordinator.storage import StorageError, download_bytes, upload_bytes


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


@app.post("/files")
def upload():
    """Accept an uploaded file and return its coordinator-issued ID."""
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify({"error": "multipart field 'file' is required"}), 400
    try:
        file_id = upload_bytes(uploaded.read(), uploaded.filename or "upload.bin")
    except StorageError as error:
        return jsonify({"error": str(error)}), 503
    return jsonify({"file_id": file_id}), 201


@app.get("/files/<file_id>")
def download(file_id: str):
    """Return reconstructed plaintext for a stored file."""
    try:
        data = download_bytes(file_id)
    except StorageError as error:
        return jsonify({"error": str(error)}), 404
    return app.response_class(data, mimetype="application/octet-stream")


if __name__ == "__main__":
    init_db().close()
    start_heartbeat_listener()
    start_failure_detector()
    app.run(debug=True, port=5000, use_reloader=False)
