#!/usr/bin/env python3
"""
Hub Agent runtime scaffold (N3) — factory/IC health on :13032.
Full extract deferred until ASF Phase N3 approved.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("HUB_AGENT_RUNTIME_PORT", "13032"))
FACTORY = Path.home() / ".sina" / "factory-now-v1.json"


class _RuntimeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "hub-agent-runtime", "port": PORT})
            return
        if path == "/api/factory":
            try:
                f = json.loads(FACTORY.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                f = {}
            self._json(
                200,
                {
                    "ok": True,
                    "frozen": bool(f.get("frozen") or f.get("freeze_on")),
                    "mode": f.get("mode"),
                    "factory_now": f,
                },
            )
            return
        self.send_error(404)


def main() -> None:
    print(f"[agent-runtime] listening on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), _RuntimeHandler).serve_forever()


if __name__ == "__main__":
    main()
