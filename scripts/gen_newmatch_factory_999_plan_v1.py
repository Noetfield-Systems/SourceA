#!/usr/bin/env python3
"""Generate 999 UNIQUE NewMatch factory plans — free-tier first · cloud router · follow-up.

Law: data/newmatch-factory-v1.json · tool-pick-two-phase · tier-priority policy
OUT: data/newmatch-factory-999-plan-v1.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "newmatch-factory-999-plan-v1.json"
SSOT = ROOT / "data" / "newmatch-factory-v1.json"

PHASES = [
    ("P0-GRAPH", "People graph SSOT", 1, 150, "graph"),
    ("P0-ROUTER", "Situation router cloud API", 151, 300, "router"),
    ("P1-FOLLOW", "Agentic follow-up loops", 301, 500, "follow"),
    ("P1-INGEST", "Founder-approved ingest", 501, 650, "ingest"),
    ("P1-COST", "Affordable cost intelligence", 651, 750, "cost"),
    ("P2-HANDOFF", "Business lane handoffs", 751, 850, "handoff"),
    ("P2-WIRE", "Factory wire + governance", 851, 950, "wire"),
    ("P3-SCALE", "Learn · privacy · scale", 951, 999, "scale"),
]

MVP_WAVES = [
    ("W1", 1, 150),
    ("W2", 151, 300),
    ("W4", 301, 500),
    ("W3", 501, 650),
    ("W5", 751, 999),
]

SIGNALS = [
    "dating_mutual_like", "dating_message", "linkedin_connection", "linkedin_inmail",
    "calendar_overlap", "manual_note", "csv_import_row", "semej_capture",
]

ROUTES = [
    "personal_nurture", "hybrid_explore", "business_opportunity", "defer", "block", "founder_gate",
]

GRAPH_ENTITIES = ["person", "edge", "signal", "situation", "follow_up"]

VERBS = [
    "Define", "Wire", "Validate", "Deploy", "Prove", "Receipt", "Audit", "Sync",
    "Register", "Classify", "Route", "Defer", "Block", "Nurture", "Handoff",
    "Gate", "Cap", "Learn", "Encrypt", "Approve",
]

OBJECTS = [
    "people node schema",
    "situation card",
    "edge relationship",
    "dating-app signal",
    "linkedin signal",
    "calendar overlap",
    "manual paste intake",
    "SEMEJ read-only capture",
    "situation classifier T1",
    "follow-up loop NM-FOLLOW",
    "planner executor split",
    "cost tier T0 rule",
    "cost tier T1 classify",
    "cost tier T2 draft",
    "founder gate T3 send",
    "personal_nurture route",
    "hybrid_explore route",
    "business_opportunity route",
    "Noetfield NF-RD handoff",
    "TrustField TF-001 handoff",
    "SourceA agency handoff",
    "Supabase people graph",
    "FBE Railway /newmatch/route",
    "newmatch_router_cloud factory",
    "anti-theater personal outreach",
    "disclosure tier T4_internal",
    "PII encrypt at rest",
    "feedback loop routing weight",
    "monthly spend cap",
    "receipt chain integrity",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mvp_wave(seq: int) -> str:
    for wid, start, end in MVP_WAVES:
        if start <= seq <= end:
            return wid
    if 651 <= seq <= 750:
        return "W4"
    if 851 <= seq <= 950:
        return "W5"
    return "W5"


def _priority(seq: int, goal: str) -> int:
    if seq <= 40:
        return 1
    if seq in (150, 300, 500, 650, 750, 850, 950, 999):
        return 1
    if goal in ("graph", "router") and seq <= 300:
        return 2
    if goal in ("follow", "ingest"):
        return 3
    return 4


def _tier(seq: int, goal: str) -> str:
    if seq <= 300 or goal in ("graph", "router"):
        return "P0"
    if seq <= 750 or goal in ("follow", "ingest", "cost"):
        return "P1"
    return "P2"


def _title(seq: int, phase_label: str, goal: str) -> str:
    v = VERBS[(seq * 3) % len(VERBS)]
    o = OBJECTS[(seq * 7 + len(goal)) % len(OBJECTS)]
    return f"{v} {o} — {phase_label} step {seq}"


def _acceptance(seq: int, goal: str) -> str:
    free = "free-tier check PASS · $0 path exhausted before paid"
    base = {
        "graph": f"Schema logged · local JSON or Supabase free · {free}",
        "router": f"T0 rules first · :free LLM only if rules ambiguous · {free}",
        "follow": f"Planner→executor · default marginal_cost_usd=0 · {free}",
        "ingest": f"Manual/CSV/SEMEJ only · $0 ingest · {free}",
        "cost": f"T0→T1(:free) before T2 paid · phase_0 ceiling $0 · {free}",
        "handoff": f"founder_routing_panel SKU · founder gate · no paid outbound until gate",
        "wire": f"tool_pick phase_1_free wired · paid needs founder approval receipt",
        "scale": f"Feedback loop · privacy audit · {free}",
    }
    return f"{base.get(goal, 'Receipt filed')} · NM-{seq:03d}"


def _receipt(goal: str, seq: int) -> str:
    m = {
        "graph": "newmatch-graph-receipt-v1.json",
        "router": "newmatch-router-receipt-v1.json",
        "follow": "newmatch-follow-receipt-v1.json",
        "ingest": "newmatch-ingest-receipt-v1.json",
        "cost": "newmatch-cost-receipt-v1.json",
        "handoff": "newmatch-handoff-receipt-v1.json",
        "wire": "newmatch-wire-receipt-v1.json",
        "scale": "newmatch-scale-receipt-v1.json",
    }
    return f"~/.sina/{m.get(goal, 'newmatch-factory-receipt-v1.json')}"


def _blocker(goal: str, seq: int) -> str:
    if seq <= 150:
        return "Graph SSOT missing — router cannot classify without people/situation schema"
    if goal == "router" and seq <= 300:
        return "Situation router blocked — FBE public HTTPS or cloud receipt RED"
    if goal == "follow":
        return "Follow-up loop blocked — founder gate required for T3 or business handoff"
    if goal == "ingest":
        return "Ingest blocked — platform ToS · founder session only"
    if goal == "cost":
        return "Free-tier path not exhausted or cost cap exceeded — loop stops fail-closed"
    return "Mac cannot execute factory body — control panel approve only"


def _marginal_cost(goal: str, seq: int) -> float:
    if goal in ("graph", "ingest", "wire") or seq <= 650:
        return 0.0
    if goal == "cost" and seq <= 720:
        return 0.0
    if goal in ("router", "follow") and seq <= 400:
        return 0.0
    return 0.01


def _row(seq: int, phase_id: str, phase_label: str, goal: str) -> dict:
    pid = f"NM-{seq:03d}"
    title = _title(seq, phase_label, goal)
    mc = _marginal_cost(goal, seq)
    return {
        "id": pid,
        "seq": seq,
        "phase": phase_id,
        "phase_label": phase_label,
        "tier": _tier(seq, goal),
        "title": title,
        "goal_alignment": goal,
        "policy_refs": [
            "data/newmatch-factory-v1.json",
            "data/newmatch-graph-schema-v1.json",
            "data/tool-pick-two-phase-v1.json",
            "data/mcp-stack-free-tier-v1.json",
            "data/phase0-freemium-sandbox-reference-v1.json",
            "data/cloud-factories-online-only-v1.json",
            "data/factory-cost-intelligence-loop-v1.json",
        ],
        "owner_role": "worker" if seq <= 500 else "brain_route_worker",
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "work_template": f"WORK: {pid} — {title[:90]}",
        "acceptance": _acceptance(seq, goal),
        "receipt_path": _receipt(goal, seq),
        "blocker_if_skipped": _blocker(goal, seq),
        "factory_id": "newmatch_router_cloud",
        "status": "planned",
        "cloud_only": True,
        "local_worker_allowed": False,
        "cloud_proof_required": True,
        "disclosure_tier_default": "T4_internal",
        "free_tier_first": True,
        "marginal_cost_usd": mc,
        "cost_tier_max": 1 if mc == 0 else (2 if goal != "cost" else 3),
        "paid_escalation_blocked": mc == 0,
        "mvp_wave": _mvp_wave(seq),
        "priority": _priority(seq, goal),
        "signal_hint": SIGNALS[seq % len(SIGNALS)],
        "route_hint": ROUTES[(seq + len(goal)) % len(ROUTES)],
        "graph_entity": GRAPH_ENTITIES[seq % len(GRAPH_ENTITIES)],
    }


def generate() -> dict:
    plans: list[dict] = []
    for phase_id, phase_label, start, end, goal in PHASES:
        for seq in range(start, end + 1):
            plans.append(_row(seq, phase_id, phase_label, goal))

    titles = [p["title"] for p in plans]
    critical = ["NM-001", "NM-150", "NM-300", "NM-500", "NM-650", "NM-750", "NM-850", "NM-950", "NM-999"]

    return {
        "schema": "newmatch-factory-999-plan-v1",
        "version": "1.2.0",
        "saved_at": _now(),
        "law": "NewMatch v1.2 — free-tier first · situation engine · graph schema · MVP waves · cloud+API",
        "graph_schema": "data/newmatch-graph-schema-v1.json",
        "situation_router_t0": "scripts/newmatch_situation_router_t0_v1.py",
        "free_tier_check": "scripts/newmatch_free_tier_check_v1.py",
        "free_tier_policy": "docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md",
        "phase_0_cost_ceiling_usd": 0,
        "free_plan_count": sum(1 for p in plans if p.get("marginal_cost_usd", 0) == 0),
        "ssot": "data/newmatch-factory-v1.json",
        "generator": "scripts/gen_newmatch_factory_999_plan_v1.py",
        "factory_id": "newmatch_router_cloud",
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_control_panel",
        "plan_count": len(plans),
        "unique_titles": len(set(titles)),
        "tier_counts": {
            t: sum(1 for p in plans if p["tier"] == t) for t in ("P0", "P1", "P2")
        },
        "phase_counts": {p[0]: p[3] - p[2] + 1 for p in PHASES},
        "critical_path": critical,
        "mvp_waves": [{"id": w[0], "start": w[1], "end": w[2]} for w in MVP_WAVES],
        "execution_order_top_40": [f"NM-{i:03d}" for i in range(1, 41)],
        "phases": [
            {"id": pid, "label": lab, "start": s, "end": e, "goal": g}
            for pid, lab, s, e, g in PHASES
        ],
        "plans": plans,
    }


def main() -> int:
    doc = generate()
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(
        f"OK: {OUT.name} plans={doc['plan_count']} unique={doc['unique_titles']} "
        f"P0={doc['tier_counts']['P0']} P1={doc['tier_counts']['P1']} P2={doc['tier_counts']['P2']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
