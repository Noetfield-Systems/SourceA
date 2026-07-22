#!/usr/bin/env python3
"""Founder / advisor discussion track — pinned PENDING table + live factory/S10 strip."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
ATTACH = SOURCE_A / "archive/attachments/2026-06-10"
STATE_PATH = Path.home() / ".sina/founder-advisor-discussion-v1.json"
DOC_PATH = ATTACH / "SOURCEA_FOUNDER_ADVISOR_DISCUSSION_TRACK_LOCKED_v1.md"
S10_RECEIPT = Path.home() / ".sina/s10-eternal-receipt-v1.json"
SCHEMA = "founder-advisor-discussion-v1"

_SUBJECTS: list[dict] = [
    {"n": 1, "topic": "Map of everything", "insight": "One index for this crisis", "action": "Start here", "file": "SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md", "send_advisor": False},
    {"n": 2, "topic": "Why stuck", "insight": "Two OS fight: factory law vs Cursor “finish todos”", "action": "No new architecture — 4 invariants only", "file": "SOURCEA_ROOT_CAUSE_FACTORY_CONTROL_PLANE_ESSAY_LOCKED_v1.md", "send_advisor": True},
    {"n": 3, "topic": "Machine fix spec", "insight": "Chat STOP failed; need spawn gate + factory-now", "action": "P0 shipped as factory_control_v1.py", "file": "SOURCEA_PERMANENT_CONDUCT_POISON_MACHINE_ENFORCEMENT_ESSAY_LOCKED_v1.md", "send_advisor": True},
    {"n": 4, "topic": "Advisor pack", "insight": "External = critic only — no batch drain / no new D-modules", "action": "Send with §0 intake from this file", "file": "SOURCEA_EXTERNAL_ADVISOR_BRIEF_AND_CHECKLISTS_LOCKED_v1.md", "send_advisor": True},
    {"n": 5, "topic": "Audit playbook", "insight": "CONDUCT ≠ POISON — separate diseases", "action": "Paste BLOCK A/C for audits; audit before heal", "file": "SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md", "send_advisor": True},
    {"n": 6, "topic": "Audit v1", "insight": "Superseded", "action": "Use #5 only", "file": "SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v1.md", "send_advisor": False, "superseded": True},
    {"n": 7, "topic": "015-CONDUCT → 023", "insight": "Worker ran drain after STOP; +69 while you thought frozen", "action": "Disposition packs 41–45: accept / sample / rollback", "file": "archive/superseded/incidents/INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md", "send_advisor": True, "repo_root": True},
    {"n": 8, "topic": "Who bypasses what", "insight": "Cursor Shell bypasses spawn like old ENFORCE", "action": "Treat shell as outside airlock until gated", "file": "SOURCEA_MACHINE_ENFORCEMENT_REGISTRY_AND_AGENT_MAP_LOCKED_v1.md", "send_advisor": True},
    {"n": 9, "topic": "Smooth vs now", "insight": "Jun 9 slow = trust; Jun 10 batch = speed, broken trust", "action": "Keep ~596 if accepted; replay one sa rhythm", "file": "SOURCEA_SMOOTH_PROGRESS_HISTORY_VS_NOW_LOCKED_v1.md", "send_advisor": True},
    {"n": 10, "topic": "014 brain display", "insight": "Stale brain file — display lag, not redo all work", "action": "Hub refresh; cite factory-now", "file": "SOURCEA_BRAIN_REPAIR_AUDIT_AND_INCIDENT_014_COMPLETION_LOCKED_v1.md", "send_advisor": False},
    {"n": 11, "topic": "Brain overclaim", "insight": "“Healed / fewer red moments” without proof", "action": "Brain quotes factory-now line only", "file": "SOURCEA_BRAIN_IGNORANCE_AND_ONE_LINER_ANALYSIS_LOCKED_v1.md", "send_advisor": False},
    {"n": 12, "topic": "What to do now", "insight": "Gates OK; trust still hurt; 015 open", "action": "Stay FREEZE → disposition → bounded resume", "file": "SOURCEA_WORKER_CONDUCT_AUDIT_DISPOSITION_GUIDE_LOCKED_v1.md", "send_advisor": False},
    {"n": 13, "topic": "51 Cursor Review", "insight": "Pending edits queue — not git", "action": "Keep All if you want those fixes", "file": "SOURCEA_CURSOR_REVIEW_KEEP_ALL_GUIDE_LOCKED_v1.md", "send_advisor": False},
    {"n": 14, "topic": "Full synthesis + E2E", "insight": "Hub lags disk (dual pick, START under FREEZE)", "action": "Panel lane fixes visibility", "file": "SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md", "send_advisor": True},
    {"n": 15, "topic": "S10 eternal law", "insight": "100 prompts audit factory forever — not run inbox", "action": "Read daily receipt on disk", "file": "SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md", "send_advisor": False, "repo_root": True},
    {"n": 16, "topic": "Conduct plane (live)", "insight": "One module: mode · stop · spawn · factory-now", "action": "Resume: factory_control_v1.py resume --max-turns 1", "file": "scripts/factory_control_v1.py", "send_advisor": False, "script": True},
    {"n": 17, "topic": "S10 machine", "insight": "10 prompts/day · disk receipts", "action": "python3 scripts/s10_eternal_audit_loop_v1.py --daily --json", "file": "scripts/s10_eternal_audit_loop_v1.py", "send_advisor": False, "script": True},
    {"n": 18, "topic": "S10 skill + schedule", "insight": "launchd 06:00 · skill for agents", "action": "Maintainer wires Hub Track when ready", "file": "agent-skills/shared/s10-eternal-self-heal/SKILL.md", "send_advisor": False},
]

_DECISIONS_DEFAULT: list[dict] = [
    {"id": "D1", "title": "Stay frozen?", "options": ["Yes (default)", "Resume now"], "blocks": "Any batch drain", "status": "pending", "choice": ""},
    {"id": "D2", "title": "Packs 41–45 (+69)", "options": ["Accept", "Spot-check", "Rollback"], "blocks": "Closing 015-CONDUCT", "status": "pending", "choice": ""},
    {"id": "D3", "title": "Resume how?", "options": ["ASF: Cloud Forge Run — max 1 — receipt required"], "blocks": "Trust recovery", "status": "pending", "choice": ""},
    {"id": "D4", "title": "Hub UX", "options": ["Hide START under FREEZE", "Fix dual pick", "Both"], "blocks": "“Feels stuck” while gates green", "status": "pending", "choice": ""},
]

_INCIDENT_LAYERS: list[dict] = [
    {"layer": 1, "name": "Master", "file": "brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md", "use": "All IDs 001–021 + paths"},
    {"layer": 2, "name": "Subject", "file": "brain-os/incidents/INCIDENT_SUBJECT_INDEX_LOCKED_v1.md", "use": "Group by monitor / factory / agent / governance"},
    {"layer": 3, "name": "History", "file": "brain-os/incidents/SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_LOCKED_v1.md", "use": "Lessons 001–010"},
]

_ADVISOR_SEND: dict = {
    "attach_nums": [2, 3, 4, 5, 8, 9, 14, 7],
    "say": "EXTERNAL_CRITIC only · FREEZE · find_critical_bugs critical 0 · D1–D4 decided",
    "forbid": ["Batch autodrain", "972 chase", "new D-modules", "complete all todos"],
}

_VERDICT = (
    "Steady state: FREEZE default (D1) · packs 41–45 accepted (D2) · Hub UX shipped (D4) · "
    "dual-pick aligned to queue_sa · find_critical_bugs critical 0. Bounded resume only on ASF token (D3)."
)

_SUPPRESSED_DOCS: list[dict] = [
    {"id": "SUP-A", "tier": "A", "title": "012 stale goal_progress duplicate", "status": "archived", "path": "archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md", "use_instead": "INCIDENT-013"},
    {"id": "SUP-B", "tier": "A", "title": "Wrong REPORT id (010 reuse)", "status": "archived", "path": "archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md", "use_instead": "INCIDENT-013"},
    {"id": "SUP-C", "tier": "A", "title": "S10/bash topic tombstone at root", "status": "pointer", "path": "SINA_S10_WRONG_BASH_CWD_INCIDENT_019_REPORT_LOCKED_v1.md", "use_instead": "INCIDENT-019 + 020"},
    {"id": "SUP-D", "tier": "A", "title": "015-CONDUCT draft (pre-023)", "status": "archived", "path": "archive/superseded/incidents/INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md", "use_instead": "INCIDENT-023"},
    {"id": "SUP-E", "tier": "B", "title": "Goal1 loop proof root duplicate", "status": "archived", "path": "archive/superseded/incidents/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md", "use_instead": "brain-os/incidents/…003"},
    {"id": "SUP-F", "tier": "C", "title": "19 root MOVED stubs", "status": "archived", "path": "archive/superseded/pointers/", "use_instead": "brain-os/ canonical paths"},
    {"id": "SUP-G", "tier": "D", "title": "AUTO-RUN converge program", "status": "archived", "path": "archive/superseded/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md", "use_instead": "FOUNDER_AGENTIC no-AUTO-RUN law"},
    {"id": "SUP-H", "tier": "D", "title": "TODAY_AUTORUN_50 plan", "status": "archived", "path": "archive/superseded/contract/TODAY_AUTORUN_50_PLAN_LOCKED_v1.md", "use_instead": "same"},
    {"id": "SUP-I", "tier": "D", "title": "AUTO_RUN_FULLY_AUTOMATIC law", "status": "archived", "path": "archive/superseded/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md", "use_instead": "same"},
    {"id": "SUP-J", "tier": "E", "title": "20 attachment essays (2026-06-10)", "status": "archive_only", "path": "archive/attachments/2026-06-10/", "use_instead": "authority index + advisor subjects"},
]

_PENDING_SUBJECT_NUMS: set[int] = set()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _doc_path(row: dict) -> str:
    if row.get("script") or row.get("file", "").startswith("agent-skills/"):
        return row["file"]
    if row.get("repo_root"):
        return row["file"]
    return f"archive/attachments/2026-06-10/{row['file']}"


def _live_factory() -> dict:
    try:
        import sys

        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
        return {
            "line": fn.get("line") or "",
            "mode": fn.get("mode") or "FREEZE",
            "kill_flag": bool(fn.get("kill_flag")),
            "queue_sa": fn.get("queue_sa") or "",
            "valid_yes": fn.get("valid_yes"),
            "dual_proof_ok": fn.get("dual_proof_ok"),
        }
    except Exception as exc:
        return {"line": f"factory-now unavailable: {exc}", "mode": "?", "kill_flag": None}


def _live_s10() -> dict:
    row = _read_json(S10_RECEIPT)
    if not row:
        return {"ok": False, "summary": "No S10 receipt yet — run s10_eternal_audit_loop_v1.py --daily"}
    counts = row.get("counts") or {}
    pack = row.get("pack")
    return {
        "ok": bool(row.get("ok")),
        "at": row.get("at"),
        "day": row.get("day"),
        "pack": pack,
        "pass": counts.get("PASS", 0),
        "warn": counts.get("WARN", 0),
        "fail": counts.get("FAIL", 0),
        "summary": f"pack {pack} · {counts.get('PASS', 0)} PASS / {counts.get('WARN', 0)} WARN / {counts.get('FAIL', 0)} FAIL",
    }


def _load_state() -> dict:
    row = _read_json(STATE_PATH)
    if row.get("schema") != SCHEMA:
        row = {
            "schema": SCHEMA,
            "track_status": "pending",
            "pinned": True,
            "decisions": [dict(d) for d in _DECISIONS_DEFAULT],
            "notes": "",
            "created_at": _now(),
            "updated_at": _now(),
        }
        _save_state(row)
        return row
    decisions = row.get("decisions") or []
    by_id = {d.get("id"): d for d in decisions if d.get("id")}
    merged = []
    for default in _DECISIONS_DEFAULT:
        did = default["id"]
        merged.append({**default, **(by_id.get(did) or {})})
    row["decisions"] = merged
    return row


def _save_state(row: dict) -> None:
    row["updated_at"] = _now()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def _subjects_payload() -> list[dict]:
    out = []
    for row in _SUBJECTS:
        out.append({**row, "path": _doc_path(row)})
    return out


def _suppressed_docs_payload() -> list[dict]:
    out = []
    for row in _SUPPRESSED_DOCS:
        rel = row["path"]
        full = SOURCE_A / rel if not rel.endswith("/") else None
        exists = full.is_file() if full else (SOURCE_A / rel).is_dir()
        out.append({**row, "on_disk": exists})
    return out


def _pending_board(decisions: list[dict], subjects: list[dict]) -> list[dict]:
    board: list[dict] = []
    for d in decisions:
        if d.get("status") != "pending":
            continue
        board.append(
            {
                "kind": "decision",
                "id": d.get("id"),
                "title": d.get("title"),
                "detail": d.get("blocks") or "",
                "priority": "P0",
                "options": d.get("options") or [],
                "path": "",
            }
        )
    for s in subjects:
        if s.get("superseded") or s.get("n") not in _PENDING_SUBJECT_NUMS:
            continue
        board.append(
            {
                "kind": "subject",
                "id": f"S{s.get('n')}",
                "title": s.get("topic"),
                "detail": s.get("action") or s.get("insight") or "",
                "priority": "P1" if s.get("n") == 7 else "P2",
                "options": [],
                "path": s.get("path") or "",
            }
        )
    board.append(
        {
            "kind": "archive",
            "id": "PHASE-PACK",
            "title": "Phase pack reorg draft (s2–s9)",
            "detail": "ASF approve before PHASE_STRICT resume",
            "priority": "P1",
            "options": ["Approve draft", "Edit draft", "Defer"],
            "path": "archive/attachments/2026-06-10/PHASE_PACK_REORG_DRAFT_s2-s9_ACHIEVABLE_v1.md",
        }
    )
    board.append(
        {
            "kind": "archive",
            "id": "10-PHASE",
            "title": "10-phase 100-step fix plan",
            "detail": "Machine enforcement rollout — founder disposition on open todos",
            "priority": "P2",
            "options": [],
            "path": "archive/attachments/2026-06-10/SOURCEA_10_PHASE_100_STEP_FIX_PLAN_LOCKED_v1.md",
        }
    )
    for row in _suppressed_docs_payload():
        if row.get("status") == "archived":
            board.append(
                {
                    "kind": "suppressed",
                    "id": row.get("id"),
                    "title": row.get("title"),
                    "detail": f"Use: {row.get('use_instead')}",
                    "priority": "P3",
                    "options": [],
                    "path": row.get("path") or "",
                }
            )
    return board


def founder_advisor_discussion_payload() -> dict:
    state = _load_state()
    factory = _live_factory()
    s10 = _live_s10()
    decisions = state.get("decisions") or _DECISIONS_DEFAULT
    subjects = _subjects_payload()
    pending = sum(1 for d in decisions if d.get("status") == "pending")
    track_status = state.get("track_status") or "pending"
    if track_status == "decided" and pending == 0:
        board = []
        pending_total = 0
    else:
        board = _pending_board(decisions, subjects)
        pending_total = len(board)
    return {
        "ok": True,
        "schema": SCHEMA,
        "pinned": bool(state.get("pinned", True)),
        "track_status": track_status,
        "tagline": "Advisor track — PINNED crisis table · D1–D4 · subjects A–E · live factory/S10",
        "live_poll_ms": 5000,
        "pending_total": pending_total,
        "pending_board": board,
        "suppressed_docs": _suppressed_docs_payload(),
        "law": str(DOC_PATH.relative_to(SOURCE_A)),
        "doc_path": str(DOC_PATH.relative_to(SOURCE_A)),
        "folder": "archive/attachments/2026-06-10/",
        "live_now": {
            "factory": factory,
            "s10": s10,
            "headline": factory.get("line") or "factory-now unavailable",
            "s10_line": s10.get("summary") or "S10 receipt missing",
        },
        "subjects": subjects,
        "advisor_send_nums": [2, 3, 4, 5, 7, 8, 9, 14],
        "advisor_send": _ADVISOR_SEND,
        "decisions": decisions,
        "pending_decisions": pending,
        "incident_layers": _INCIDENT_LAYERS,
        "incident_note": "Registry 015 = ID filing mistake · 015-CONDUCT = STOP ignored (subject #7 only)",
        "verdict": _VERDICT,
        "notes": state.get("notes") or "",
        "updated_at": state.get("updated_at") or _now(),
        "hub_tab": "advisor-discussion",
    }


def handle_action(body: dict) -> dict:
    action = (body.get("action") or "").strip().lower()
    state = _load_state()

    if action in ("list", "refresh", ""):
        return {"ok": True, **founder_advisor_discussion_payload()}

    if action == "update_decision":
        did = body.get("id") or body.get("decision_id")
        choice = (body.get("choice") or "").strip()
        status = (body.get("status") or "decided").strip()
        if not did:
            return {"ok": False, "error": "missing decision id"}
        found = False
        for d in state.get("decisions") or []:
            if d.get("id") == did:
                if choice:
                    d["choice"] = choice
                d["status"] = status
                d["decided_at"] = _now()
                found = True
                break
        if not found:
            return {"ok": False, "error": f"unknown decision {did}"}
        pending = sum(1 for x in state["decisions"] if x.get("status") == "pending")
        if pending == 0:
            state["track_status"] = "decided"
        _save_state(state)
        return {"ok": True, **founder_advisor_discussion_payload()}

    if action == "set_notes":
        state["notes"] = (body.get("notes") or "").strip()
        _save_state(state)
        return {"ok": True, **founder_advisor_discussion_payload()}

    if action == "reopen":
        state["track_status"] = "pending"
        state["pinned"] = True
        for d in state.get("decisions") or []:
            d["status"] = "pending"
            d["choice"] = ""
            d.pop("decided_at", None)
        _save_state(state)
        return {"ok": True, **founder_advisor_discussion_payload()}

    return {"ok": False, "error": f"unknown action: {action}"}


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Founder advisor discussion track")
    p.add_argument("--json", action="store_true")
    p.add_argument("--action", default="refresh")
    p.add_argument("--id", default="")
    p.add_argument("--choice", default="")
    args = p.parse_args()
    out = handle_action({"action": args.action, "id": args.id, "choice": args.choice})
    print(json.dumps(out, indent=2))
