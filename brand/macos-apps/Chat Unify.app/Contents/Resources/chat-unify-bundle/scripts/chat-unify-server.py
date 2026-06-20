#!/usr/bin/env python3
"""Chat Unify — standalone server (UI + API). Default :13023. No Sina Command hub."""
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
    raw = os.environ.get("CHAT_UNIFY_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "chat-unify-server.py").is_file() and (root / "app" / "index.html").is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "chat-unify-standalone"
    if not APP_DIR.is_dir():
        APP_DIR = SOURCE_A / "agent-control-panel" / "mini-apps" / "chat-unify"
    SCRIPTS_DIR = SOURCE_A / "scripts"

PORT = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))


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
        if (candidate / "CHAT_EXTRACT_UNIFY_PROMPT.txt").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("CHAT_UNIFY_STANDALONE", "1")
os.environ.setdefault("CHAT_UNIFY_PORT", str(PORT))

sys.path.insert(0, str(SCRIPTS_DIR))
if str(REAL_SA / "scripts") not in sys.path:
    sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class ChatUnifyHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class ChatUnifyHandler(BaseHTTPRequestHandler):
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
                    "service": "chat-unify",
                    "port": PORT,
                    "standalone": True,
                    "version": "1.4.0",
                    "ui_contract": build_ui_contract("chat_unify", port=PORT),
                },
            )
            return
        if path == "/api/chat-unify":
            from chat_unify_merge import build_report  # noqa: WPS433

            self._json(200, build_report())
            return
        if path == "/api/ai-unify":
            from ai_unify_api_v1 import status_payload  # noqa: WPS433

            row = status_payload()
            row["ok"] = True
            self._json(200, row)
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/ai-unify":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from ai_unify_api_v1 import handle_action  # noqa: WPS433

            result = handle_action(body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path != "/api/chat-unify":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        from chat_unify_merge import handle_action  # noqa: WPS433

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
    boot_log = Path.home() / ".sina" / "chat-unify-boot.log"
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
        server = ChatUnifyHTTPServer(("127.0.0.1", PORT), ChatUnifyHandler)
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
    print(f"Chat Unify standalone → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
