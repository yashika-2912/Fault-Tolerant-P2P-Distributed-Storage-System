"""Minimal Day-1 coordinator HTTP application."""

from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/status")
def status():
    """Return the current node-status stub."""
    return jsonify({"nodes": []}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
