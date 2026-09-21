"""Small command-line client for the coordinator HTTP API."""

import argparse
from pathlib import Path

import requests


def _url(base_url: str, suffix: str) -> str:
    return base_url.rstrip("/") + suffix


def main() -> int:
    parser = argparse.ArgumentParser(description="P2P storage client")
    parser.add_argument("--coordinator", default="http://127.0.0.1:5000")
    commands = parser.add_subparsers(dest="command", required=True)
    upload = commands.add_parser("upload")
    upload.add_argument("path", type=Path)
    download = commands.add_parser("download")
    download.add_argument("file_id")
    download.add_argument("output", type=Path)
    commands.add_parser("status")
    args = parser.parse_args()
    try:
        if args.command == "upload":
            with args.path.open("rb") as source:
                response = requests.post(_url(args.coordinator, "/files"), files={"file": (args.path.name, source)}, timeout=30)
            response.raise_for_status()
            print(response.json()["file_id"])
        elif args.command == "download":
            response = requests.get(_url(args.coordinator, f"/files/{args.file_id}"), timeout=30)
            response.raise_for_status()
            args.output.write_bytes(response.content)
            print(args.output)
        else:
            response = requests.get(_url(args.coordinator, "/status"), timeout=10)
            response.raise_for_status()
            for node in response.json()["nodes"]:
                print(f"{node['node_id']}: {node['status']} ({node['host']}:{node['port']})")
    except (OSError, requests.RequestException, KeyError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
