#!/usr/bin/env python3
"""API Station — per-app task router for founder ops, AI agents, automation spine."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
CHAT_PORT = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))
N8N_PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))
CLOUD_PORT = int(os.environ.get("CLOUD_WORKERS_PORT", "13027"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _http_json(url: str, *, method: str = "GET", body: dict | None = None, timeout: float = 30.0) -> dict[str, Any]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw.strip() else {}
            return {"ok": True, "status": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw[:500]}
        return {"ok": False, "status": exc.code, "body": parsed, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "url": url}


def _probe(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def _founder_hub_tasks(hub: str) -> list[dict[str, Any]]:
    from founder_ops_v1 import station_tasks  # noqa: WPS433

    return station_tasks("machine-hub" if hub == "H2" else "worker-hub")


STATIONS: dict[str, dict[str, Any]] = {
    "worker-hub": {
        "title": "Worker Hub (H1)",
        "port": HUB_PORT,
        "hub": "H1",
        "api_base": f"http://127.0.0.1:{HUB_PORT}/api/api-station/v1",
    },
    "machine-hub": {
        "title": "Machine Hub (H2)",
        "port": HUB_PORT,
        "hub": "H2",
        "api_base": f"http://127.0.0.1:{HUB_PORT}/api/api-station/v1?app=machine-hub",
    },
    "founder-ops": {
        "title": "Founder Ops (all)",
        "port": HUB_PORT,
        "hub": "both",
        "api_base": f"http://127.0.0.1:{HUB_PORT}/api/api-station/v1?app=founder-ops",
    },
    "hub-form": {
        "title": "Official Form",
        "port": HUB_PORT,
        "hub": "H1",
        "api_base": f"http://127.0.0.1:{HUB_PORT}/api/api-station/v1?app=hub-form",
    },
    "portfolio-mail": {
        "title": "Portfolio Mail",
        "port": HUB_PORT,
        "api_base": f"http://127.0.0.1:{HUB_PORT}/api/api-station/v1?app=portfolio-mail",
        "tasks": [
            {"id": "integration_status", "label": "Integration status", "method": "GET", "tier": "light", "desc": "Mail · Chat · N8N wire state"},
            {"id": "wire_stack", "label": "Wire stack", "method": "POST", "tier": "light", "desc": "Run portfolio mail integration wire"},
            {"id": "refresh_inboxes", "label": "Refresh inboxes", "method": "GET", "tier": "light", "desc": "Reload mailbox probes"},
        ],
    },
    "chat-unify": {
        "title": "Chat Unify",
        "port": CHAT_PORT,
        "api_base": f"http://127.0.0.1:{CHAT_PORT}/api/api-station/v1",
        "tasks": [
            {"id": "report", "label": "Merge report", "method": "GET", "tier": "light", "desc": "Extract counts and brief status"},
            {"id": "merge_all", "label": "Merge all", "method": "POST", "tier": "heavy", "desc": "Run chat unify merge pipeline"},
            {"id": "stack_status", "label": "Stack status", "method": "GET", "tier": "light", "desc": "Portfolio stack from hub"},
        ],
    },
    "n8n-integration": {
        "title": "N8N Integration",
        "port": N8N_PORT,
        "api_base": f"http://127.0.0.1:{N8N_PORT}/api/api-station/v1",
        "tasks": [
            {"id": "report", "label": "Stack report", "method": "GET", "tier": "light", "desc": "n8n · hub · workflow status"},
            {"id": "capture_intelligence", "label": "Capture intelligence", "method": "POST", "tier": "light", "desc": "Ingest stack signals to n8n spine"},
            {"id": "wire_portfolio_mail", "label": "Wire Portfolio Mail", "method": "POST", "tier": "light", "desc": "Three-app mail glue"},
            {"id": "wire_chat_unify", "label": "Wire Chat Unify", "method": "POST", "tier": "heavy", "desc": "Chat Unify · n8n merge wire"},
        ],
    },
    "cloud-workers": {
        "title": "Cloud Workers Command Center",
        "port": CLOUD_PORT,
        "hub": "H1",
        "api_base": f"http://127.0.0.1:{CLOUD_PORT}/api/api-station/v1",
    },
}


def _normalize_app_id(app_id: str) -> str:
    raw = (app_id or "").strip().lower()
    aliases = {
        "cloud_workers": "cloud-workers",
        "n8n_integration": "n8n-integration",
        "chat_unify": "chat-unify",
        "portfolio_mail": "portfolio-mail",
        "hub_form": "hub-form",
    }
    return aliases.get(raw, raw)


def station_manifest(app_id: str) -> dict[str, Any]:
    app_id = _normalize_app_id(app_id)
    spec = STATIONS.get(app_id)
    if not spec:
        return {"ok": False, "error": "unknown_app", "app_id": app_id, "known": list(STATIONS.keys())}
    health_url = f"http://127.0.0.1:{spec['port']}/health"
    up = _probe(health_url)
    if app_id in ("worker-hub", "machine-hub", "founder-ops", "hub-form", "cloud-workers"):
        from founder_ops_v1 import station_tasks  # noqa: WPS433

        tasks = station_tasks(app_id.replace("cloud-workers", "cloud_workers"))
    else:
        tasks = spec.get("tasks") or []
    hub = spec.get("hub") or ""
    return {
        "ok": True,
        "schema": "api-station-v1",
        "at": _now(),
        "app_id": app_id,
        "title": spec["title"],
        "port": spec["port"],
        "hub": hub,
        "service_up": up,
        "api_base": spec["api_base"],
        "founder_ops_api": f"http://127.0.0.1:{HUB_PORT}/api/founder-ops/v1",
        "post_shape": {"task": "<task_id>", "payload": {}},
        "tasks": tasks,
        "founder_line": (
            f"API Station · {spec['title']} · tap Run or POST task id · "
            "light=seconds · heavy=up to 3 min · no Worker chat"
        ),
    }


def _exec_founder_ops(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    from founder_ops_v1 import run_op  # noqa: WPS433

    return run_op(task, payload)


def _exec_portfolio_mail(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    base = f"http://127.0.0.1:{HUB_PORT}"
    if task == "integration_status":
        r = _http_json(f"{base}/api/portfolio-mail/v1/integration")
        return {"ok": bool(r.get("ok")), "task": task, "result": r.get("body") or r}
    if task == "wire_stack":
        return _exec_founder_ops("wire_stack", payload)
    if task == "refresh_inboxes":
        r = _http_json(f"{base}/api/portfolio-mail/v1?limit=8")
        return {"ok": bool(r.get("ok")), "task": task, "result": r.get("body") or r}
    return {"ok": False, "error": "unknown_task", "task": task}


def _exec_chat_unify(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    base = f"http://127.0.0.1:{CHAT_PORT}"
    if task == "report":
        r = _http_json(f"{base}/api/chat-unify")
        return {"ok": bool(r.get("ok")), "task": task, "result": r.get("body") or r}
    if task == "merge_all":
        r = _http_json(f"{base}/api/chat-unify", method="POST", body={"action": "merge_all", **payload}, timeout=180.0)
        return {"ok": bool(r.get("ok")), "task": task, "result": r.get("body") or r}
    if task == "stack_status":
        return _exec_founder_ops("stack_status", payload)
    return {"ok": False, "error": "unknown_task", "task": task}


def _cloud_task_action(task: str) -> str | None:
    mapping = {
        "cloud_workers_situation": "situation",
        "cloud_workers_status": "status",
        "cloud_workers_plans": "plans",
        "cloud_workers_inbox": "inbox",
        "cloud_workers_events": "events",
        "cloud_workers_cli": "cli",
        "cloud_workers_probe": "probe",
        "cloud_workers_dry_run": "dry_run",
        "cloud_proceed_dry_cloud": "proceed_dry_cloud",
        "cloud_skip_head": "skip_head",
        "cloud_skip_to_next_real": "skip_to_next_real",
        "cloud_auto_tick": "auto_tick",
        "cloud_deploy_instructions": "deploy_instructions",
        "cloud_proceed_dry": "proceed_dry_cloud",
        "cloud_skip_to_next_real": "skip_to_next_real",
        "cloud_auto_tick": "auto_tick",
    }
    return mapping.get(task)


def _exec_cloud_workers(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    action = _cloud_task_action(task)
    if not action:
        return {"ok": False, "error": "unknown_task", "task": task}
    try:
        from cloud_workers_hub_v1 import handle_action  # noqa: WPS433

        body = dict(payload or {})
        body["action"] = action
        if task in ("cloud_proceed_dry_cloud", "cloud_proceed_dry"):
            body.setdefault("dry_run", True)
            body.setdefault("llm_provider", body.get("llm_provider") or "openrouter")
        if task == "cloud_auto_tick":
            from cloud_drain_auto_runtime_v1 import run_auto_tick  # noqa: WPS433

            result = run_auto_tick(force=bool(payload.get("force")))
            return {"ok": bool(result.get("ok", True)), "task": task, "result": result}
        result = handle_action(body)
        return {"ok": bool(result.get("ok", True)), "task": task, "result": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300], "task": task}


def _exec_n8n_integration(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    action_map = {
        "report": "report",
        "capture_intelligence": "capture_intelligence",
        "wire_portfolio_mail": "wire_portfolio_mail",
        "wire_chat_unify": "wire_chat_unify",
    }
    action = action_map.get(task)
    if not action:
        return {"ok": False, "error": "unknown_task", "task": task}
    try:
        from n8n_integration_core import handle_action  # noqa: WPS433

        body = handle_action({"action": action, **payload})
        return {"ok": bool(body.get("ok")), "task": task, "result": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300], "task": task}


EXECUTORS = {
    "worker-hub": _exec_founder_ops,
    "machine-hub": _exec_founder_ops,
    "founder-ops": _exec_founder_ops,
    "portfolio-mail": _exec_portfolio_mail,
    "chat-unify": _exec_chat_unify,
    "n8n-integration": _exec_n8n_integration,
    "cloud-workers": _exec_cloud_workers,
}


def _task_meta(app_id: str, task: str) -> dict[str, str]:
    if app_id in ("worker-hub", "machine-hub", "founder-ops", "hub-form", "cloud-workers"):
        from founder_ops_v1 import CATALOG  # noqa: WPS433

        row = next((r for r in CATALOG if r["id"] == task), None)
        if row:
            return {"tier": row["tier"], "label": row["label"]}
    spec = STATIONS.get(app_id) or {}
    row = next((t for t in (spec.get("tasks") or []) if t.get("id") == task), None)
    if row:
        return {"tier": str(row.get("tier") or "light"), "label": str(row.get("label") or task)}
    return {"tier": "light", "label": task}


def run_task(
    app_id: str,
    task: str,
    payload: dict[str, Any] | None = None,
    *,
    async_run: bool = False,
) -> dict[str, Any]:
    app_id = _normalize_app_id(app_id)
    payload = payload or {}
    if app_id not in EXECUTORS:
        return {"ok": False, "error": "unknown_app", "app_id": app_id}
    if app_id in ("worker-hub", "machine-hub", "founder-ops", "hub-form"):
        from founder_ops_v1 import CATALOG  # noqa: WPS433

        valid = {r["id"] for r in CATALOG}
        if app_id == "worker-hub":
            valid = {t["id"] for t in _founder_hub_tasks("H1")}
        elif app_id == "machine-hub":
            valid = {t["id"] for t in _founder_hub_tasks("H2")}
    elif app_id == "cloud-workers":
        from founder_ops_v1 import station_tasks  # noqa: WPS433

        valid = {t["id"] for t in station_tasks("cloud_workers")}
    else:
        valid = {t["id"] for t in STATIONS[app_id].get("tasks") or []}
    if task not in valid:
        return {"ok": False, "error": "unknown_task", "task": task, "valid": sorted(valid)}
    meta = _task_meta(app_id, task)
    tier = meta.get("tier") or "light"
    label = meta.get("label") or task

    def _runner() -> dict[str, Any]:
        try:
            result = EXECUTORS[app_id](task, payload)
            result.setdefault("schema", "api-station-v1")
            result.setdefault("app_id", app_id)
            result.setdefault("task", task)
            result.setdefault("at", _now())
            return result
        except Exception as exc:
            return {"ok": False, "error": str(exc), "app_id": app_id, "task": task}

    from api_station_terminal_v1 import run_with_terminal, start_async_run  # noqa: WPS433

    if async_run or tier == "heavy":
        return start_async_run(app_id=app_id, task=task, tier=tier, label=label, runner=_runner)
    return run_with_terminal(app_id=app_id, task=task, tier=tier, label=label, runner=_runner)


def handle_terminal_get(*, lines: int = 120) -> dict[str, Any]:
    from api_station_terminal_v1 import terminal_tail  # noqa: WPS433

    return terminal_tail(lines=lines)


def handle_get(*, app_id: str, query: dict[str, str] | None = None) -> dict[str, Any]:
    app_id = _normalize_app_id(app_id)
    query = query or {}
    if query.get("task"):
        return run_task(app_id, query["task"], {})
    return station_manifest(app_id)


def handle_post(*, app_id: str, body: dict[str, Any]) -> dict[str, Any]:
    app_id = _normalize_app_id(app_id)
    task = str(body.get("task") or "").strip()
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    if not task:
        return {"ok": False, "error": "task_required", "hint": "POST { task: '<id>', payload: {} }"}
    return run_task(app_id, task, payload, async_run=bool(body.get("async")))


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="API Station v1")
    ap.add_argument("--app", required=True)
    ap.add_argument("--task")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.task:
        out = run_task(args.app, args.task)
    else:
        out = station_manifest(args.app)
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
