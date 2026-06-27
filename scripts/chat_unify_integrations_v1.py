#!/usr/bin/env python3
"""Chat Unify Connect — integrations registry, live probes, webhook triggers."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _repo_root() -> Path:
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (
        Path.home() / "Desktop" / "SourceA",
        Path(__file__).resolve().parents[1],
    ):
        if (candidate / "data" / "chat-unify-integrations-v1.json").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


ROOT = _repo_root()
CATALOG_PATH = ROOT / "data" / "chat-unify-integrations-v1.json"
PLUGIN_PATH = ROOT / "data" / "chat-unify-cursor-plugin-v1.json"
TRIGGERS_PATH = Path.home() / ".sina" / "chat-unify-triggers-v1.json"
RECEIPT_PATH = Path.home() / ".sina" / "chat-unify-connect-receipt-v1.json"
CHAT_UNIFY_PORT = 13023


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _http_probe(url: str, timeout: float = 1.2) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            ok = 200 <= resp.status < 300
            parsed: Any = None
            try:
                parsed = json.loads(body) if body.strip() else None
            except json.JSONDecodeError:
                parsed = body[:200]
            return {"ok": ok, "status": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc.reason)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:200]}


def _cursor_running() -> bool:
    try:
        proc = subprocess.run(
            ["pgrep", "-x", "Cursor"],
            capture_output=True,
            check=False,
        )
        return proc.returncode == 0
    except OSError:
        return False


def _inbox_ready() -> dict[str, Any]:
    inbox = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
    if not inbox.is_file():
        return {"ok": False, "path": str(inbox), "reason": "missing_inbox"}
    row = _read_json(inbox)
    return {"ok": True, "path": str(inbox), "has_prompt": bool((row.get("prompt") or "").strip())}


def _env_ready(keys: list[str]) -> dict[str, bool]:
    return {k: bool(os.environ.get(k, "").strip()) for k in keys}


def load_catalog() -> dict[str, Any]:
    return _read_json(CATALOG_PATH)


def load_plugin_manifest() -> dict[str, Any]:
    return _read_json(PLUGIN_PATH)


def load_triggers() -> dict[str, Any]:
    row = _read_json(TRIGGERS_PATH)
    if not row:
        return {"schema": "chat-unify-triggers-v1", "triggers": [], "updated_at": _utc_now()}
    return row


def save_trigger(name: str, event: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    store = load_triggers()
    triggers = list(store.get("triggers") or [])
    entry = {
        "id": f"trg_{len(triggers) + 1:04d}",
        "name": name,
        "event": event,
        "meta": meta or {},
        "created_at": _utc_now(),
    }
    triggers.append(entry)
    store["triggers"] = triggers[-50:]
    store["updated_at"] = _utc_now()
    _write_json(TRIGGERS_PATH, store)
    return entry


def integrations_live_payload(port: int = CHAT_UNIFY_PORT) -> dict[str, Any]:
    catalog = load_catalog()
    base = f"http://127.0.0.1:{port}"
    self_health = _http_probe(f"{base}/health")
    n8n = _http_probe("http://127.0.0.1:13026/health")
    cloud = _http_probe("http://127.0.0.1:13027/health")
    hub = _http_probe("http://127.0.0.1:13020/health")

    cursor_local = {
        "ok": _cursor_running(),
        "cursor_app": _cursor_running(),
        "inbox": _inbox_ready(),
        "paste_env": os.environ.get("SINA_ALLOW_CURSOR_PASTE", "").strip() in ("1", "true", "yes"),
    }
    cursor_cloud = {
        "ok": any(_env_ready(["CURSOR_API_KEY", "OPENROUTER_API_KEY"]).values()),
        "env": _env_ready(["CURSOR_API_KEY", "OPENROUTER_API_KEY"]),
    }

    lanes = []
    for lane in catalog.get("lanes") or []:
        lid = lane.get("id", "")
        status = "offline"
        detail: dict[str, Any] = {}
        if lid == "cursor_local":
            status = "live" if cursor_local["ok"] else "ready"
            detail = cursor_local
        elif lid == "cursor_cloud":
            status = "live" if cursor_cloud["ok"] else "setup"
            detail = cursor_cloud
        elif lid == "n8n":
            status = "live" if n8n.get("ok") else "offline"
            detail = n8n
        elif lid == "cloud_workers":
            status = "live" if cloud.get("ok") else "offline"
            detail = cloud
        elif lid == "webhook_inbound":
            status = "live" if self_health.get("ok") else "offline"
            detail = {"hook_url": f"{base}/api/integrations/v1/hook"}
        elif lid == "mcp_ready":
            status = "live" if self_health.get("ok") else "offline"
            detail = {"manifest_url": f"{base}/api/integrations/v1/manifest"}
        lanes.append({**lane, "status": status, "probe": detail})

    payload = {
        "ok": bool(self_health.get("ok")),
        "schema": "chat-unify-integrations-live-v1",
        "saved_at": _utc_now(),
        "base_url": base,
        "ui_version": (self_health.get("body") or {}).get("ui_version") if isinstance(self_health.get("body"), dict) else None,
        "features": (self_health.get("body") or {}).get("features") if isinstance(self_health.get("body"), dict) else [],
        "catalog": catalog,
        "lanes": lanes,
        "mesh": {
            "chat_unify": self_health,
            "hub": hub,
            "n8n": n8n,
            "cloud_workers": cloud,
        },
        "triggers": load_triggers().get("triggers") or [],
        "plugin": load_plugin_manifest(),
    }
    _write_json(RECEIPT_PATH, {"saved_at": payload["saved_at"], "ok": payload["ok"], "lanes_live": sum(1 for x in lanes if x.get("status") == "live")})
    return payload


def handle_integration_action(body: dict[str, Any], *, port: int = CHAT_UNIFY_PORT) -> dict[str, Any]:
    action = (body.get("action") or "").strip().lower()
    if action in ("status", "live", "refresh"):
        return integrations_live_payload(port=port)
    if action == "manifest":
        return {"ok": True, "manifest": load_plugin_manifest(), "catalog": load_catalog()}
    if action == "register_trigger":
        name = (body.get("name") or "unnamed").strip()[:80]
        event = (body.get("event") or "custom").strip()[:80]
        entry = save_trigger(name, event, body.get("meta") if isinstance(body.get("meta"), dict) else {})
        return {"ok": True, "trigger": entry}
    if action == "test_connection":
        lane = (body.get("lane") or "").strip()
        live = integrations_live_payload(port=port)
        match = next((x for x in live.get("lanes") or [] if x.get("id") == lane), None)
        if not match:
            return {"ok": False, "error": "unknown_lane", "lane": lane}
        return {"ok": match.get("status") in ("live", "ready"), "lane": match}
    if action == "dispatch_cloud":
        url = "http://127.0.0.1:13027/api/cloud-worker/dispatch/v1"
        payload = json.dumps(body.get("dispatch") or {"kind": "ping", "source": "chat_unify_connect"}).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read(8192).decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = {"raw": raw[:500]}
                return {"ok": True, "status": resp.status, "result": parsed}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:300]}
    return {"ok": False, "error": f"unknown_integration_action:{action}"}


def handle_webhook_hook(body: dict[str, Any], *, run_chat_unify) -> dict[str, Any]:
    """Inbound automation hook — routes event to Chat Unify machine."""
    event = (body.get("event") or body.get("type") or "custom").strip()
    save_trigger(f"hook:{event}", event, {"source": body.get("source", "webhook")})

    plugin = load_plugin_manifest()
    route = next((h for h in plugin.get("hook_events") or [] if h.get("event") == event), None)
    if route and isinstance(route.get("body"), dict):
        action_body = dict(route["body"])
        for key, val in action_body.items():
            if isinstance(val, str) and val.startswith("{{") and val.endswith("}}"):
                field = val[2:-2].strip()
                action_body[key] = body.get(field) or body.get("text") or ""
        result = run_chat_unify(action_body)
        return {"ok": bool(result.get("ok")), "event": event, "routed": route.get("routes_to"), "result": result}

    text = (body.get("text") or body.get("founder_text") or body.get("prompt") or "").strip()
    if not text:
        return {"ok": False, "error": "empty_payload", "event": event}

    if event.startswith("forge") or event == "prompt_forge":
        result = run_chat_unify({"action": "prompt_forge", "text": text})
    elif event.startswith("verify") or event == "founder_loop":
        result = run_chat_unify({"action": "founder_loop_stage", "stage": "language", "text": text})
    elif event.startswith("proof"):
        result = run_chat_unify({"action": "proof_pack_stage", "stage": "collect", "text": text})
    else:
        result = run_chat_unify({"action": "prompt_forge", "text": text})

    return {"ok": bool(result.get("ok")), "event": event, "result": result}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Chat Unify integrations live probe")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = integrations_live_payload()
    print(json.dumps(out, indent=2, ensure_ascii=False))
