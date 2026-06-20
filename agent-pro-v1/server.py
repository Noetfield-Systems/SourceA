#!/usr/bin/env python3
"""Agent Pro v1 — standalone agent surface. No legacy hub. Port 13050."""
from __future__ import annotations

import json
import queue
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
PORT = 13050

# In-memory only — wire real agents later via AGENT_PRO_BACKEND env (not implemented here).
STATE = {
    "version": 1,
    "inbox": [
        {
            "id": "task-1",
            "title": "Review pricing page copy",
            "delegate": "Research agent",
            "status": "needs_approval",
            "owner": "You",
        },
        {
            "id": "task-2",
            "title": "Ship onboarding email sequence",
            "delegate": "Ops agent",
            "status": "queued",
            "owner": "You",
        },
    ],
    "sessions": [],
    "active_session_id": None,
}
STATE_LOCK = threading.Lock()
SSE_CLIENTS: list[queue.Queue] = []


def _broadcast(event: str, data: dict) -> None:
    payload = json.dumps({"event": event, "data": data, "ts": time.time()})
    dead = []
    for q in SSE_CLIENTS:
        try:
            q.put_nowait(payload)
        except Exception:
            dead.append(q)
    for q in dead:
        if q in SSE_CLIENTS:
            SSE_CLIENTS.remove(q)


def _snapshot() -> dict:
    with STATE_LOCK:
        return json.loads(json.dumps(STATE))


def _run_session(session_id: str, prompt: str) -> None:
    steps = [
        ("plan", "Scanning context and drafting plan…"),
        ("plan", f"Goal: {prompt[:120]}"),
        ("plan", "1. Gather requirements\n2. Draft deliverable\n3. Review with you"),
        ("act", "Running step 1 — gather requirements"),
        ("act", "Running step 2 — draft deliverable"),
        ("act", "Running step 3 — prepare summary"),
        ("done", "Session complete — ready for your review."),
    ]
    for phase, line in steps:
        time.sleep(1.2)
        with STATE_LOCK:
            for s in STATE["sessions"]:
                if s["id"] == session_id:
                    s["phase"] = phase
                    s["log"].append({"phase": phase, "line": line, "at": time.time()})
                    if phase == "done":
                        s["status"] = "done"
                    else:
                        s["status"] = "running"
                    break
        _broadcast("session.update", _snapshot())
    _broadcast("state", _snapshot())


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentPro/1.0"

    def log_message(self, fmt, *args):
        return

    def _send(self, code: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, json.dumps({"ok": True, "app": "agent-pro-v1", "port": PORT}).encode())
            return
        if path == "/api/state":
            self._send(200, json.dumps({"ok": True, **_snapshot()}).encode())
            return
        if path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            q: queue.Queue = queue.Queue()
            SSE_CLIENTS.append(q)
            try:
                self.wfile.write(f"data: {json.dumps({'event': 'connected', 'data': _snapshot()})}\n\n".encode())
                self.wfile.flush()
                while True:
                    msg = q.get()
                    self.wfile.write(f"data: {msg}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                if q in SSE_CLIENTS:
                    SSE_CLIENTS.remove(q)
            return
        if path in ("/", "/index.html"):
            self._send(200, (PUBLIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        for name, ctype in (("app.js", "application/javascript"), ("style.css", "text/css")):
            if path == f"/{name}":
                self._send(200, (PUBLIC / name).read_bytes(), f"{ctype}; charset=utf-8")
                return
        self._send(404, b'{"ok":false}')

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/api/inbox/approve":
            tid = body.get("id")
            with STATE_LOCK:
                for t in STATE["inbox"]:
                    if t["id"] == tid:
                        t["status"] = "approved"
            snap = _snapshot()
            _broadcast("state", snap)
            self._send(200, json.dumps({"ok": True, **snap}).encode())
            return
        if path == "/api/session/start":
            prompt = (body.get("prompt") or "").strip() or "New task"
            sid = str(uuid.uuid4())[:8]
            session = {
                "id": sid,
                "prompt": prompt,
                "status": "running",
                "phase": "plan",
                "log": [{"phase": "plan", "line": "Session started.", "at": time.time()}],
            }
            with STATE_LOCK:
                STATE["sessions"].insert(0, session)
                STATE["active_session_id"] = sid
            snap = _snapshot()
            _broadcast("state", snap)
            threading.Thread(target=_run_session, args=(sid, prompt), daemon=True).start()
            self._send(200, json.dumps({"ok": True, **snap}).encode())
            return
        self._send(404, b'{"ok":false}')


def main() -> None:
    print(f"[agent-pro-v1] http://127.0.0.1:{PORT}", flush=True)
    print("[agent-pro-v1] Standalone agent surface — no legacy hub imports", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
