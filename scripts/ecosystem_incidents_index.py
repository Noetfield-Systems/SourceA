#!/usr/bin/env python3
"""Unified ecosystem incidents index for Sina Command doc library + Essentials."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
ROOM_ROOT = SINA_HOME / "incident-room"

# Root incident reports indexed under INCIDENT_CORPUS — not separate authority law rows.
LOCKED_ROOT_INCIDENT_REPORTS: tuple[str, ...] = (
    "AGENT_INCIDENTS_REGISTRY_REPORT_LOCKED_v1.md",
    "CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_REPORT_LOCKED_v1.md",
    "INCIDENT_SUBJECT_INDEX_REPORT_LOCKED_v1.md",
    "SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_REPORT_LOCKED_v1.md",
    "SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_REPORT_LOCKED_v1.md",
    "SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_REPORT_LOCKED_v1.md",
    "SINA_AGENT_INCIDENT_WRONG_FOLDER_FILING_INCIDENT_021_REPORT_LOCKED_v1.md",
    "SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_REPORT_LOCKED_v1.md",
    "SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_AGENT_TOPIC_CONFLATION_INCIDENT_020_REPORT_LOCKED_v1.md",
    "SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_REPORT_LOCKED_v1.md",
    "SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_REPORT_LOCKED_v1.md",
    "SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md",
    "SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_REPORT_LOCKED_v1.md",
    "SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_REPORT_LOCKED_v1.md",
    "SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_REPORT_LOCKED_v1.md",
    "SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_REPORT_LOCKED_v1.md",
    "SINA_MONITOR_FOUNDER_SCROLL_RESPECT_INCIDENT_018_REPORT_LOCKED_v1.md",
    "SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_S10_WRONG_BASH_CWD_INCIDENT_019_REPORT_LOCKED_v1.md",
    "SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_REPORT_LOCKED_v1.md",
    "SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_WORKER_INCIDENT_028_REPEAT_REPORT_LOCKED_v1.md",
    "SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_REPORT_LOCKED_v1.md",
    "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md",
    "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_REPORT_LOCKED_v1.md",
    "SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_REPORT_LOCKED_v1.md",
    "SINA_BRAIN_STALE_COMMAND_DATA_GOVERNANCE_FAILURE_INCIDENT_033_REPORT_LOCKED_v1.md",
    "SINA_PROHIBITION_INSTEAD_OF_DISK_WIRE_INCIDENT_034_REPORT_LOCKED_v1.md",
    "SINA_AGENT_PIPELINE_MAZE_SPEED_TRAP_INCIDENT_035_REPORT_LOCKED_v1.md",
    "SINA_VOYAGE_P05_FAKE_GREEN_STALE_LABELS_INCIDENT_036_REPORT_LOCKED_v1.md",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _room_posts() -> list[dict]:
    rows: list[dict] = []
    if not ROOM_ROOT.is_dir():
        return rows
    for week_dir in sorted(ROOM_ROOT.glob("weeks/*"), reverse=True):
        posts_file = week_dir / "posts.jsonl"
        if not posts_file.is_file():
            continue
        for line in posts_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(
                {
                    "kind": "incident_room_post",
                    "week": week_dir.name,
                    "title": row.get("title", "Weekly post"),
                    "agent_id": row.get("agent_id", ""),
                    "at": row.get("at", ""),
                    "path": str(posts_file),
                }
            )
    return rows[:30]


def _incident_entry(path: str, title: str = "", why: str = "") -> dict:
    base = Path(path).name
    return {
        "path": path,
        "title": title or base.replace("_LOCKED_v1.md", "").replace("_", " "),
        "why": why or "Indexed under INCIDENT_CORPUS — see ECOSYSTEM_INCIDENTS_INDEX.",
        "tab": "doc-library",
    }


def ecosystem_incidents_payload() -> dict:
    locked_docs = [
        {
            "path": "WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "WTM UI content-loss incident (2026-06-05)",
            "why": "Never strip founder WTM tab on UI upgrade; no agent reads in hub UI.",
            "tab": "system-roadmap",
        },
        {
            "path": "WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "WTM phase naming incident (2026-06-05)",
            "why": "Founder phases A→B→C→D only; step IDs (B4, A1.1) stay stable.",
            "tab": "system-roadmap",
        },
        {
            "path": "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Auto-paste incident (2026-06-04)",
            "why": "Never re-enable Cursor inject without ASF.",
            "tab": "doc-library",
        },
        {
            "path": "CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md",
            "title": "Context / memory / closeout incident (2026-06-06)",
            "why": "Chat is not SSOT — session-start + session-close every turn.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md",
            "title": "Maintainer repeat-mistake / Mac lag incident (2026-05-27)",
            "why": "Run maintainer_self_audit_loop.py — no hub ship without postflight.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md",
            "title": "Goal 1 loop unvalidated proof (2026-06-07)",
            "why": "Never claim RUNNING without AGENT DONE + broker + orchestrator + hub health.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Goal hierarchy enforcement failure (2026-06-08)",
            "why": "INCIDENT-004 — Brain + Claude Pro must read GOAL_HIERARCHY first; never ask founder to pick main vs commercial; CLI queue SSOT is ~/.sina eval-dispatch.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Goal 1 auto-run broker STALE receipts (2026-06-09)",
            "why": "INCIDENT-007 — recipe·validation·evidence·built audit; 67 STALE broker; receipt_on_disk ban; no autorun until broker PASS.",
            "tab": "doc-library",
        },
        {
            "path": "WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md",
            "title": "Worker full-round evidence enforcement (2026-06-09)",
            "why": "Factory gate law — RECIPE·VALIDATION·EVIDENCE·BUILT; worker_factory_evidence_gate_v1.py wired on every Worker entry.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Worker auto-run stall & timing (2026-06-09)",
            "why": "INCIDENT-008 — 180s poll ban; timing estimates; CLOSEOUT_TEMPLATE; stale agent log; §7 worker playbook.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Worker session mistakes & closeout (2026-06-09)",
            "why": "INCIDENT-009 — session digest: false broker_ok, STALE 67, tips, sa-0001..0010 audit, open gaps.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_REPORT_LOCKED_v1.md",
            "title": "Ecosystem incidents master index + session insights (2026-06-09)",
            "why": "Chronological table 001–009 · arc · essentials · mistakes · better moves · tips · never-again card.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_REPORT_LOCKED_v1.md",
            "title": "Worker stale goal_progress chat report (2026-06-10)",
            "why": "INCIDENT-010 — never parrot INBOX goal_progress; run goal-progress-v1.py; honest +1 per VERIFY only.",
            "tab": "doc-library",
        },
        {
            "path": "brain-os/law/enforcement/GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md",
            "title": "Goal 1 execution solution — PEV / headless (2026-06-07)",
            "why": "Batch log = truth; AUTO-RUN 10; Worker chat = optional visible lane.",
            "tab": "doc-library",
        },
        {
            "path": "brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md",
            "title": "Goal 1 activation chain — inject · validate · activate",
            "why": "Deliver ≠ running; WORKER_ROUND_REPORT + agent -p -f mandatory.",
            "tab": "doc-library",
        },
        {
            "path": "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
            "title": "Incident Room law",
            "why": "Weekly share + certify.",
            "tab": "incident-room",
        },
        {
            "path": "SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md",
            "title": "Conflict Room law",
            "why": "ACE triage — report and continue.",
            "tab": "conflict-room",
        },
        {
            "path": "AUTO_CONFLICT_ENGINE_V3_LOCKED.md",
            "title": "ACE v3",
            "why": "DESIGN / EXECUTION / DELIVERY planes.",
            "tab": "conflict-room",
        },
    ]
    seen_paths = {d["path"] for d in locked_docs}
    for report in LOCKED_ROOT_INCIDENT_REPORTS:
        if report not in seen_paths:
            locked_docs.append(_incident_entry(report))
            seen_paths.add(report)
    sections = [
        {
            "id": "locked_reports",
            "title": "Locked incident reports",
            "items": locked_docs,
        },
        {
            "id": "weekly_room",
            "title": "Incident Room — weekly posts",
            "items": _room_posts() or [
                {
                    "kind": "hint",
                    "title": "No weekly posts yet",
                    "why": "Open Incident Room tab — each agent posts once per ISO week.",
                    "tab": "incident-room",
                }
            ],
        },
        {
            "id": "storage",
            "title": "On-disk storage",
            "items": [
                {"path": str(ROOM_ROOT), "title": "Incident Room data", "why": "~/.sina/incident-room/", "tab": "incident-room"},
                {"path": str(SINA_HOME / "agent-workspaces"), "title": "Per-agent incident reports", "why": "INCIDENT_REPORT_ALWAYS.md per workspace", "tab": "agents"},
            ],
        },
    ]
    total = sum(len(s["items"]) for s in sections)
    return {
        "ok": True,
        "built_at": _now(),
        "tagline": "All incident surfaces — locked docs, weekly room, agent storage.",
        "sections": sections,
        "total_count": total,
        "law_path": "ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md",
    }
