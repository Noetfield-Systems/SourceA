#!/usr/bin/env python3
"""ONE prompt = ONE purpose (HEALTHY_PROMPT_SEQUENCE_LOCKED_v1). SSOT for API + CLI turns."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANDATORY_PATHS = [
    "brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    "brain-os/law/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
    "brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/REGISTRY_DRAIN_PROCESS_LOCKED_v1.md",
]


def _use_slim_prompt(slim: bool | None) -> bool:
    if slim is not None:
        return slim
    if os.environ.get("SINA_INBOX_FULL", "").strip().lower() in ("1", "true", "yes"):
        return False
    env = os.environ.get("SINA_INBOX_SLIM", "").strip().lower()
    if env in ("1", "true", "yes"):
        return True
    if env in ("0", "false", "no"):
        return False
    try:
        from worker_manual_only_v1 import is_manual_only  # noqa: WPS433

        return is_manual_only()
    except Exception:
        return False


def build_turn_prompt_slim(*, item: dict, pos: int, total: int, engine: str = "WORKER") -> str:
    """~12 lines — founder/Worker chat. Laws logged; agent reads paths, not pasted walls."""
    sa_id = item.get("sa_id", "?")
    role = (item.get("queue_role") or "check").lower()
    instr = (item.get("instruction") or item.get("sa_title") or "").strip()
    if len(instr) > 160:
        instr = instr[:157] + "..."
    sa_path = item.get("sa_path") or ""
    task_md = f"brain-os/plan-registry/sourcea-1000/{sa_path}" if sa_path else ""

    role_one = {
        "check": "CHECK — validators + gap report only. No implement.",
        "act": "ACT — minimal diff for this sa only. No closeout.",
        "verify": "VERIFY — validators + receipt + closeout. Then STOP.",
    }.get(role, f"{role.upper()} — one purpose only.")

    lines = [
        f"RUN INBOX · {sa_id} · {role.upper()} · {pos}/{total}",
        "",
        role_one,
        f"Task: {instr}" if instr else f"Task file: {task_md or '(see queue item)'}",
    ]
    if task_md and instr:
        lines.append(f"File: {task_md}")
    lines += [
        "",
        "Stop after this role · WORKER_ROUND_REPORT · broker submit",
        "Disk SSOT: ~/.sina/run-inbox-disk-truth-v1.json",
        f"Skill: @sina-sourcea-worker · engine={engine}",
    ]
    return "\n".join(lines)


def build_turn_prompt(*, item: dict, pos: int, total: int, engine: str, slim: bool | None = None) -> str:
    """One queue slot · one purpose · stop after WORKER_ROUND_REPORT."""
    if _use_slim_prompt(slim):
        return build_turn_prompt_slim(item=item, pos=pos, total=total, engine=engine)

    from agent_turn_context_v1 import build_memory_block, role_law_block  # noqa: WPS433

    sa_id = item.get("sa_id", "?")
    role = (item.get("queue_role") or "check").lower()
    instr = (item.get("instruction") or "").strip()
    verify = (item.get("verify") or "").strip()
    try:
        from worker_verify_normalize_v1 import normalize_worker_verify  # noqa: WPS433

        verify = normalize_worker_verify(verify, role=role)
    except Exception:
        pass
    sa_path = item.get("sa_path") or ""
    title = item.get("title") or item.get("sa_title") or ""
    task_md = f"brain-os/plan-registry/sourcea-1000/{sa_path}" if sa_path else ""

    scout = Path.home() / ".sina" / "sidecar" / "api-scout" / f"{sa_id}-scout.md"
    prep = Path.home() / ".sina" / "sidecar" / "cli-prep" / f"{sa_id}-prep.md"

    laws = "\n".join(f"- {p}" for p in MANDATORY_PATHS)

    disk_truth = ""
    try:
        from run_inbox_disk_truth_v1 import format_truth_block, write_truth  # noqa: WPS433

        write_truth(sync=False)
        disk_truth = format_truth_block()
    except Exception:
        disk_truth = ""

    lines = [
        f"SourceA Worker turn — engine={engine}",
        f"bound: sa_id={sa_id} role={role} pos={pos}/{total}",
        f"title: {title}",
        "",
        "LAW: one prompt = one purpose. No multi-step 0-5 contract. STOP after this role.",
        "LAW: Next steps shows live next-10 mirror — THIS INBOX turn is execution SSOT.",
        "Cursor skill (session): @sina-sourcea-worker · shared: @sina-registry-drain",
        f"Mandatory reads (Read tool if needed, do not paste all):",
        laws,
        "",
        role_law_block(role),
        "",
    ]
    if disk_truth:
        lines += [disk_truth, ""]
    lines += [
        build_memory_block(sa_id=sa_id, role=role, pos=pos, total=total),
        "",
        f"Queue instruction: {instr}",
    ]

    if task_md:
        lines.append(f"Task file: {task_md}")

    if "check" in role:
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "track_validate",
                ROOT / "scripts" / "track_validate_backlog_v1.py",
            )
            tv = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tv)  # type: ignore[union-attr]
            track_block = tv.format_inbox_block(limit=25)
        except Exception:
            track_block = ""
        lines += [
            "",
            "THIS TURN: CHECK ONLY — validators + gap report. Zero implement. Zero closeout.",
            "LAW: run worker_turn_entry_v1.sh first (gate + anti-staleness auto-heal).",
            f"Verify: {verify or 'preflight validators per task .md'}",
        ]
        if track_block:
            lines += ["", track_block]
        if scout.is_file():
            lines.append(f"Optional scout: {scout}")

    elif "act" in role:
        lines += [
            "",
            "PREFLIGHT: Cursor window focused before any paste (cursor_window_preflight_v1.py).",
            "BROKER: after WORKER_ROUND_REPORT → goal1_lane_broker.py worker-submit (machine pickup; not Brain chat).",
            "",
            "THIS TURN: ACT ONLY — minimal diff for bound sa_id. No closeout. No batch.",
            "LAW: run worker_turn_entry_v1.sh first (gate + anti-staleness auto-heal).",
            f"Verify hint: {verify}",
        ]
        if scout.is_file():
            lines.append(f"Read scout first: {scout}")
        if prep.is_file():
            lines.append(f"Read prep plan: {prep}")

    elif "verify" in role:
        lines += [
            "",
            "PREFLIGHT: Cursor window focused before any paste (cursor_window_preflight_v1.py).",
            "BROKER: after WORKER_ROUND_REPORT → goal1_lane_broker.py worker-submit (machine pickup; not Brain chat).",
            "",
            "THIS TURN: VERIFY + CLOSEOUT only — validators + receipt + WORKER_ROUND_REPORT → STOP.",
            "LAW: WORKER_NO_SLOW_VERIFY_SHELL — never full find_critical_bugs (3 min). Safety = hub only.",
            "LAW: WORKER_FAST_ANTI_STALENESS — worker_verify_ultra_v1.sh runs probe + auto-heal first.",
            f"Verify commands: {verify or 'bash worker_verify_ultra_v1.sh + task-specific validator'}",
        ]

    lines += [
        "",
        "Output: end with worker_round_report YAML (status PASS/FAIL/BLOCKED).",
        "next_action: next queue role on same sa, or NONE after verify.",
    ]
    return "\n".join(lines)
