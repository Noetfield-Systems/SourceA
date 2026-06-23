#!/usr/bin/env python3
"""AG Routing Panel — standalone server :8782 (agent light + full)."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("AG_ROUTING_PANEL_PORT", "8782"))


def _bundle_root_env() -> str:
    raw = os.environ.get("AG_ROUTING_PANEL_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "ag-routing-panel-server.py").is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    APP_DIR = Path(BUNDLE_ROOT) / "app"
    SCRIPTS_DIR = Path(BUNDLE_ROOT) / "scripts"
else:
    APP_DIR = Path(__file__).resolve().parents[1] / "scripts" / "ag-routing-panel-standalone"
    SCRIPTS_DIR = Path(__file__).resolve().parents[1]

REAL_SA = Path(os.environ.get("SINA_SOURCE_A", str(Path.home() / "Desktop" / "SourceA")))
LIVE_APP = REAL_SA / "scripts" / "ag-routing-panel-standalone"
if LIVE_APP.is_dir() and (LIVE_APP / "index.html").is_file():
    APP_DIR = LIVE_APP

sys.path.insert(0, str(SCRIPTS_DIR))
if str(REAL_SA / "scripts") not in sys.path:
    sys.path.insert(0, str(REAL_SA / "scripts"))


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        pass

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        qs = parse_qs(urlparse(self.path).query)
        if path == "/health":
            from ag_routing_panel_core import VERSION  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "service": "ag-routing-panel",
                    "port": PORT,
                    "version": VERSION,
                    "standalone": True,
                },
            )
            return
        if path == "/api/ag-routing-panel":
            from ag_routing_panel_core import build_report_full, build_report_light  # noqa: WPS433

            if qs.get("full"):
                self._json(200, build_report_full())
            else:
                self._json(200, build_report_light())
            return
        if path in ("/", "/index.html"):
            index = APP_DIR / "index.html"
            if index.is_file():
                self._serve_file(index)
                return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        if path == "/api/ag-routing-panel":
            from ag_routing_panel_core import handle_action  # noqa: WPS433

            result = handle_action(body)
            self._json(200 if result.get("ok", True) else 400, result)
            return
        self._json(404, {"ok": False, "error": "not_found"})

    def _serve_file(self, fp: Path) -> None:
        ctype = mimetypes.guess_type(str(fp))[0] or "application/octet-stream"
        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, path: str) -> None:
        rel = path.lstrip("/")
        fp = APP_DIR / rel
        if fp.is_file() and str(fp.resolve()).startswith(str(APP_DIR.resolve())):
            self._serve_file(fp)
            return
        self._json(404, {"ok": False, "error": "not_found", "path": path})


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"AG Routing Panel http://127.0.0.1:{PORT}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
