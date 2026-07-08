#!/usr/bin/env python3
"""Founder Ops — one catalog of Hub-runnable checks, heals, pipelines, machines.

GET  /api/founder-ops/v1           — full manifest (grouped)
POST /api/founder-ops/v1           — { "op": "<id>", "payload": {} }
API Station worker-hub / machine-hub — filtered task lists call run_op().

Law: founder runs via Hub · Machines · API — not Worker chat on Mac.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
HUB = f"http://127.0.0.1:{HUB_PORT}"

# id · label · tier (light|heavy) · hub (H1|H2|both) · category · desc
CATALOG: list[dict[str, str]] = [
    # — H1 health & sync —
    {"id": "stack_status", "label": "Portfolio stack status", "tier": "light", "hub": "both", "category": "stack", "desc": "Hub · Mail · Chat · N8N · Mac Law wire state"},
    {"id": "wire_stack", "label": "Wire all portfolio apps", "tier": "light", "hub": "both", "category": "stack", "desc": "Integration wire across portfolio stack"},
    {"id": "worker_snapshot", "label": "Worker Hub snapshot", "tier": "light", "hub": "H1", "category": "refresh", "desc": "GET /api/worker-hub/v1 — live H1 payload"},
    {"id": "machine_snapshot", "label": "Machine Hub snapshot", "tier": "light", "hub": "H2", "category": "refresh", "desc": "GET /api/machine-hub/v1 — H2 pending registry"},
    {"id": "light_refresh", "label": "Light refresh (H1)", "tier": "light", "hub": "H1", "category": "refresh", "desc": "Align shell generation · no monolith rebuild"},
    {"id": "heal", "label": "Auto-heal H1", "tier": "light", "hub": "H1", "category": "anti-staleness", "desc": "Anti-staleness · hung kill · hub heal · inbox latch"},
    {"id": "heal_deep", "label": "Deep heal H1", "tier": "heavy", "hub": "H1", "category": "anti-staleness", "desc": "Heal + stuck recovery (use when heal alone fails)"},
    {"id": "dual_heal", "label": "Dual-hub heal (H1+H2)", "tier": "light", "hub": "both", "category": "anti-staleness", "desc": "H1 worker heal · H2 registry sync · agentic pipeline fast"},
    {"id": "h2_registry_sync", "label": "H2 registry sync", "tier": "light", "hub": "H2", "category": "machines", "desc": "Sync h2-pending-registry from disk truth"},
    {"id": "staleness_h1", "label": "H1 staleness probe", "tier": "light", "hub": "H1", "category": "anti-staleness", "desc": "Read-only freshness · factory-now · latches"},
    {"id": "staleness_h2", "label": "H2 staleness probe", "tier": "light", "hub": "H2", "category": "anti-staleness", "desc": "Read-only H2 registry freshness"},
    {"id": "disk_live_wire", "label": "Disk live wire sync", "tier": "light", "hub": "both", "category": "anti-staleness", "desc": "agent-live-surfaces · truth bundle · worker context"},
    {"id": "safety_check", "label": "Ecosystem safety check", "tier": "light", "hub": "H1", "category": "validators", "desc": "H1 safety gate · no validator marathon"},
    # — Cloud —
    {"id": "cloud_workers_situation", "label": "Cloud situation card", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Pipe · queue head · last proceed · failure class"},
    {"id": "cloud_workers_status", "label": "Cloud Workers full status", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Situation + plans + inbox + events + CLI bundle"},
    {"id": "cloud_workers_plans", "label": "Cloud plans queue", "tier": "light", "hub": "H1", "category": "cloud", "desc": "MAC-CTL + CLOUD-SEC organized with status"},
    {"id": "cloud_workers_inbox", "label": "Cloud inbox", "tier": "light", "hub": "H1", "category": "cloud", "desc": "P0 head row + upcoming — not Worker RUN INBOX"},
    {"id": "cloud_workers_events", "label": "Cloud event log", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Proceed · skip · dispatch timeline"},
    {"id": "cloud_workers_cli", "label": "Cloud CLI catalog", "tier": "light", "hub": "H1", "category": "cloud", "desc": "All founder CLI + curl commands"},
    {"id": "cloud_proceed_dry_cloud", "label": "Cloud proceed dry-run (Railway)", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Dry-run on Railway via Hub proxy"},
    {"id": "cloud_skip_head", "label": "Skip cloud queue head", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Advance CLOUD-SEC head when motor blocked"},
    {"id": "cloud_skip_to_next_real", "label": "Skip to next real row", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Skip mock_only scaffold rows until shippable head"},
    {"id": "cloud_auto_tick", "label": "Auto Runtime tick", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Auto skip mock · self-heal · optional Cloud Forge Run"},
    {"id": "cloud_workers_probe", "label": "Cloud Workers probe", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Deep probe proceed module on Railway"},
    {"id": "cloud_workers_dry_run", "label": "Cloud queue dry-run (Mac)", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Resolve next CLOUD-SEC row on Mac only — no motor"},
    {"id": "cloud_deploy_instructions", "label": "Railway deploy command", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Show deploy_fbe_railway_v1 command — founder runs, not agents"},
    {"id": "cloud_proceed_dry", "label": "Cloud proceed dry-run", "tier": "light", "hub": "H1", "category": "cloud", "desc": "Mac→Railway proceed preview · CLOUD-SEC next row"},
    # — Pipelines & loops —
    {"id": "loop_chain", "label": "Loop chain (full tick)", "tier": "heavy", "hub": "H1", "category": "pipelines", "desc": "Observatory · investigator · judge · specialist · routing · disclosure · MCP · tool pick · anti-theater · plans · WTM"},
    {"id": "plans_unified", "label": "Plans unified sync", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Outbound 100 · full-stack 100 · brain 1000 smart pick"},
    {"id": "world_model", "label": "World model plan check", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Platform-neutral WTM · plan alignment"},
    {"id": "anti_theater", "label": "Anti-theater loop", "tier": "light", "hub": "H1", "category": "validators", "desc": "Noise vs useful · cloud proof honesty"},
    {"id": "pipeline_graph", "label": "Node graph T3 proof", "tier": "heavy", "hub": "H1", "category": "pipelines", "desc": "Pipeline node graph parallel proof tier"},
    {"id": "loop_specialist", "label": "Auto Runtime specialist tick", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "ASF resume Cloud Forge Run · queue specialist"},
    {"id": "investigator", "label": "Investigator tick", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Investigator circle room"},
    {"id": "judge_loop", "label": "Judge loop tick", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Judge loop room verdict"},
    {"id": "routing_panel", "label": "Routing panel refresh", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Founder routing panel · brands · chain"},
    {"id": "disclosure_ladder", "label": "Disclosure ladder audit", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Public voice · ICP audit"},
    {"id": "mcp_stack", "label": "MCP stack audit", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Free tier MCP servers"},
    {"id": "tool_pick", "label": "Tool pick audit", "tier": "light", "hub": "H1", "category": "pipelines", "desc": "Free-first tool pick · founder approval queue"},
    {"id": "outbound_coherence", "label": "Outbound disk coherence", "tier": "light", "hub": "H1", "category": "validators", "desc": "Queue · receipt path coherence heal"},
    {"id": "agentic_pipeline", "label": "Agentic layer pipeline", "tier": "light", "hub": "both", "category": "pipelines", "desc": "L0.5 fast tier · brain L2 wire"},
    # — Governance / zero drift —
    {"id": "governance_drift", "label": "Zero drift report", "tier": "light", "hub": "both", "category": "governance", "desc": "Governance drift engine · SSOT alignment"},
    {"id": "governance_unify", "label": "Governance unify scan", "tier": "light", "hub": "both", "category": "governance", "desc": "Agent governance unification read"},
    # — H2 machines —
    {"id": "run_judge", "label": "Run Judge Center", "tier": "heavy", "hub": "H2", "category": "machines", "desc": "Weekly judge room machine"},
    {"id": "run_thread", "label": "Run Thread Room", "tier": "heavy", "hub": "H2", "category": "machines", "desc": "Weekly thread curation machine"},
    {"id": "run_both_rooms", "label": "Run Judge + Thread", "tier": "heavy", "hub": "H2", "category": "machines", "desc": "Both weekly review machines"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hub_json(path: str, *, method: str = "GET", body: dict | None = None, timeout: float = 120.0) -> dict[str, Any]:
    from api_station_terminal_v1 import active_emit  # noqa: WPS433

    active_emit(f"→ {method} {HUB}{path} (timeout {int(timeout)}s)")
    stop = threading.Event()

    def _heartbeat() -> None:
        elapsed = 0
        while not stop.wait(3.0):
            elapsed += 3
            active_emit(f"  … {elapsed}s elapsed")

    pulse = threading.Thread(target=_heartbeat, daemon=True)
    pulse.start()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{HUB}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw.strip() else {}
            row = {"ok": resp.status < 400 and parsed.get("ok", True), "status": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw[:800]}
        row = {"ok": False, "status": exc.code, "body": parsed, "error": str(exc)}
    except Exception as exc:
        row = {"ok": False, "error": str(exc), "path": path}
    finally:
        stop.set()

    active_emit(f"  ← HTTP {row.get('status', '—')} ok={row.get('ok')}")
    body_out = row.get("body") or {}
    if isinstance(body_out, dict):
        steps = body_out.get("steps")
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict):
                    name = step.get("step") or step.get("name") or "step"
                    ok = step.get("ok")
                    mark = "PASS" if ok else "FAIL" if ok is False else "—"
                    err = f" — {step.get('error')}" if step.get("error") else ""
                    active_emit(f"    [{mark}] {name}{err}")
        show = (body_out.get("for_founder") or {}).get("show_this")
        if show:
            active_emit(f"    · {show}")
    if row.get("error"):
        active_emit(f"  [ERROR] {row.get('error')}")
    return row


def _py(mod: str, fn: str, **kwargs: Any) -> dict[str, Any]:
    from api_station_terminal_v1 import active_emit  # noqa: WPS433

    active_emit(f"→ python {mod}.{fn}()")
    sys.path.insert(0, str(SCRIPTS))
    import importlib

    m = importlib.import_module(mod)
    row = getattr(m, fn)(**kwargs)
    out = row if isinstance(row, dict) else {"ok": True, "result": row}
    active_emit(f"  ← ok={out.get('ok', True)}")
    return out


def manifest(*, hub: str | None = None) -> dict[str, Any]:
    rows = CATALOG
    if hub:
        rows = [r for r in rows if r["hub"] == hub or r["hub"] == "both"]
    by_cat: dict[str, list] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    return {
        "ok": True,
        "schema": "founder-ops-v1",
        "at": _now(),
        "hub_filter": hub,
        "ops": rows,
        "by_category": by_cat,
        "post_shape": {"op": "<id>", "payload": {}},
        "api": "/api/founder-ops/v1",
        "founder_line": "Founder Ops · run checks · heals · pipelines from Hub — no Worker chat required",
    }


def _tasks_for_station(hub: str) -> list[dict[str, str]]:
    out = []
    for r in CATALOG:
        if r["hub"] not in (hub, "both"):
            continue
        out.append(
            {
                "id": r["id"],
                "label": r["label"],
                "method": "POST",
                "tier": r["tier"],
                "category": r["category"],
                "desc": f"[{r['tier']}] {r['desc']}",
            }
        )
    return out


def run_op(op_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    meta = next((r for r in CATALOG if r["id"] == op_id), None)
    if not meta:
        return {"ok": False, "error": "unknown_op", "op": op_id, "known": [r["id"] for r in CATALOG]}

    t0 = _now()
    try:
        result = _dispatch(op_id, payload)
    except Exception as exc:
        return {
            "ok": False,
            "schema": "founder-ops-run-v1",
            "op": op_id,
            "tier": meta["tier"],
            "hub": meta["hub"],
            "category": meta["category"],
            "error": str(exc)[:400],
            "at": t0,
        }

    ok = bool(result.get("ok", True))
    if "body" in result and isinstance(result["body"], dict):
        ok = bool(result["body"].get("ok", ok))
        result = result["body"]

    return {
        "ok": ok,
        "schema": "founder-ops-run-v1",
        "op": op_id,
        "label": meta["label"],
        "tier": meta["tier"],
        "hub": meta["hub"],
        "category": meta["category"],
        "at": _now(),
        "started_at": t0,
        "result": result,
    }


def _dispatch(op_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if op_id == "stack_status":
        return _hub_json("/api/portfolio-mail/v1/integration")
    if op_id == "wire_stack":
        return _py("portfolio_mail_integration_wire_v1", "wire_all")
    if op_id == "worker_snapshot":
        return _hub_json("/api/worker-hub/v1", timeout=60.0)
    if op_id == "machine_snapshot":
        return _hub_json("/api/machine-hub/v1")
    if op_id == "light_refresh":
        return _hub_json("/refresh", method="POST", body={"mode": "light"})
    if op_id == "heal":
        return _hub_json(
            "/api/worker-hub/heal",
            method="POST",
            body={"reason": payload.get("reason") or "founder-api", "force": True},
        )
    if op_id == "heal_deep":
        return _hub_json(
            "/api/worker-hub/heal",
            method="POST",
            body={"reason": "founder-deep", "force": True, "deep": True, "full": True},
            timeout=180.0,
        )
    if op_id == "dual_heal":
        return _py("hub_dual_heal_v1", "heal_two_hubs", reason=payload.get("reason") or "founder-api", full=bool(payload.get("full")))
    if op_id == "h2_registry_sync":
        row = _py("h2_pending_registry_sync_v1", "sync_h2_registry", caller="founder-ops")
        _py("machine_hub_v1", "invalidate_machine_hub_cache")
        return row
    if op_id == "staleness_h1":
        return _py("worker_hub_staleness_v1", "staleness_probe")
    if op_id == "staleness_h2":
        return _py("machine_hub_staleness_v1", "machine_hub_staleness_probe")
    if op_id == "disk_live_wire":
        return _py("disk_live_wire_sync_v1", "sync_disk_live_wire", role="founder")
    if op_id == "safety_check":
        return _hub_json(
            "/api/worker-hub/heal",
            method="POST",
            body={"reason": "founder-ecosystem-safety"},
        )
    if op_id == "cloud_workers_situation":
        return _hub_json("/api/cloud-workers/v1", method="POST", body={"action": "situation"}, timeout=60.0)
    if op_id == "cloud_workers_plans":
        return _hub_json("/api/cloud-workers/v1", method="POST", body={"action": "plans"}, timeout=30.0)
    if op_id == "cloud_workers_inbox":
        return _hub_json("/api/cloud-workers/v1", method="POST", body={"action": "inbox"}, timeout=30.0)
    if op_id == "cloud_workers_events":
        return _hub_json("/api/cloud-workers/v1", method="POST", body={"action": "events"}, timeout=30.0)
    if op_id == "cloud_workers_cli":
        return _hub_json("/api/cloud-workers/v1", method="POST", body={"action": "cli"}, timeout=15.0)
    if op_id == "cloud_proceed_dry_cloud":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "proceed_dry_cloud", "llm_provider": payload.get("llm_provider") or "openrouter"},
            timeout=120.0,
        )
    if op_id == "cloud_skip_head":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "skip_head", "reason": payload.get("reason") or "founder_api_station"},
            timeout=30.0,
        )
    if op_id == "cloud_skip_to_next_real":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "skip_to_next_real", "reason": payload.get("reason") or "founder_api_station"},
            timeout=30.0,
        )
    if op_id == "cloud_auto_tick":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "auto_tick", "force": bool(payload.get("force"))},
            timeout=300.0,
        )
    if op_id == "cloud_workers_status":
        return _hub_json("/api/cloud-workers/v1", method="GET", timeout=90.0)
    if op_id == "cloud_workers_probe":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "probe"},
            timeout=90.0,
        )
    if op_id == "cloud_workers_dry_run":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "dry_run"},
            timeout=30.0,
        )
    if op_id == "cloud_deploy_instructions":
        return _hub_json(
            "/api/cloud-workers/v1",
            method="POST",
            body={"action": "deploy_instructions"},
            timeout=15.0,
        )
    if op_id == "cloud_proceed_dry":
        return _hub_json(
            "/api/cloud-forge-run/proceed/v1",
            method="POST",
            body={
                "dry_run": True,
                "llm_provider": payload.get("llm_provider") or "openrouter",
                "full_motor": True,
            },
            timeout=120.0,
        )
    if op_id == "loop_chain":
        return _hub_json("/api/loop-chain/tick/v1", method="POST", body={}, timeout=300.0)
    if op_id == "plans_unified":
        return _hub_json("/api/plans-unified/tick/v1", method="POST", body={})
    if op_id == "world_model":
        return _hub_json("/api/world-model-plan-check/tick/v1", method="POST", body={})
    if op_id == "anti_theater":
        return _py("anti_theater_validator_loop_v1", "run_loop", write=True)
    if op_id == "pipeline_graph":
        tier = str(payload.get("tier") or "T3_proof_parallel")
        return _hub_json("/api/pipeline-node-graph/run/v1", method="POST", body={"tier": tier}, timeout=180.0)
    if op_id == "loop_specialist":
        return _hub_json("/api/loop-specialist/tick/v1", method="POST", body=payload)
    if op_id == "investigator":
        return _hub_json("/api/investigator-circle/tick/v1", method="POST", body={})
    if op_id == "judge_loop":
        return _hub_json("/api/judge-loop/tick/v1", method="POST", body={})
    if op_id == "routing_panel":
        return _hub_json("/api/routing-panel/tick/v1", method="POST", body={})
    if op_id == "disclosure_ladder":
        return _hub_json("/api/disclosure-ladder/tick/v1", method="POST", body={})
    if op_id == "mcp_stack":
        return _hub_json("/api/mcp-stack/tick/v1", method="POST", body={})
    if op_id == "tool_pick":
        return _hub_json("/api/tool-pick/tick/v1", method="POST", body={})
    if op_id == "outbound_coherence":
        return _hub_json("/api/worker-hub/outbound-coherence-heal/v1", method="POST", body={})
    if op_id == "agentic_pipeline":
        return _py("agentic_layer_pipeline_v2", "run_agentic_pipeline_v2", sync_brain=False, tier="fast")
    if op_id == "governance_drift":
        return _py("governance_drift_engine", "run_drift_report", write_ssot=True)
    if op_id == "governance_unify":
        return _py("agent_governance_unification", "unification_payload")
    if op_id == "run_judge":
        return _hub_json("/api/worker-hub/rooms/run", method="POST", body={"room": "judge"}, timeout=180.0)
    if op_id == "run_thread":
        return _hub_json("/api/worker-hub/rooms/run", method="POST", body={"room": "thread"}, timeout=180.0)
    if op_id == "run_both_rooms":
        return _hub_json("/api/worker-hub/rooms/run", method="POST", body={"room": "both"}, timeout=300.0)
    return {"ok": False, "error": "unwired_op", "op": op_id}


def station_tasks(app_id: str) -> list[dict[str, str]]:
    """ASF full catalog on H1/H2/founder-ops stations — hub tag in desc."""
    if app_id in ("cloud_workers", "cloud-workers"):
        rows = [
            r
            for r in CATALOG
            if r.get("category") == "cloud" or str(r.get("id", "")).startswith("cloud_")
        ]
        return [
            {
                "id": r["id"],
                "label": r["label"],
                "method": "POST",
                "tier": r["tier"],
                "category": r["category"],
                "desc": f"[{r['tier']}] [{r['hub']}] {r['desc']}",
            }
            for r in rows
        ]
    if app_id in ("founder-ops", "machine-hub", "worker-hub", "hub-form", "hub_form"):
        return [
            {
                "id": r["id"],
                "label": r["label"],
                "method": "POST",
                "tier": r["tier"],
                "category": r["category"],
                "desc": f"[{r['tier']}] [{r['hub']}] {r['desc']}",
            }
            for r in CATALOG
        ]
    return _tasks_for_station("H1")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Founder ops v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--hub", choices=("H1", "H2", "both"))
    ap.add_argument("--op")
    ap.add_argument("--payload", default="{}")
    args = ap.parse_args()
    if args.op:
        payload = json.loads(args.payload)
        out = run_op(args.op, payload)
    else:
        out = manifest(hub=None if args.hub == "both" else args.hub)
    if args.json or args.op or args.manifest:
        print(json.dumps(out, indent=2))
    else:
        print(out.get("founder_line") or f"ops={len(CATALOG)}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
