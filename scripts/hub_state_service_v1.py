#!/usr/bin/env python3
"""
Hub State service scaffold (N2) — queue/progress read API on :13031.
Sole-writer migration deferred until ASF Phase N2 approved.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("HUB_STATE_SERVICE_PORT", "13031"))
TRUTH = Path.home() / ".sina" / "run-inbox-disk-truth-v1.json"
PROGRESS = ROOT / "PROGRAM_PROGRESS.json"


class _StateHandler(BaseHTTPRequestHandler):
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
            self._json(200, {"ok": True, "service": "hub-state", "port": PORT})
            return
        if path == "/api/queue":
            try:
                t = json.loads(TRUTH.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                t = {}
            q = t.get("queue") or {}
            self._json(
                200,
                {
                    "ok": True,
                    "sa_id": q.get("sa_id"),
                    "queue_role": q.get("queue_role"),
                    "pos": q.get("pos"),
                    "pending": bool(t.get("pending")),
                },
            )
            return
        if path == "/api/progress":
            try:
                p = json.loads(PROGRESS.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                p = {}
            self._json(200, {"ok": True, "progress": p})
            return
        self.send_error(404)


def main() -> None:
    print(f"[state] listening on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), _StateHandler).serve_forever()


if __name__ == "__main__":
    main()
