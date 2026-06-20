#!/usr/bin/env python3
"""N8N Integration — standalone server (UI + API). Default :13026. No Sina Command hub."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


def _bundle_root_env() -> str:
    raw = os.environ.get("N8N_INTEGRATION_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "n8n-integration-server.py").is_file() and (root / "app" / "index.html").is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "n8n-standalone"
    SCRIPTS_DIR = SOURCE_A / "scripts"

PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))


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
        if (candidate / "SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("N8N_INTEGRATION_STANDALONE", "1")
os.environ.setdefault("N8N_INTEGRATION_PORT", str(PORT))

sys.path.insert(0, str(SCRIPTS_DIR))
if str(REAL_SA / "scripts") not in sys.path:
    sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class N8nIntegrationHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class N8nIntegrationHandler(BaseHTTPRequestHandler):
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
            from n8n_integration_core import VERSION  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "service": "n8n-integration",
                    "port": PORT,
                    "standalone": True,
                    "version": VERSION,
                    "ui_contract": build_ui_contract("n8n_integration", port=PORT),
                },
            )
            return
        if path == "/api/n8n-integration":
            from n8n_integration_core import build_report  # noqa: WPS433

            self._json(200, build_report())
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/n8n-integration":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        from n8n_integration_core import handle_action  # noqa: WPS433

        result = handle_action(body)
        err = (result.get("error") or "").strip().lower()
        if err.startswith("unknown") or err == "not_found":
            self._json(400, result)
        else:
            self._json(200, result)

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
    boot_log = Path.home() / ".sina" / "n8n-integration-boot.log"
    try:
        boot_log.parent.mkdir(parents=True, exist_ok=True)
        boot_log.write_text(
            f"{datetime.now(timezone.utc).isoformat()} starting port={PORT} app_dir={APP_DIR}\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    if not APP_DIR.is_dir():
        print(f"Missing app dir: {APP_DIR}", file=sys.stderr)
        sys.exit(1)
    try:
        server = N8nIntegrationHTTPServer(("127.0.0.1", PORT), N8nIntegrationHandler)
        try:
            boot_log.write_text(
                boot_log.read_text(encoding="utf-8") + f"bound ok fd={getattr(server.socket, 'fileno', lambda: '?')()}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
    except OSError as exc:
        try:
            boot_log.write_text(
                boot_log.read_text(encoding="utf-8") + f"bind failed: {exc}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        print(f"Bind failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"N8N Integration standalone → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
