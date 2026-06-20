#!/usr/bin/env python3
"""Hub payload — STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md for WTM + Council UI."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
DOC = "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md"
SCHEMA = "strategic-synthesis-v1"
TWO_CLOCK_CROSSREF = "archive/attachments/2026-06-14/sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md"
TWO_CLOCK_CANONICAL = "archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_path() -> Path:
    return SOURCE_A / DOC


def _read_doc(*, max_chars: int = 16000) -> str:
    p = _doc_path()
    if not p.is_file():
        return ""
    text = p.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n… [truncated — open full doc in hub]"


def strategic_goals() -> list[dict]:
    gates = _machine_gates()
    dispatch_ready = bool(gates.get("dispatch_ready"))
    gdc_status = "done" if dispatch_ready else "in_progress"
    gdc_blocker = (
        "Orchestra active — founder spine Action to enqueue"
        if dispatch_ready
        else "Founder spine Action — eval proof bridge ready"
    )
    return [
        {
            "id": "goal-ecosystem-proof",
            "title": "Prove packet beats raw LLM on real tasks",
            "track": "ecosystem",
            "priority": "critical",
            "status": "in_progress",
        },
        {
            "id": "goal-commercial-revenue",
            "title": "Shipped products, users, revenue (lane P0)",
            "track": "commercial",
            "priority": "critical",
            "status": "in_progress",
        },
        {
            "id": "goal-governance-moat",
            "title": "Governance + rules-in-charge every session",
            "track": "governance",
            "priority": "high",
            "status": "active",
        },
        {
            "id": "goal-dispatch-closure",
            "title": "Close Plan→Execute→Measure→Learn loop",
            "track": "runtime",
            "priority": "high",
            "status": gdc_status,
            "blocker": gdc_blocker,
        },
    ]


def next_plans() -> list[dict]:
    eval_live = _eval_1b_live_pass()
    gates = _machine_gates()
    return [
        {
            "phase": 0,
            "id": "slice-sustain",
            "title": "Strategic slice sustain + lane attests",
            "status": "in_progress",
            "owner": "maintainer+lanes",
            "gate": "now",
        },
        {
            "phase": 1,
            "id": "eval-1b",
            "title": "Eval-1b behavioral harness",
            "status": "done" if gates["eval_1b_gate_ok"] else "in_progress",
            "owner": "maintainer",
            "gate": "live_pass" if eval_live else "openrouter_credits",
            "roi": "highest",
        },
        {
            "phase": 2,
            "id": "dispatch-policy",
            "title": "Dispatch policy + C7→spine bridge",
            "status": "done" if gates.get("dispatch_ready") else "in_progress",
            "owner": "maintainer",
            "gate": "orchestrator_dispatch_ready",
            "note": (
                "dispatch_ready=true — orchestra active"
                if gates.get("dispatch_ready")
                else f"blocked: {'; '.join((gates.get('dispatch_ready_blockers') or [])[:2]) or 'gates'}"
            ),
        },
        {
            "phase": 3,
            "id": "l8-embeddings",
            "title": "L8 embedding index + hybrid D9",
            "status": "in_progress",
            "owner": "maintainer",
            "gate": "hash_local_scaffold",
        },
        {
            "phase": 4,
            "id": "learning-loop",
            "title": "Learning loop outcomes→ranking",
            "status": "in_progress",
            "owner": "maintainer",
            "gate": "feedback_to_bus",
        },
        {
            "phase": 5,
            "id": "event-bus",
            "title": "Event fabric pub/sub",
            "status": "in_progress",
            "owner": "maintainer",
            "gate": "hub_api",
        },
    ]


def _eval_1b_live_pass() -> bool:
    path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
    if not path.is_file():
        return False
    try:
        import json

        rep = json.loads(path.read_text(encoding="utf-8"))
        return rep.get("mode") == "live" and bool(rep.get("live_ok", rep.get("ok")))
    except (json.JSONDecodeError, OSError):
        return False


def _machine_gates() -> dict:
    """Live dispatch/eval gates — honest SSOT (v1.1 orchestrator_dispatch_ready)."""
    eval_ok = False
    eval_note = "eval_packet missing"
    eval_mode = ""
    dispatch_ready = False
    blockers: list[str] = []
    try:
        import json
        import sys

        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from runtime.dispatch_policy.policy_engine import (
            eval_1b_gate_status,
            orchestrator_dispatch_ready_payload,
        )

        eval_ok, eval_note = eval_1b_gate_status()
        orch = orchestrator_dispatch_ready_payload()
        dispatch_ready = bool(orch.get("dispatch_ready"))
        blockers = list(orch.get("dispatch_ready_blockers") or [])
    except Exception as exc:  # noqa: BLE001
        eval_note = str(exc)
    rep_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
    if rep_path.is_file():
        try:
            import json

            rep = json.loads(rep_path.read_text(encoding="utf-8"))
            eval_mode = str(rep.get("mode") or "")
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "dispatch_ready": dispatch_ready,
        "dispatch_ready_blockers": blockers,
        "eval_1b_gate_ok": eval_ok,
        "eval_1b_note": eval_note,
        "eval_1b_mode": eval_mode or ("live" if eval_ok else "structural"),
    }


def pendings() -> list[dict]:
    eval_live = _eval_1b_live_pass()
    items: list[tuple[str, str, str, str, str]] = [
        ("P0", "Eval-1b sustain — 5+ live tasks + CI", "maintainer", "critical", "done" if eval_live else "open"),
        ("P1", "ENFORCE bypass map LOCKED + hub", "maintainer", "high", "done"),
        ("P2", "L0-full editor telemetry", "maintainer", "medium", "partial"),
        ("P3", "L0/L1 deepen", "maintainer", "high", "open"),
        ("P4", "Dispatch policy + eval gate", "maintainer", "high", "done" if eval_live else "open"),
        ("P5", "graph_executor + spine_bridge", "maintainer", "medium", "done" if eval_live else "open"),
        ("P6", "L8 embeddings hybrid", "maintainer", "medium", "done"),
        ("P7", "L5/L6 semantic history", "maintainer", "low", "done"),
        ("P8", "Learning loop + event bus", "maintainer", "low", "done"),
        ("P9", "Lane Scoreboard + vault attests", "lanes", "high", "done"),
        ("P10", "TrustField outreach / pilot", "trustfield", "critical", "in_progress"),
        ("P11", "Wire RunReceipt / verify:wire", "wire", "high", "done"),
    ]
    return [
        {"id": i, "title": t, "owner": o, "priority": p, "status": st}
        for i, t, o, p, st in items
    ]


def this_week() -> list[dict]:
    return [
        {"who": "founder", "action": "Refresh → Actions: Enqueue eval spine bridge → Track"},
        {"who": "maintainer", "action": "SSOT sync + fleet auto-pass UI; sustain Eval-1b CI on build"},
        {"who": "lanes", "action": "Scoreboard session report + governance-drift essay (auto-green, no manual verify)"},
        {"who": "trustfield", "action": "P10 pilot outreach + vault note"},
        {"who": "wire", "action": "G3 attest on WIRE_LANE_PROGRESS + hub Track close"},
    ]


def two_clock_lesson() -> dict:
    """Commercial lane lesson — CLOCK A (slice) ∥ CLOCK B (lane P0). sa-0524."""
    return {
        "lesson_id": "two-clock-slice-lane-p0",
        "summary": "Two clocks: strategic slice (STRATEGIC-SLICE) ∥ parallel lane P0 revenue",
        "crossref_doc": TWO_CLOCK_CROSSREF,
        "canonical_case_study": TWO_CLOCK_CANONICAL,
        "synthesis_doc": DOC,
        "synthesis_lesson": "§9.4 Two clocks normal (slice ∥ lane P0)",
        "clock_a": {
            "id": "STRATEGIC-SLICE",
            "namespace": "WTM D-phase · spine",
            "hub_headline": True,
            "pass_signal": "eval_1b_gate_ok · dispatch_ready · spine bridge",
        },
        "clock_b": {
            "id": "lane-p0",
            "namespace": "TrustField · Wire · MergePack · FORGE",
            "hub_headline": False,
            "pass_signal": "lane deposit · outreach receipt · vault attest · verify:wire",
        },
    }


def strategic_synthesis_payload() -> dict:
    path = _doc_path()
    body = _read_doc()
    gates = _machine_gates()
    dr = gates.get("dispatch_ready")
    if gates["eval_1b_gate_ok"] and dr:
        one_line = (
            "Eval-1b live pass (eval_1b_gate_ok=true) + dispatch_ready=true — orchestra active (enforce gate); "
            "founder spine Action to enqueue; lane P0 revenue parallel."
        )
    elif gates["eval_1b_gate_ok"]:
        one_line = (
            "Eval-1b live pass (eval_1b_gate_ok=true); dispatch_ready blocked — "
            f"{'; '.join((gates.get('dispatch_ready_blockers') or [])[:2]) or 'check gates'}."
        )
    else:
        one_line = (
            f"Eval-1b {gates['eval_1b_mode']} only (eval_1b_gate_ok=false); "
            "dispatch_ready=false — live eval + enforce required; lane P0 revenue."
        )
    return {
        "ok": path.is_file(),
        "schema": SCHEMA,
        "version": "2.0",
        "doc_path": DOC,
        "doc_abs": str(path),
        "built_at": _now(),
        "machine_gates": gates,
        "one_line": one_line,
        "bottleneck": (
            f"dispatch_ready={dr} · eval_1b_gate_ok={gates['eval_1b_gate_ok']} — "
            + (
                "orchestra active — spine bridge enqueue"
                if dr
                else f"blocked: {'; '.join((gates.get('dispatch_ready_blockers') or [])[:3]) or 'gates'}"
            )
        ),
        "do_now_primary": "STRATEGIC-SLICE",
        "strategic_goals": strategic_goals(),
        "next_plans": next_plans(),
        "pendings": pendings(),
        "this_week": this_week(),
        "lessons": [
            "Architecture without outcome proof = decision support",
            "Governance is ~50% of the product",
            "SSOT > screenshots > chat",
            "Two clocks: slice ∥ lane P0",
            "D16 ≠ loop closure",
        ],
        "two_clock_lesson": two_clock_lesson(),
        "forbidden": [
            "New D-modules from critic paste",
            "L8 as WTM primary",
            "Lane SourceA edits",
            "Fabricate physical G3 for Track slice",
        ],
        "body_markdown": body,
        "body_chars": len(body),
        "related_docs": [
            "COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md",
            "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md",
            "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
            TWO_CLOCK_CROSSREF,
            TWO_CLOCK_CANONICAL,
        ],
    }
