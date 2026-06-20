#!/usr/bin/env python3
"""Order Guardian — task orders registry + smart advisory from live hub state."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / ".sina" / "task-orders"
ORDERS_PATH = ROOT / "orders.jsonl"
SUMMARY_PATH = ROOT / "summary.json"
LAW_PATH = Path(__file__).resolve().parents[1] / "ORDER_GUARDIAN_AGENT_LOCKED_v1.md"
REGISTER_PATH = Path(__file__).resolve().parents[1] / "TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md"

AGENT_ID = "order_guardian"
AGENT_NAME = "Order Guardian"
AGENT_ICON = "🛡"

STATUSES = frozenset(
    {"open", "partial", "needs_activation", "deferred", "lane_shipped", "shipped", "different_goal"}
)
JUDGMENTS = frozenset({"missed", "partial", "different_goal", "needs_activation", "lane_shipped", "shipped"})
PRIORITIES = frozenset({"critical", "high", "normal", "low"})
LANES = frozenset({"hub", "noetfield", "fleet", "ecosystem", "portfolio"})

# status → expected judgment (seed + UI Ship/Defer contract — sa-0798)
STATUS_JUDGMENT_CONTRACT: dict[str, str] = {
    "open": "missed",
    "needs_activation": "needs_activation",
    "partial": "partial",
    "shipped": "shipped",
    "deferred": "different_goal",
    "lane_shipped": "lane_shipped",
    "different_goal": "different_goal",
}

# Pendings ↔ task-order pairs for cross-SSOT drift warn (no auto-sync)
PENDINGS_ORDER_PAIRS: list[tuple[str, str]] = [
    ("P2", "TO-DRIFT"),
    ("P8", "TO-008"),
    ("P9", "TO-009"),
    ("P10", "TO-SKU"),
    ("P11", "TO-WIRE"),
]

SEED_ROWS: list[dict[str, Any]] = [
    {
        "id": "TO-OG-001",
        "title": "Order Guardian — task orders + smart advisor in hub",
        "detail": "Save all orders into important docs + app; advise what to do from current state.",
        "status": "shipped",
        "judgment": "shipped",
        "priority": "critical",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "governance",
        "quick_win": False,
        "strategic": False,
        "register_doc": "TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md",
        "shipped_evidence": "ORDER_GUARDIAN_AGENT_LOCKED_v1.md + task_orders_guardian.py + hub tab",
    },
    {
        "id": "TO-002",
        "title": "D2 Graph Fusion (WTM)",
        "detail": "World Target Model next strategic build after D1 — graph fusion layer.",
        "status": "different_goal",
        "judgment": "different_goal",
        "priority": "high",
        "lane": "hub",
        "thread": "THREAD-SUPERBRAIN",
        "category": "wtm",
        "quick_win": False,
        "strategic": True,
        "defer_reason": "Sprint focused agent hub; activate when SUPERBRAIN thread is P0",
    },
    {
        "id": "TO-003",
        "title": "GPT report-only mode lock (D-GPT-01)",
        "detail": "Lock default paste mode to report-only; EXTERNAL_CRITIC must not auto-apply builds.",
        "status": "open",
        "judgment": "missed",
        "priority": "high",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "policy",
        "quick_win": True,
        "strategic": False,
        "linked_doc": "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
    },
    {
        "id": "TO-004",
        "title": "Supervisor dashboard tab",
        "detail": "Traffic lights, weekly digest, links to scoreboard/vault/essay.",
        "status": "open",
        "judgment": "missed",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "ui",
        "quick_win": False,
        "strategic": False,
    },
    {
        "id": "TO-005",
        "title": "Authority index hub tile",
        "detail": "Optional founder tile → SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md",
        "status": "open",
        "judgment": "missed",
        "priority": "low",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "ui",
        "quick_win": True,
        "strategic": False,
    },
    {
        "id": "TO-007",
        "title": "Trust ledger schema v1",
        "detail": "Formal schema for agent-governance-events.jsonl; Noetfield blueprint optional via UKE.",
        "status": "open",
        "judgment": "missed",
        "priority": "high",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "governance",
        "quick_win": False,
        "strategic": False,
    },
    {
        "id": "TO-010",
        "title": "Lazy-load COMMAND_DATA (~2MB)",
        "detail": "Split hub payload — index.html embeds full command-data.",
        "status": "open",
        "judgment": "missed",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "perf",
        "quick_win": False,
        "strategic": False,
    },
    {
        "id": "TO-011",
        "title": "Import historical rules → founder-directives.jsonl",
        "detail": "Batch ingest legacy founder directives; complements founder-requests registry.",
        "status": "open",
        "judgment": "missed",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "data",
        "quick_win": False,
        "strategic": False,
    },
    {
        "id": "TO-012",
        "title": "Essay auto-nudges in hub",
        "detail": "Surface essay gaps on Today/Council — API exists, nudge UI missing.",
        "status": "open",
        "judgment": "missed",
        "priority": "high",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "fleet",
        "quick_win": True,
        "strategic": False,
    },
    {
        "id": "TO-008",
        "title": "Fleet essays — governance drift (6/8 remaining)",
        "detail": "Subject governance-drift-detection; agents must post via Council essay API.",
        "status": "needs_activation",
        "judgment": "needs_activation",
        "priority": "high",
        "lane": "fleet",
        "thread": "THREAD-MAINTAINER",
        "category": "fleet",
        "quick_win": False,
        "strategic": False,
        "activation_hint": "Open each agent chat → Council essay subject governance-drift-detection",
    },
    {
        "id": "TO-009",
        "title": "Scoreboard fleet reports + ASF verify",
        "detail": "1 report, 0 verified — all 8 agents file session reports; ASF marks verify.",
        "status": "needs_activation",
        "judgment": "needs_activation",
        "priority": "high",
        "lane": "fleet",
        "thread": "THREAD-MAINTAINER",
        "category": "fleet",
        "quick_win": False,
        "strategic": False,
        "activation_hint": "Agent scoreboard tab → each agent submits + ASF verify ✓",
    },
    {
        "id": "TO-DRIFT",
        "title": "Governance drift enterprise runtime (8-layer)",
        "detail": "Hub Phase 1 score 100; full enterprise engine on roadmap.",
        "status": "partial",
        "judgment": "partial",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "governance",
        "quick_win": False,
        "strategic": False,
        "shipped_evidence": "governance_drift_engine.py Phase 1",
    },
    {
        "id": "TO-006",
        "title": "Council Phase 2 formal ballots",
        "detail": "After Phase 1 votes + essay discourse mature.",
        "status": "deferred",
        "judgment": "different_goal",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "governance",
        "defer_reason": "Gate: 8/8 essays + stable Phase 1",
    },
    {
        "id": "TO-ML",
        "title": "ML drift sensors (PSI/KL)",
        "detail": "D5+ roadmap — not Phase 1.",
        "status": "deferred",
        "judgment": "different_goal",
        "priority": "low",
        "lane": "hub",
        "thread": "THREAD-SUPERBRAIN",
        "category": "wtm",
        "defer_reason": "WTM phase gate D5+",
    },
    {
        "id": "TO-SKU",
        "title": "TrustField Governance Drift SKU",
        "detail": "Product Phase 3 after Noetfield proof.",
        "status": "deferred",
        "judgment": "different_goal",
        "priority": "low",
        "lane": "portfolio",
        "thread": "THREAD-TRUSTFIELD",
        "category": "product",
        "defer_reason": "After Noetfield lane proof",
    },
    {
        "id": "NF-DRIFT",
        "title": "Noetfield governance drift blueprints (×4)",
        "detail": "LANE_SHIPPED on Mac ~/Desktop/Noetfield/docs/reference/ — not merged to SourceA.",
        "status": "lane_shipped",
        "judgment": "lane_shipped",
        "priority": "high",
        "lane": "noetfield",
        "thread": "THREAD-NOETFIELD",
        "category": "governance",
        "activation_hint": "Governance Unification Engine → batch intake from Noetfield reference",
    },
    {
        "id": "NF-PRIVATE",
        "title": "Noetfield private annex sync",
        "detail": "ops/private/ may be gitignored; sync from cloud if ahead.",
        "status": "partial",
        "judgment": "partial",
        "priority": "normal",
        "lane": "noetfield",
        "thread": "THREAD-NOETFIELD",
        "category": "sync",
    },
    {
        "id": "NF-PUSH",
        "title": "Noetfield git commit/push",
        "detail": "Portfolio lane needs founder activation in Noetfield chat.",
        "status": "needs_activation",
        "judgment": "needs_activation",
        "priority": "high",
        "lane": "noetfield",
        "thread": "THREAD-NOETFIELD",
        "category": "git",
        "activation_hint": "Say commit in Noetfield local chat",
    },
    {
        "id": "NF-CLOUD",
        "title": "Noetfield cloud agent read order",
        "detail": "[NF-CLOUD-AGENT] entry via git — cloud lane activation.",
        "status": "needs_activation",
        "judgment": "needs_activation",
        "priority": "high",
        "lane": "noetfield",
        "thread": "THREAD-NOETFIELD",
        "category": "cloud",
        "activation_hint": "Open noetfield_cloud agent pack in Agent hub",
    },
    {
        "id": "NF-UKE",
        "title": "Merge Noetfield drift docs into SourceA (UKE)",
        "detail": "2 items rejected at intake — rerun UKE when ready.",
        "status": "open",
        "judgment": "missed",
        "priority": "high",
        "lane": "noetfield",
        "thread": "THREAD-NOETFIELD",
        "category": "governance",
        "activation_hint": "Council Room → Governance Unification → batch from Noetfield",
    },
    {
        "id": "TO-MP",
        "title": "MergePack MP-SHIP (Vercel 401)",
        "detail": "Disable deployment protection or fix auth for live ship.",
        "status": "open",
        "judgment": "missed",
        "priority": "high",
        "lane": "ecosystem",
        "thread": "THREAD-MERGEPACK",
        "category": "ops",
        "activation_hint": "Founder: Vercel project settings → deployment protection",
    },
    {
        "id": "TO-WIRE",
        "title": "Wire G3 Tailscale proof",
        "detail": "Wire lane G3 proof pending founder/repo action.",
        "status": "open",
        "judgment": "missed",
        "priority": "normal",
        "lane": "ecosystem",
        "thread": "THREAD-WIRE",
        "category": "ops",
    },
    {
        "id": "TO-PDB",
        "title": "Personal DB raw ingestion",
        "detail": "Layer A exists; first chat drops → L2 ingestion partial.",
        "status": "partial",
        "judgment": "partial",
        "priority": "normal",
        "lane": "hub",
        "thread": "THREAD-MAINTAINER",
        "category": "data",
    },
    {
        "id": "TO-BOWL",
        "title": "Daily bowl drift item",
        "detail": "False-positive D-REG-1 removed — mergepack/registry aligned; DRIFT.json empty.",
        "status": "shipped",
        "judgment": "shipped",
        "priority": "normal",
        "lane": "ecosystem",
        "thread": "THREAD-MAINTAINER",
        "category": "daily",
        "quick_win": True,
        "strategic": False,
        "shipped_evidence": "build-sina-daily-bowl.py detect_drift fix + drift score 100",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_dir() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)


def _read_rows() -> list[dict[str, Any]]:
    _ensure_dir()
    if not ORDERS_PATH.exists():
        return []
    rows = []
    for line in ORDERS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _write_rows(rows: list[dict[str, Any]]) -> None:
    _ensure_dir()
    ORDERS_PATH.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def seed_if_empty() -> int:
    rows = _read_rows()
    if rows:
        return 0
    now = _now()
    seeded = []
    for r in SEED_ROWS:
        seeded.append({**r, "created_at": now, "updated_at": now, "source": "seed"})
    _write_rows(seeded)
    _write_summary(seeded)
    return len(seeded)


def _write_summary(rows: list[dict[str, Any]]) -> None:
    by_status: dict[str, int] = {}
    by_lane: dict[str, int] = {}
    actionable = 0
    for r in rows:
        st = r.get("status", "open")
        by_status[st] = by_status.get(st, 0) + 1
        ln = r.get("lane", "hub")
        by_lane[ln] = by_lane.get(ln, 0) + 1
        if st in ("open", "partial", "needs_activation"):
            actionable += 1
    SUMMARY_PATH.write_text(
        json.dumps(
            {
                "updated_at": _now(),
                "total": len(rows),
                "actionable_count": actionable,
                "by_status": by_status,
                "by_lane": by_lane,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _priority_weight(p: str) -> int:
    return {"critical": 4, "high": 3, "normal": 2, "low": 1}.get(p, 2)


def _hub_signals(hub: dict[str, Any] | None) -> dict[str, Any]:
    hub = hub or {}
    signals: dict[str, Any] = {
        "ops_blockers": False,
        "essay_gap": 0,
        "essay_total": 8,
        "scoreboard_reports": 0,
        "scoreboard_verified": 0,
        "drift_score": None,
        "p0_active": False,
        "open_commitments": 0,
        "open_founder_requests": 0,
    }
    gd = hub.get("governance_drift") or {}
    if gd.get("aggregate_score") is not None:
        signals["drift_score"] = gd["aggregate_score"]

    essay = hub.get("essay_discourse") or {}
    posted = 0
    topics = essay.get("topics") or []
    if topics:
        active = next((t for t in topics if t.get("active")), topics[0])
        posted = int(active.get("essay_count") or len(active.get("agents") or []))
    else:
        agents = essay.get("agents") or essay.get("by_agent") or []
        if isinstance(agents, list):
            posted = sum(1 for a in agents if (a.get("posted") or a.get("has_essay")))
        elif isinstance(agents, dict):
            posted = sum(1 for v in agents.values() if v)
        elif essay.get("posted_count") is not None:
            posted = int(essay.get("posted_count", 0))
    signals["essay_gap"] = max(0, 8 - posted)

    sb = hub.get("agent_scoreboard") or {}
    signals["scoreboard_reports"] = int(
        sb.get("reported_count") or sb.get("report_count") or sb.get("total_reports") or 0
    )
    signals["scoreboard_verified"] = int(sb.get("verified_count") or 0)

    prog = hub.get("program_progress") or hub.get("state", {}).get("program_progress") or {}
    if prog.get("p0_percent") is not None and float(prog.get("p0_percent", 0)) < 100:
        signals["p0_active"] = True

    commits = hub.get("commitments") or {}
    signals["open_commitments"] = int(commits.get("open_count") or 0)
    fr = hub.get("founder_requests") or {}
    signals["open_founder_requests"] = int(fr.get("open_count") or 0)

    blockers = hub.get("blockers") or hub.get("state", {}).get("blockers") or []
    if blockers:
        signals["ops_blockers"] = True
    ops = hub.get("ops_alerts") or []
    if ops:
        signals["ops_blockers"] = True

    return signals


def compute_advisory(rows: list[dict[str, Any]], hub: dict[str, Any] | None = None) -> dict[str, Any]:
    signals = _hub_signals(hub)
    scored: list[tuple[float, dict[str, Any], str]] = []

    for r in rows:
        st = r.get("status", "open")
        if st in ("shipped", "deferred", "different_goal", "lane_shipped"):
            continue

        score = 0.0
        reasons: list[str] = []

        score += _priority_weight(r.get("priority", "normal")) * 10

        if st == "needs_activation":
            score += 50
            reasons.append("Fleet/founder must act — system already built")
        elif st == "partial":
            score += 35
            reasons.append("Finish what was started")
        elif st == "open":
            score += 25

        if r.get("quick_win"):
            score += 30
            reasons.append("Quick hub win — low build cost")

        oid = r.get("id", "")
        if oid == "TO-008" and signals["essay_gap"] > 0:
            score += 40 + signals["essay_gap"] * 5
            reasons.append(f"Essay gap: {signals['essay_gap']} agents still missing")
        if oid == "TO-009" and signals["scoreboard_verified"] < 8:
            score += 35 + (8 - signals["scoreboard_verified"]) * 4
            reasons.append(f"Scoreboard: {signals['scoreboard_verified']}/8 verified")
        if oid == "TO-012" and signals["essay_gap"] > 0:
            score += 25
            reasons.append("Nudge UI would unblock fleet essays")

        if r.get("strategic") and signals["ops_blockers"]:
            score -= 60
            reasons.append("Defer strategic build — ops blockers active")
        elif r.get("strategic") and signals["essay_gap"] >= 4:
            score -= 30
            reasons.append("Fleet activation queue first")

        if r.get("lane") == "noetfield" and oid == "NF-UKE":
            if signals["drift_score"] and signals["drift_score"] >= 95:
                score += 20
                reasons.append("Drift score high — good time for UKE merge")

        if signals["p0_active"] and r.get("category") == "perf":
            score -= 20
            reasons.append("P0 program active — perf can wait")

        rec = {
            "id": r.get("id"),
            "title": r.get("title"),
            "status": st,
            "lane": r.get("lane"),
            "priority": r.get("priority"),
            "score": round(score, 1),
            "reasons": reasons[:4],
            "activation_hint": r.get("activation_hint"),
            "tab_hint": _tab_hint_for(r),
        }
        scored.append((score, rec, r.get("title", "")))

    scored.sort(key=lambda x: (-x[0], x[2]))
    top = [s[1] for s in scored[:5]]

    state_summary = _state_summary(signals, rows)
    do_now = top[0] if top else None
    brief = _guardian_brief(state_summary, do_now, top)

    return {
        "signals": signals,
        "state_summary": state_summary,
        "do_now": do_now,
        "recommendations": top,
        "brief": brief,
        "computed_at": _now(),
    }


def _tab_hint_for(row: dict[str, Any]) -> str:
    cat = row.get("category", "")
    oid = row.get("id", "")
    if cat == "fleet" or oid in ("TO-008", "TO-009"):
        return "agent-scoreboard"
    if row.get("lane") == "noetfield":
        return "council-room"
    if cat == "daily":
        return "daily"
    if cat == "policy":
        return "rules"
    return "order-guardian"


def _state_summary(signals: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    actionable = sum(1 for r in rows if r.get("status") in ("open", "partial", "needs_activation"))
    parts = [f"{actionable} actionable orders"]
    if signals["essay_gap"]:
        parts.append(f"essays {8 - signals['essay_gap']}/8")
    if signals["scoreboard_verified"] < 8:
        parts.append(f"scoreboard verify {signals['scoreboard_verified']}/8")
    if signals["drift_score"] is not None:
        parts.append(f"drift score {signals['drift_score']}")
    if signals["ops_blockers"]:
        parts.append("ops blockers active")
    return " · ".join(parts)


def _guardian_brief(state_summary: str, do_now: dict[str, Any] | None, top: list[dict]) -> str:
    lines = [f"Order Guardian — {state_summary}."]
    if do_now:
        lines.append(f"Do now: {do_now['title']} ({do_now['id']}).")
        if do_now.get("activation_hint"):
            lines.append(do_now["activation_hint"])
        elif do_now.get("reasons"):
            lines.append(do_now["reasons"][0])
    elif top:
        lines.append("No urgent activation — review open hub builds.")
    else:
        lines.append("All clear — check deferred and strategic queue.")
    return " ".join(lines)


def judgment_contract_mismatches(rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return rows where judgment ≠ STATUS_JUDGMENT_CONTRACT[status]."""
    rows = rows if rows is not None else _read_rows()
    out: list[dict[str, Any]] = []
    for r in rows:
        st = str(r.get("status") or "")
        exp = STATUS_JUDGMENT_CONTRACT.get(st)
        if not exp:
            continue
        jg = str(r.get("judgment") or "")
        if jg != exp:
            out.append(
                {
                    "id": r.get("id"),
                    "status": st,
                    "judgment": jg,
                    "expected": exp,
                }
            )
    return out


