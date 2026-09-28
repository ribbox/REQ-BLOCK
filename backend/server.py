#!/usr/bin/env python3
"""
Requirement Scratch – shared snapshot API
-----------------------------------------
GET  /            → current project JSON
PUT  /  (or POST) → replace project JSON
GET  /health      → liveness

Optional basic auth: set BASIC_AUTH_USER and BASIC_AUTH_PASSWORD.
Data is stored in DATA_FILE (default /data/project.json).
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
DATA_FILE = Path(os.environ.get("DATA_FILE", "/data/project.json"))
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "*")
BASIC_USER = os.environ.get("BASIC_AUTH_USER", "")
BASIC_PASS = os.environ.get("BASIC_AUTH_PASSWORD", "")

_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_snapshot() -> dict:
    return {
        "version": 1,
        "exportedAt": utc_now(),
        "savedAt": utc_now(),
        "savedBy": "server",
        "pages": [
            {
                "id": 1,
                "name": "Page 1",
                "savedRequirements": [],
                "workspaceState": None,
            }
        ],
        "currentPageId": 1,
        "nextPageId": 2,
        "pieceLibrary": [
            {"type": "req_list_item", "text": "PDF report"},
            {"type": "req_list_item", "text": "Word report"},
            {"type": "req_list_item", "text": "CSV"},
        ],
    }


def ensure_data_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            json.dumps(default_snapshot(), indent=2), encoding="utf-8"
        )


def read_raw() -> bytes:
    ensure_data_file()
    with _lock:
        return DATA_FILE.read_bytes()


def write_raw(data: bytes) -> None:
    ensure_data_file()
    # Validate JSON before writing
    parsed = json.loads(data.decode("utf-8"))
    if not isinstance(parsed, dict) or "pages" not in parsed:
        raise ValueError("Body must be a JSON object with a 'pages' array")
    with _lock:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(DATA_FILE)


def etag_for(data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()[:16]
    return f'"{digest}"'


def check_basic_auth(header: str | None) -> bool:
    if not BASIC_USER:
        return True  # auth disabled
    if not header or not header.startswith("Basic "):
        return False
    import base64

    try:
        decoded = base64.b64decode(header[6:].strip()).decode("utf-8")
        user, _, password = decoded.partition(":")
        return secrets.compare_digest(user, BASIC_USER) and secrets.compare_digest(
            password, BASIC_PASS
        )
    except Exception:
        return False


class Handler(BaseHTTPRequestHandler):
    server_version = "RequirementScratchBackend/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{utc_now()}] {self.address_string()} {fmt % args}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization, If-Match, Accept",
        )
        self.send_header("Access-Control-Expose-Headers", "ETag")
        if CORS_ORIGIN != "*":
            self.send_header("Access-Control-Allow-Credentials", "true")

    def _auth_ok(self) -> bool:
        if check_basic_auth(self.headers.get("Authorization")):
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Requirement Scratch"')
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"unauthorized"}')
        return False

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        if path not in ("/", ""):
            self.send_response(404)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return

        if not self._auth_ok():
            return

        raw = read_raw()
        tag = etag_for(raw)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("ETag", tag)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_PUT(self) -> None:
        self._handle_write()

    def do_POST(self) -> None:
        self._handle_write()

    def _handle_write(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path not in ("/", ""):
            self.send_response(404)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return

        if not self._auth_ok():
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 20 * 1024 * 1024:
            self.send_response(400)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"invalid body size"}')
            return

        body = self.rfile.read(length)
        current = read_raw()
        current_tag = etag_for(current)

        if_match = self.headers.get("If-Match")
        if if_match and if_match != current_tag:
            self.send_response(412)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("ETag", current_tag)
            self.end_headers()
            self.wfile.write(
                b'{"error":"precondition failed","message":"Remote was modified; load first"}'
            )
            return

        try:
            write_raw(body)
        except (ValueError, json.JSONDecodeError) as e:
            self.send_response(400)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "invalid json", "message": str(e)}).encode()
            )
            return

        new_raw = read_raw()
        new_tag = etag_for(new_raw)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("ETag", new_tag)
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "ok", "etag": new_tag, "savedAt": utc_now()}).encode()
        )


def main() -> None:
    ensure_data_file()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    auth = "on" if BASIC_USER else "off"
    print(
        f"Requirement Scratch backend listening on http://{HOST}:{PORT} "
        f"(data={DATA_FILE}, basic_auth={auth}, cors={CORS_ORIGIN})"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
