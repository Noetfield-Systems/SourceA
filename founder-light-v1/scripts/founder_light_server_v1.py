#!/usr/bin/env python3
"""Founder Light v1 — minimal live founder surface. Port 13040.

Does NOT modify legacy hub (agent-control-panel :13020). Read-only use of slim sync + actions.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_A = ROOT.parent
PUBLIC = ROOT / "public"
SCRIPTS = SOURCE_A / "scripts"
sys.path.insert(0, str(SCRIPTS))

PORT = 13040

ESSENTIAL_ACTIONS = [
    {"id": "founder-ecosystem-safety", "label": "Safety check"},
    {"id": "founder-ecosystem-fix-all", "label": "Fix everything"},
    {"id": "founder-refresh", "label": "Refresh data"},
    {"id": "founder-goal1-autorun-stop", "label": "Stop factory"},
    {"id": "founder-emergency-stop", "label": "Emergency stop", "danger": True},
    {"id": "founder-restart-hub", "label": "Restart legacy hub"},
]


def _json_bytes(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def live_state() -> dict:
    from hub_sync_slim_v1 import hub_sync_payload, live_factory_payload, live_queue_payload  # noqa: WPS433

    sync = hub_sync_payload()
    factory = live_factory_payload()
    queue = live_queue_payload()
    hfv = sync.get("home_founder_view") or {}
    goals = hfv.get("goals") or []
    g0 = goals[0] if goals else {}
    status = hfv.get("status") or {}
    return {
        "ok": True,
        "app": "founder-light-v1",
        "port": PORT,
        "legacy_hub": "http://127.0.0.1:13020",
        "generation_id": sync.get("generation_id"),
        "built_at": sync.get("built_at"),
        "home": {
            "headline": status.get("headline") or "Status",
            "subline": status.get("subline") or status.get("next_plain") or "",
            "progress_pct": g0.get("progress_pct"),
            "progress_label": g0.get("status_label") or "",
            "goal_title": g0.get("title") or "Progress",
        },
        "context": {
            "frozen": bool(factory.get("frozen")),
            "queue_pos": queue.get("pos"),
            "sa_id": queue.get("sa_id"),
            "worker_ok": _worker_ok(),
        },
        "run": {
            "message": (sync.get("goal1_auto_run") or {}).get("unified_autorun", {}).get("message")
            or (sync.get("goal1_auto_run") or {}).get("executor", {}).get("busy")
            and "Running"
            or "Ready",
            "busy": bool((sync.get("goal1_auto_run") or {}).get("executor", {}).get("busy")),
        },
        "needs_you": _needs_you(hfv),
        "actions": ESSENTIAL_ACTIONS,
    }


def _worker_ok() -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:13030/health", timeout=1.5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status == 200 and bool(body.get("ok"))
    except Exception:
        return False


def _needs_you(hfv: dict) -> list[dict]:
    card = hfv.get("missed_actions_card") or {}
    items = card.get("items") or []
    out = []
    for it in items[:3]:
        out.append(
            {
                "label": it.get("label") or "Item",
                "id": it.get("id"),
                "tab": it.get("tab"),
            }
        )
    return out


def run_action(action_id: str) -> dict:
    from sina_command_lib import run_branch_action  # noqa: WPS433

    result = run_branch_action(action_id)
    # Light path: no hub_after_mutation / no 2.7MB rebuild
    result["state"] = live_state()
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = "FounderLight/1.0"

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
            self._send(200, _json_bytes({"ok": True, "service": "founder-light-v1", "port": PORT}))
            return
        if path == "/api/state":
            self._send(200, _json_bytes(live_state()))
            return
        if path in ("/", "/index.html"):
            html = (PUBLIC / "index.html").read_text(encoding="utf-8")
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        for name, ctype in (
            ("app.js", "application/javascript; charset=utf-8"),
            ("style.css", "text/css; charset=utf-8"),
        ):
            if path == f"/{name}":
                data = (PUBLIC / name).read_bytes()
                self._send(200, data, ctype)
                return
        self._send(404, _json_bytes({"ok": False, "error": "not found"}))

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/action":
            body = self._read_json()
            action_id = body.get("id")
            if not action_id:
                self._send(400, _json_bytes({"ok": False, "error": "id required"}))
                return
            try:
                result = run_action(action_id)
                code = 200 if result.get("ok") else 400
                self._send(code, _json_bytes(result))
            except Exception as exc:
                self._send(500, _json_bytes({"ok": False, "error": str(exc), "action_id": action_id}))
            return
        self._send(404, _json_bytes({"ok": False, "error": "not found"}))


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[founder-light-v1] http://127.0.0.1:{PORT}", flush=True)
    print(f"[founder-light-v1] legacy hub frozen at :13020 — reference only", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
