#!/usr/bin/env python3
"""Sina Command local API — :13021 refresh, state, open, todos."""
from __future__ import annotations

import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))
from sina_command_lib import (  # noqa: E402
    SOURCE_A as SA,
    branches_registry,
    build_payload,
    mark_todo_done,
    read_rule,
    run_branch_action,
    write_panel_outputs,
    write_rule,
)

PORT = int(__import__("os").environ.get("SINA_COMMAND_API_PORT", "13021"))
ALLOWED_OPEN_ROOTS = [
    SA,
    Path.home() / "Desktop/SinaaiMonoRepo",
    Path.home() / "Desktop/mergepack",
    Path.home() / "Desktop/SinaaiDataBase",
    Path.home() / "Desktop/SinaPromptOS",
]


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class CommandAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/rule":
            rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
            if not rel:
                self._json(400, {"error": "path query required"})
                return
            self._json(200, read_rule(rel))
            return
        if path in ("/api/state", "/command-data.json"):
            p = SA / "agent-control-panel" / "command-data.json"
            if not p.is_file():
                payload = build_payload()
                write_panel_outputs(payload)
            body = p.read_text(encoding="utf-8")
            self._json(200, json.loads(body))
            return
        if path == "/api/branches":
            self._json(200, {"ok": True, "branches": branches_registry()})
            return
        if path == "/health":
            self._json(200, {"ok": True, "service": "sina-command-api"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            body = {}

        if path == "/refresh":
            payload = build_payload(run_refresh_scripts=True)
            write_panel_outputs(payload)
            self._json(200, {"ok": True, "built_at": payload.get("built_at"), "data": payload})
            return

        if path == "/open":
            rel = body.get("path") or parse_qs(urlparse(self.path).query).get("path", [""])[0]
            if not rel:
                self._json(400, {"error": "path required"})
                return
            target = Path(rel).expanduser()
            if not target.is_absolute():
                target = (SA / rel).resolve()
            else:
                target = target.resolve()
            allowed = any(
                target == root.resolve() or root.resolve() in target.parents
                for root in ALLOWED_OPEN_ROOTS
            )
            if not allowed:
                self._json(403, {"error": "path not allowed"})
                return
            if not target.exists():
                self._json(404, {"error": "not found"})
                return
            subprocess.run(["open", str(target)], check=False)
            self._json(200, {"ok": True, "opened": str(target)})
            return

        if path == "/api/rule":
            rel = body.get("path")
            content = body.get("content")
            if not rel or content is None:
                self._json(400, {"error": "path and content required"})
                return
            result = write_rule(rel, content)
            if result.get("ok"):
                payload = build_payload(run_refresh_scripts=True)
                write_panel_outputs(payload)
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return

        if path == "/api/action":
            action_id = body.get("id")
            if not action_id:
                self._json(400, {"error": "id required"})
                return
            result = run_branch_action(action_id)
            if result.get("ok") and action_id == "hq-refresh":
                payload = build_payload(run_refresh_scripts=False)
                write_panel_outputs(payload)
                result["data"] = payload
            elif result.get("ok") and action_id.startswith("pos-"):
                payload = build_payload(run_refresh_scripts=False)
                write_panel_outputs(payload)
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return

        if path == "/todo/done":
            todo_id = body.get("id")
            if not todo_id:
                self._json(400, {"error": "id required"})
                return
            result = mark_todo_done(todo_id)
            if result.get("ok"):
                payload = build_payload(run_refresh_scripts=True)
                write_panel_outputs(payload)
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return

        self._json(404, {"error": "not found"})

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        cors_headers(self)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), CommandAPIHandler)
    print(f"Sina Command API → http://127.0.0.1:{PORT}/")
    print("  GET  /api/state   GET /api/branches   GET /api/rule")
    print("  POST /api/action  POST /api/rule   POST /refresh   POST /open   POST /todo/done")
    server.serve_forever()


if __name__ == "__main__":
    main()
