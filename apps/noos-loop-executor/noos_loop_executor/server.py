#!/usr/bin/env python3
"""NOOS loop executor HTTP — GET /health · POST /loop (one bounded tick)."""
from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from noos_loop_executor.auth import auth_ok
from noos_loop_executor.tick_v1 import run_bounded_tick


def _json(handler: BaseHTTPRequestHandler, code: int, row: dict[str, Any]) -> None:
    body = json.dumps(row, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D401
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/health":
            secret_ready = bool((os.environ.get("NOOS_LOOP_SECRET") or "").strip())
            _json(
                self,
                200,
                {
                    "ok": True,
                    "service": "noos-loop-executor",
                    "schema": "noos-loop-executor-health-v1",
                    "auth_header": "X-NOOS-Loop-Secret",
                    "secret_configured": secret_ready,
                    "bounded_tick": True,
                    "daemon": False,
                },
            )
            return
        _json(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/loop":
            _json(self, 404, {"ok": False, "error": "not_found"})
            return

        ok_auth, reason = auth_ok(dict(self.headers))
        if not ok_auth:
            _json(self, 401, {"ok": False, "error": reason or "unauthorized"})
            return

        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            body = {}

        row = run_bounded_tick(body if isinstance(body, dict) else {})
        _json(self, 200 if row.get("ok") else 422, row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    args = parser.parse_args()
    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