def pendings_orders_drift_warnings(
    hub: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Cross-SSOT drift: WTM pendings status vs linked task-order status."""
    from strategic_synthesis_hub import pendings  # noqa: WPS433

    rows = _read_rows()
    by_id = {r.get("id"): r for r in rows}
    signals = _hub_signals(hub)
    warns: list[dict[str, Any]] = []
    pend_by = {p.get("id"): p for p in pendings()}

    for pid, oid in PENDINGS_ORDER_PAIRS:
        p = pend_by.get(pid) or {}
        o = by_id.get(oid) or {}
        if not p or not o:
            continue
        pst = p.get("status")
        ost = o.get("status")
        aligned = True
        if pid == "P2" and pst == "partial" and ost == "partial":
            aligned = True
        elif pst == "done" and ost in ("needs_activation", "open"):
            aligned = False
        elif pst == "in_progress" and ost == "deferred":
            aligned = False
        if not aligned:
            warns.append(
                {
                    "pending_id": pid,
                    "pending_status": pst,
                    "order_id": oid,
                    "order_status": ost,
                    "order_judgment": o.get("judgment"),
                    "reason": "cross_ssot_drift",
                }
            )

    if signals.get("essay_gap") == 0 and signals.get("scoreboard_verified") == 8:
        for oid in ("TO-008", "TO-009"):
            o = by_id.get(oid) or {}
            if o.get("status") == "needs_activation":
                warns.append(
                    {
                        "order_id": oid,
                        "order_status": o.get("status"),
                        "order_judgment": o.get("judgment"),
                        "reason": "fleet_green_order_stale",
                        "signals": {
                            "essay_gap": 0,
                            "scoreboard_verified": signals.get("scoreboard_verified"),
                        },
                    }
                )
    return warns


def orders_payload(hub: dict[str, Any] | None = None) -> dict[str, Any]:
    seed_if_empty()
    rows = _read_rows()
    _write_summary(rows)
    advisory = compute_advisory(rows, hub)
    try:
        from founder_agent_use_guide import reminder_payload  # noqa: WPS433

        aw = reminder_payload(hub)
        if aw.get("wanted_count"):
            advisory["agent_window_reminder"] = aw
            if aw.get("do_now") and not advisory.get("do_now"):
                advisory["do_now"] = {
                    "id": f"AW-{aw['do_now']['id']:03d}",
                    "title": f"Agents Window task {aw['do_now']['id']}: {aw['do_now']['title'][:50]}",
                    "status": "needs_activation",
                    "lane": "cursor",
                    "priority": "high",
                    "score": 90,
                    "reasons": ["Multi-step work — use Cursor Agents Window, not Editor"],
                    "activation_hint": aw["do_now"].get("agent_prompt"),
                    "tab_hint": "agent-window",
                }
    except Exception:
        pass
    by_status: dict[str, list] = {s: [] for s in sorted(STATUSES)}
    for r in rows:
        st = r.get("status", "open")
        if st not in by_status:
            by_status[st] = []
        by_status[st].append(r)

    actionable = [r for r in rows if r.get("status") in ("open", "partial", "needs_activation")]

    return {
        "ok": True,
        "agent": {
            "id": AGENT_ID,
            "name": AGENT_NAME,
            "icon": AGENT_ICON,
            "role": "Task orders registry + smart advisor",
            "law_path": LAW_PATH.name,
            "register_path": REGISTER_PATH.name,
        },
        "actionable_count": len(actionable),
        "open_count": sum(1 for r in rows if r.get("status") == "open"),
        "needs_activation_count": sum(1 for r in rows if r.get("status") == "needs_activation"),
        "partial_count": sum(1 for r in rows if r.get("status") == "partial"),
        "total": len(rows),
        "by_status": {k: v for k, v in by_status.items() if v},
        "orders": rows,
        "advisory": advisory,
        "register_doc": str(REGISTER_PATH.relative_to(LAW_PATH.parent)),
        "updated_at": _now(),
    }


def register_order(body: dict[str, Any]) -> dict[str, Any]:
    title = (body.get("title") or "").strip()
    if not title:
        return {"ok": False, "error": "title required"}
    rows = _read_rows()
    now = _now()
    row = {
        "id": body.get("id") or f"TO-{uuid.uuid4().hex[:8].upper()}",
        "title": title,
        "detail": (body.get("detail") or "").strip(),
        "status": body.get("status") or "open",
        "judgment": body.get("judgment") or "missed",
        "priority": body.get("priority") or "normal",
        "lane": body.get("lane") or "hub",
        "thread": body.get("thread") or "THREAD-MAINTAINER",
        "category": body.get("category") or "general",
        "created_at": now,
        "updated_at": now,
        "source": body.get("source") or "hub",
    }
    if row["status"] not in STATUSES:
        return {"ok": False, "error": f"invalid status: {row['status']}"}
    rows.append(row)
    _write_rows(rows)
    _write_summary(rows)
    return {"ok": True, "order": row}


def update_order(body: dict[str, Any]) -> dict[str, Any]:
    oid = (body.get("id") or "").strip()
    if not oid:
        return {"ok": False, "error": "id required"}
    rows = _read_rows()
    found = False
    for i, r in enumerate(rows):
        if r.get("id") != oid:
            continue
        found = True
        for key in (
            "title",
            "detail",
            "status",
            "judgment",
            "priority",
            "lane",
            "thread",
            "category",
            "defer_reason",
            "activation_hint",
            "shipped_evidence",
            "quick_win",
            "strategic",
        ):
            if key in body and body[key] is not None:
                rows[i][key] = body[key]
        rows[i]["updated_at"] = _now()
        break
    if not found:
        return {"ok": False, "error": f"order not found: {oid}"}
    _write_rows(rows)
    _write_summary(rows)
    return {"ok": True, "order": next(r for r in rows if r.get("id") == oid)}


def handle_action(body: dict[str, Any], hub: dict[str, Any] | None = None) -> dict[str, Any]:
    action = (body.get("action") or "list").strip().lower()
    if action == "list":
        return orders_payload(hub)
    if action == "register":
        result = register_order(body)
        if result.get("ok"):
            result["payload"] = orders_payload(hub)
        return result
    if action == "update":
        result = update_order(body)
        if result.get("ok"):
            result["payload"] = orders_payload(hub)
        return result
    if action == "refresh_advisory":
        seed_if_empty()
        rows = _read_rows()
        return {"ok": True, "advisory": compute_advisory(rows, hub), "actionable_count": len(rows)}
    if action == "seed":
        n = seed_if_empty()
        return {"ok": True, "seeded": n, "payload": orders_payload(hub)}
    return {"ok": False, "error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys

    seed_if_empty()
    payload = orders_payload()
    print(json.dumps({"total": payload["total"], "actionable": payload["actionable_count"], "brief": payload["advisory"]["brief"]}, indent=2))
