#!/usr/bin/env python3
"""
Single rebuild worker — SourceA hub.
ONE instance enforced via fcntl lock.
Dirty coalescing: N mutations in SETTLE seconds → 1 rebuild.
Standalone service on :13030 (health) + queue consumer thread.
"""
from __future__ import annotations

import fcntl
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("HUB_REBUILD_WORKER_PORT", "13030"))
QUEUE = Path.home() / ".sina" / "hub-rebuild-queue-v1.jsonl"
DONE = Path.home() / ".sina" / "hub-rebuild-done-v1.jsonl"
LOCK = Path.home() / ".sina" / "hub-rebuild-worker-v1.lock"
POLL = 1.0
SETTLE = 3.0

sys.path.insert(0, str(ROOT / "scripts"))

_LOCK_FH = None


class _HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/health":
            body = json.dumps({"ok": True, "service": "hub-rebuild-worker", "port": PORT}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)


def _acquire_lock():
    global _LOCK_FH
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    fh = open(LOCK, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _LOCK_FH = fh
        return fh
    except BlockingIOError:
        fh.close()
        print("[worker] another instance running — exiting", flush=True)
        sys.exit(1)


def _drain() -> list[dict]:
    if not QUEUE.exists():
        return []
    tmp = str(QUEUE) + ".drain"
    try:
        os.rename(str(QUEUE), tmp)
    except FileNotFoundError:
        return []
    evts: list[dict] = []
    with open(tmp, encoding="utf-8") as f:
        for line in f:
            try:
                evts.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass
    os.unlink(tmp)
    return evts


def _rebuild(run_refresh: bool) -> None:
    from hub_live_events_lib_v1 import append_live_event  # noqa: WPS433
    from sina_command_lib import bump_shell_generation_id, hub_after_mutation  # noqa: WPS433

    try:
        append_live_event("rebuild.status", {"state": "running", "run_refresh": run_refresh})
        hub_after_mutation(run_refresh_scripts=run_refresh)
        gid = bump_shell_generation_id()
        shell_path = ROOT / "agent-control-panel" / "command-data-shell.json"
        built_at = ""
        try:
            built_at = json.loads(shell_path.read_text(encoding="utf-8")).get("built_at") or ""
        except (OSError, json.JSONDecodeError):
            pass
        append_live_event(
            "hub.generation",
            {"generation_id": gid, "built_at": built_at, "run_refresh": run_refresh},
        )
        append_live_event(
            "tab.invalidate",
            {"keys": ["agent_loop", "intelligence_circle", "command"], "generation_id": gid},
        )
        append_live_event("rebuild.status", {"state": "done", "generation_id": gid})
        print(f"[worker] rebuild done (refresh={run_refresh}, generation_id={gid})", flush=True)
    except Exception as e:
        append_live_event("rebuild.status", {"state": "error", "error": str(e)})
        print(f"[worker] rebuild error: {e}", flush=True)


def _queue_loop() -> None:
    print("[worker] queue loop started — polling", flush=True)
    pending: list[dict] = []
    last_event_ts = 0.0
    dirty = False

    while True:
        new = _drain()
        if new:
            pending.extend(new)
            last_event_ts = time.time()

        if pending and not dirty and (time.time() - last_event_ts) >= SETTLE:
            dirty = True
            run_ref = any(e.get("run_refresh") for e in pending)
            print(f"[worker] coalescing {len(pending)} events → 1 rebuild", flush=True)
            DONE.parent.mkdir(parents=True, exist_ok=True)
            with open(DONE, "a", encoding="utf-8") as f:
                for e in pending:
                    f.write(json.dumps({**e, "consumed_at": time.time()}) + "\n")
            pending.clear()
            _rebuild(run_ref)
            dirty = False

        time.sleep(POLL)


def main() -> None:
    _acquire_lock()
    threading.Thread(target=_queue_loop, daemon=True, name="hub-rebuild-queue").start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), _HealthHandler)
    print(f"[worker] health → http://127.0.0.1:{PORT}/health", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
