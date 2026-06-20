#!/usr/bin/env python3
"""Apple Health — standalone server (UI + API). Default :13025. No Sina Command hub."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

BUNDLE_ROOT = os.environ.get("APPLE_HEALTH_BUNDLE_ROOT", "").strip()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "apple-health-standalone"
    SCRIPTS_DIR = SOURCE_A / "scripts"
PORT = int(os.environ.get("APPLE_HEALTH_PORT", "13025"))


def _resolve_source_a() -> Path:
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (
        Path.home() / "Desktop" / "SourceA",
        Path(__file__).resolve().parents[1],
    ):
        if (candidate / "ACTIVE_NOW.md").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("APPLE_HEALTH_STANDALONE", "1")
os.environ.setdefault("APPLE_HEALTH_PORT", str(PORT))

sys.path.insert(0, str(SCRIPTS_DIR))
if str(REAL_SA / "scripts") not in sys.path:
    sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class AppleHealthHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "service": "apple-health",
                    "port": PORT,
                    "standalone": True,
                    "version": "2.0.0",
                    "ui_contract": build_ui_contract("apple_health", port=PORT),
                },
            )
            return
        if path == "/api/apple-health":
            from apple_health_mini import apple_health_payload  # noqa: WPS433

            self._json(200, apple_health_payload())
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/apple-health":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        from apple_health_mini import handle_action  # noqa: WPS433

        result = handle_action(body)
        self._json(200 if result.get("ok", True) else 400, result)

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        rel = unquote(path.lstrip("/"))
        file_path = (APP_DIR / rel).resolve()
        root = APP_DIR.resolve()
        if root != file_path and root not in file_path.parents:
            self.send_error(403)
            return
        if file_path.is_dir():
            file_path = file_path / "index.html"
        if not file_path.is_file():
            self.send_error(404)
            return
        ctype, _ = mimetypes.guess_type(str(file_path))
        if not ctype:
            ctype = "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if str(file_path).endswith(".html"):
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        cors_headers(self)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main() -> None:
    if not APP_DIR.is_dir():
        print(f"Missing app dir: {APP_DIR}", file=sys.stderr)
        sys.exit(1)

    server = ThreadingHTTPServer(("127.0.0.1", PORT), AppleHealthHandler)
    print(f"Apple Health standalone → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
