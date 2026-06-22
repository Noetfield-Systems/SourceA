#!/usr/bin/env python3
"""Unified task/plan priority — smart rank for agents and machines.

SSOT: data/sourcea-task-plan-priority-v1.json
Receipt: ~/.sina/task-plan-priority-receipt-v1.json

Pairs with task_plan_validation (next_task_trigger_v1.py):
  P0 form → P1 cloud FORGE → P2 Noetfield → P3 TrustField/GTM → P4 brain meta
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/sourcea-task-plan-priority-v1.json"
RECEIPT = SINA / "task-plan-priority-receipt-v1.json"
BRAIN = ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"
DRAIN = ROOT / "data/secondary-cloud-drain-next-100-v1.json"
FULL_STACK = ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json"
OUTBOUND = ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"
ECO111 = ROOT / "data/ecosystem-mac-health-111-upgrade-plan-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read(SSOT)


def _disk_blockers() -> list[str]:
    blocked: list[str] = []
    fn = _read(SINA / "factory-now-v1.json")
    if str(fn.get("mode") or "").upper() == "FREEZE":
        blocked.append("factory_FREEZE")
    loop = _read(SINA / "loop-specialist-config-v1.json")
    if loop.get("loop_auto_dispatch_enabled") and str(fn.get("mode") or "").upper() == "FREEZE":
        blocked.append("loop_blocked")
    return blocked


def _classify_output(*, action: str, title: str, tier: str = "", lane: str = "") -> str:
    blob = f"{action} {title} {lane}".lower()
    if any(x in blob for x in ("hub ux", "preview", "deploy preview", "onboarding", "landing", "saas", "agent product")):
        return "ai_agent_product"
    if any(x in blob for x in ("marketing", "gtm", "copy", "price card", "plg", "outreach", "demo")):
        return "marketing_system"
    if any(x in blob for x in ("fetch", "evidence", "row", "json", "pipeline", "ledger", "supabase", "labs")):
        return "data_pipeline"
    if any(x in blob for x in ("receipt", "validate", "pass/fail", "theater", "brain maps", "governance meta", "mac control")):
        return "internal_meta"
    if any(x in blob for x in ("write", "generate", "file", "manifest", "schema", ".md", ".json")):
        return "file_generation"
    if tier in ("T1", "T2", "T3") and "cloud" in blob:
        return "ai_agent_product"
    return "unknown"


def _map_unified_priority(
    ssot: dict,
    *,
    lane: str,
    output_type: str,
    plane: str = "",
) -> dict:
    stack = ssot.get("priority_stack") or []
    lane_l = lane.lower()
    plane_l = plane.lower()
    for row in stack:
        lanes = [str(x).lower() for x in (row.get("lanes") or [])]
        outs = row.get("output_types") or []
        if any(l in lane_l or l in plane_l for l in lanes):
            return row
        if output_type in outs:
            return row
    if output_type in ("ai_agent_product", "data_pipeline"):
        return next((r for r in stack if r.get("id") == "P1"), stack[1] if len(stack) > 1 else {})
    if output_type == "marketing_system":
        return next((r for r in stack if r.get("id") == "P3"), stack[3] if len(stack) > 3 else {})
    if output_type == "internal_meta":
        return next((r for r in stack if r.get("id") == "P4"), stack[-1] if stack else {})
    return stack[1] if len(stack) > 1 else (stack[0] if stack else {})


def _disk_head() -> str:
    return str(_read(SINA / "phase-observed-v1.json").get("cloud_drain_head") or "CLOUD-SEC-001")


def score_task(
    ssot: dict,
    task: dict[str, Any],
    *,
    blockers: list[str] | None = None,
    paired_registry: str = "",
    drain_head: str = "",
) -> dict[str, Any]:
    blockers = blockers if blockers is not None else _disk_blockers()
    action = str(task.get("action") or task.get("cloud_action") or task.get("acceptance") or "")
    title = str(task.get("title") or "")
    lane = str(task.get("lane") or task.get("workstream") or task.get("source") or "")
    plane = str(task.get("plane") or "")
    tier = str(task.get("tier") or "")

    output_type = _classify_output(action=action, title=title, tier=tier, lane=lane)
    pri_row = _map_unified_priority(ssot, lane=lane, output_type=output_type, plane=plane)

    base = int((ssot.get("output_type_scores") or {}).get(output_type, 100))
    rank_bonus = max(0, 500 - int(pri_row.get("rank", 4)) * 100)
    score = base + rank_bonus

    if plane == "cloud_forge":
        score += 120
    elif plane == "mac_control":
        score -= 250
    if tier in ("T1", "T2"):
        score += 60
    if paired_registry:
        score += 100

    verdict_adj = ssot.get("verdict_adjustments") or {}
    meta_only = output_type == "internal_meta" and not paired_registry
    if meta_only:
        score += int(verdict_adj.get("noise", -600))
    elif blockers:
        score += int(verdict_adj.get("blocked", -400))
    else:
        score += int(verdict_adj.get("useful", 80))

    for b in blockers:
        score += int((ssot.get("blocker_penalties") or {}).get(b, -100))

    cost_tier = str(task.get("cost_tier") or "").lower()
    cost_boost = (ssot.get("cost_intelligence") or {}).get("cost_tier_boost") or {}
    if cost_tier in cost_boost:
        score += int(cost_boost[cost_tier])

    tid = str(task.get("task_id") or task.get("id") or "")
    head = drain_head or _disk_head()
    seq = ssot.get("sequential_drain_law") or {}
    if tid == head:
        score += int(seq.get("head_bonus") or 500)
        sequential = "drain_head"
    elif str(task.get("source")) == "cloud_drain" and tid.startswith("CLOUD-SEC-"):
        sequential = "cloud_drain_ahead"
    else:
        sequential = "other"

    return {
        "task_id": task.get("task_id") or task.get("id"),
        "title": title[:120] or action[:120],
        "source": task.get("source"),
        "lane": lane,
        "plane": plane,
        "output_type": output_type,
        "unified_priority": pri_row.get("id"),
        "priority_label": pri_row.get("label"),
        "score": score,
        "blocked": bool(blockers),
        "paired_registry": paired_registry or None,
        "maps_registry": task.get("maps_registry") or paired_registry or None,
        "sequential_role": sequential,
        "cost_tier": cost_tier or None,
    }


def _brain_open(limit: int = 5) -> list[dict]:
    plan = _read(BRAIN)
    out: list[dict] = []
    for u in plan.get("upgrades") or []:
        if str(u.get("status") or "") in ("planned", "pending", "open"):
            out.append(
                {
                    "id": u.get("id"),
                    "task_id": u.get("id"),
                    "title": u.get("title"),
                    "action": u.get("acceptance"),
                    "lane": u.get("lane") or "brain",
                    "tier": u.get("tier"),
                    "source": "brain_cloud_1000",
                    "maps_registry": u.get("maps_registry"),
                }
            )
            if len(out) >= limit:
                break
    return out


def _cloud_from_head(limit: int = 5) -> list[dict]:
    drain = _read(DRAIN)
    obs = _read(SINA / "phase-observed-v1.json")
    head = str(obs.get("cloud_drain_head") or "CLOUD-SEC-001")
    plans = drain.get("plans") or []
    ids = [str(p.get("id") or "") for p in plans if str(p.get("id", "")).startswith("CLOUD-SEC-")]
    out: list[dict] = []
    if head in ids:
        idx = ids.index(head)
        slice_ids = ids[idx : idx + limit]
    else:
        slice_ids = ids[:limit]
    for cid in slice_ids:
        row = next((p for p in plans if p.get("id") == cid), None)
        if row:
            out.append(
                {
                    **row,
                    "task_id": row.get("id"),
                    "title": row.get("cloud_action"),
                    "action": row.get("cloud_action"),
                    "lane": row.get("workstream") or "cloud_forge",
                    "source": "cloud_drain",
                }
            )
    return out


def _plan_slice(path: Path, *, item_key: str, source: str, lane: str, limit: int = 3) -> list[dict]:
    plan = _read(path)
    out: list[dict] = []
    for row in plan.get(item_key) or []:
        st = str(row.get("status") or "")
        if st in ("done", "shipped", "complete"):
            continue
        out.append(
            {
                "id": row.get("id"),
                "task_id": row.get("id"),
                "title": row.get("title") or row.get("acceptance"),
                "action": row.get("acceptance") or row.get("work_template") or row.get("title"),
                "lane": lane,
                "tier": row.get("tier"),
                "source": source,
            }
        )
        if len(out) >= limit:
            break
    return out


def collect_candidates(*, per_source: int = 3) -> list[dict]:
    cands: list[dict] = []
    cands.extend(_brain_open(limit=per_source))
    cands.extend(_cloud_from_head(limit=per_source))
    cands.extend(_plan_slice(FULL_STACK, item_key="fixes", source="full_stack_100", lane="full_stack", limit=2))
    cands.extend(_plan_slice(OUTBOUND, item_key="upgrades", source="outbound_100", lane="outbound", limit=2))
    cands.extend(_plan_slice(ECO111, item_key="upgrades", source="ecosystem_m111", lane="mac_health", limit=2))
    return cands


def smart_rank(*, limit: int = 12) -> list[dict]:
    ssot = load_ssot()
    blockers = _disk_blockers()
    head = _disk_head()
    ranked: list[dict] = []
    for task in collect_candidates():
        reg = str(task.get("maps_registry") or "")
        if not reg and str(task.get("source")) == "brain_cloud_1000":
            drain = _read(DRAIN)
            nxt = next((p for p in (drain.get("plans") or []) if p.get("id") == head), {})
            if nxt.get("maps_registry"):
                reg = str(nxt["maps_registry"])
        scored = score_task(
            ssot, task, blockers=blockers, paired_registry=reg, drain_head=head
        )
        scored["brain_pair"] = bool(reg and str(task.get("source")) == "brain_cloud_1000")
        ranked.append(scored)
    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
    return ranked[:limit]


def sequential_next() -> dict | None:
    head = _disk_head()
    drain = _read(DRAIN)
    row = next((p for p in (drain.get("plans") or []) if p.get("id") == head), None)
    if not row:
        return None
    ssot = load_ssot()
    task = {
        **row,
        "task_id": row.get("id"),
        "title": row.get("cloud_action"),
        "action": row.get("cloud_action"),
        "lane": row.get("workstream") or "cloud_forge",
        "source": "cloud_drain",
    }
    return score_task(
        ssot,
        task,
        blockers=_disk_blockers(),
        paired_registry=str(row.get("maps_registry") or ""),
        drain_head=head,
    )


def priority_for_task_id(task_id: str) -> dict:
    ssot = load_ssot()
    blockers = _disk_blockers()
    tid = task_id.strip()
    task: dict[str, Any] = {"task_id": tid, "source": "explicit"}
    if tid.upper().startswith("B"):
        u = next((x for x in (_read(BRAIN).get("upgrades") or []) if str(x.get("id")).upper() == tid.upper()), {})
        task = {**u, "task_id": u.get("id"), "source": "brain_cloud_1000", "lane": "brain"}
    elif tid.startswith("CLOUD-SEC"):
        row = next((p for p in (_read(DRAIN).get("plans") or []) if p.get("id") == tid), {})
        task = {**row, "task_id": row.get("id"), "title": row.get("cloud_action"), "action": row.get("cloud_action"), "source": "cloud_drain"}
    elif tid.startswith("sa-mkt"):
        row = next((p for p in (_read(DRAIN).get("plans") or []) if p.get("maps_registry") == tid), {})
        task = {**row, "task_id": row.get("id"), "title": row.get("cloud_action"), "action": row.get("cloud_action"), "source": "cloud_drain"}
    reg = str(task.get("maps_registry") or "")
    return score_task(ssot, task, blockers=blockers, paired_registry=reg)


def _summary_line(ranked: list[dict], smart_pick: dict | None, seq: dict | None) -> str:
    sp = smart_pick or {}
    sn = seq or {}
    return (
        f"task-priority · seq={sn.get('task_id')} · smart={sp.get('task_id')} · "
        f"{sp.get('unified_priority')} · output={sp.get('output_type')} · score={sp.get('score')}"
    )


def refresh(*, write: bool = True) -> dict:
    ssot = load_ssot()
    ranked = smart_rank(limit=15)
    seq_row = sequential_next()
    smart_pick = ranked[0] if ranked else {}
    if seq_row and seq_row.get("sequential_role") == "drain_head":
        smart_pick = seq_row
    blockers = _disk_blockers()
    row = {
        "schema": "task-plan-priority-receipt-v1",
        "version": ssot.get("version", "1.1.0"),
        "at": _now(),
        "ok": True,
        "one_law": ssot.get("one_law"),
        "blockers": blockers,
        "cloud_drain_head": _disk_head(),
        "sequential_next": seq_row,
        "smart_pick": smart_pick,
        "ranked": ranked,
        "priority_stack": ssot.get("priority_stack"),
        "vocabulary_map": ssot.get("vocabulary_map"),
        "task_plan_priority_line": _summary_line(ranked, smart_pick, seq_row),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def inject_slice() -> dict:
    ssot = load_ssot()
    row = _read(RECEIPT) if RECEIPT.is_file() else refresh(write=False)
    return {
        "one_law": ssot.get("one_law"),
        "priority_stack": ssot.get("priority_stack"),
        "smart_pick": row.get("smart_pick"),
        "sequential_next": row.get("sequential_next"),
        "cloud_drain_head": row.get("cloud_drain_head"),
        "top_ranked": (row.get("ranked") or [])[:5],
        "task_plan_priority_line": row.get("task_plan_priority_line"),
        "command_refresh": "python3 scripts/task_plan_priority_v1.py --refresh --json",
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified task/plan smart priority v1")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--rank", action="store_true")
    ap.add_argument("--task-id", default="")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.inject:
        row = inject_slice()
    elif args.task_id:
        row = {"ok": True, "priority": priority_for_task_id(args.task_id)}
    elif args.refresh or args.rank:
        row = refresh(write=True)
    else:
        row = refresh(write=False)

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("task_plan_priority_line") or row.get("command_refresh") or json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
