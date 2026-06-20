#!/usr/bin/env python3
"""Generate numbered Worker paste blocks — ~/.sina queue + registry fill to N."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".sina-loop" / "WORKER-OVERNIGHT-100-PASTE-QUEUE.md"
QUEUE_HOME = Path.home() / ".sina" / "healthy-queue-30-active.json"
STATE = Path.home() / ".sina" / "healthy-queue-state-v1.json"
REGISTRY = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"

MANDATORY = [
    "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    "brain-os/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
    "brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/REGISTRY_DRAIN_PROCESS_LOCKED_v1.md",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _goal_pct() -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/goal-progress-v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return "?/?"
    g = json.loads(proc.stdout).get("goal_1") or {}
    return f"{g.get('done', '?')}/{g.get('total', '?')} ({g.get('pct', '?')}%)"



def _paste_body(*, pos: int, total: int, item: dict, goal_pct: str) -> str:
    role = (item.get("queue_role") or "check").lower()
    sa = item.get("sa_id") or "?"
    path_sa = item.get("sa_path") or f"prompts/.../{sa}.md"
    instr = item.get("instruction") or f"Execute {sa} per .md"
    verify = item.get("verify") or "preflight only — see CHECK/ACT law"
    closeout = item.get("closeout")
    role_up = role.upper()
    close_line = (
        f"FULL closeout {sa} · REGISTRY · PRIORITY · pack · WORKER_ROUND_REPORT → STOP"
        if closeout
        else f"NO closeout this turn ({role} phase) · WORKER_ROUND_REPORT → STOP"
    )
    mandatory_block = "\n".join(f"- {p}" for p in MANDATORY)
    return f"""MANUAL PASTE {pos}/{total} — SourceA Worker — role={role} · sa={sa}

NO AUTORUN. Founder pastes this block into SourceA Worker chat. One paste = one turn. Then STOP.
Brain rail: REGISTRY Goal 1 only — NOT RunReceipt · NOT Prompt feed.

THIS TURN — {role_up} ONLY:
- CHECK: validators + gap report — NO implement, NO closeout.
- ACT: minimal diff for bound sa only — NO closeout.
- VERIFY: run REGISTRY verify + receipt + closeout_sa_task.

MANDATORY READS (Read tool, do not paste all):
{mandatory_block}

Queue {pos}/{total} · role={role} · Goal 1: {goal_pct} · bind {sa}
FORBIDDEN: OpenRouter · live eval · eval_1b_gate_ok true · batch stamp · UNATTENDED BATCH

1. VALIDATE FIRST (executor runs — not founder)
   python3 scripts/cursor_entry_gate.py --role worker
   python3 scripts/cursor_agent_self_audit.py session-start
   bash scripts/validate-execution-spine-v1.sh
   cd scripts && python3 find_critical_bugs.py

2. THIS TURN — {role_up} ONLY
   {instr}
   Path: {path_sa}

3. VERIFY COMMAND
   {verify}

4. CLOSEOUT
   {close_line}

End with WORKER_ROUND_REPORT YAML · STOP · wait for founder to paste next prompt manually.
"""


def _queue_items() -> tuple[list[dict], int]:
    q = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
    items = q.get("queue") or []
    pos = 1
    if STATE.is_file():
        try:
            pos = int(json.loads(STATE.read_text()).get("next_pos") or 1)
        except (json.JSONDecodeError, ValueError, TypeError):
            pos = 1
    return items, max(1, min(pos, len(items) or 1))


def _synth_turn(pl: dict, role: str) -> dict:
    sa = pl.get("id", "sa-????")
    path = pl.get("path") or f"prompts/.../{sa}.md"
    title = pl.get("title") or sa
    reg_verify = pl.get("verify") or "cd scripts && python3 find_critical_bugs.py"
    if role == "check":
        instr = (
            f"CHECK ONLY — read `{path}`. Run session-start + spine + find_critical_bugs. "
            f"Report gaps vs task: {title}. Do NOT implement. Do NOT closeout."
        )
        verify = "preflight only — see CHECK/ACT law"
        closeout = False
    elif role == "act":
        instr = (
            f"ACT ONLY — implement `{sa}` per its .md. Minimal diff. Task: {title}. "
            f"One sa only. Disk validators only — NO OpenRouter, NO live eval."
        )
        verify = "preflight only — see CHECK/ACT law"
        closeout = False
    else:
        instr = (
            f"VERIFY + CLOSEOUT — `{sa}` only. Run: {reg_verify}. "
            f"Write receipts/{sa}-receipt.json · REGISTRY done · PRIORITY row · WORKER_ROUND_REPORT → STOP."
        )
        verify = reg_verify
        closeout = True
    return {
        "queue_role": role,
        "sa_id": sa,
        "sa_path": path,
        "sa_title": title,
        "instruction": instr,
        "verify": verify,
        "closeout": closeout,
    }


def _s6_backlog_fill(*, after_sa: str, need: int) -> list[dict]:
    if not REGISTRY.is_file() or need <= 0:
        return []
    after_n = int(after_sa.split("-")[1]) if after_sa.startswith("sa-") else 0
    plans = json.loads(REGISTRY.read_text()).get("plans") or []
    backlog = sorted(
        [
            p
            for p in plans
            if p.get("status") == "backlog"
            and p.get("phase") == "phase-s6-wtm-pre-llm"
            and int((p.get("id") or "sa-0000").split("-")[1]) > after_n
        ],
        key=lambda p: p.get("id", ""),
    )
    out: list[dict] = []
    for pl in backlog:
        for role in ("check", "act", "verify"):
            out.append(_synth_turn(pl, role))
            if len(out) >= need:
                return out
    return out


def build_pastes(*, count: int = 100) -> list[tuple[int, dict]]:
    items, start_pos = _queue_items()
    total = len(items)
    pastes: list[tuple[int, dict]] = []
    # Forward from current pos through end of pack — never rewind to pos 1
    for p in range(start_pos, total + 1):
        pastes.append((p, items[p - 1]))
        if len(pastes) >= count:
            return pastes[:count]
    last_sa = items[-1]["sa_id"] if items else "sa-0615"
    virtual_pos = total + 1
    for extra in _s6_backlog_fill(after_sa=last_sa, need=count - len(pastes)):
        pastes.append((virtual_pos, extra))
        virtual_pos += 1
        if len(pastes) >= count:
            break
    return pastes[:count]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("-n", "--count", type=int, default=100)
    p.add_argument("-o", "--output", type=Path, default=OUT)
    args = p.parse_args()
    goal_pct = _goal_pct()
    pastes = build_pastes(count=args.count)
    lines = [
        f"# Worker overnight paste queue — {len(pastes)} turns",
        f"",
        f"**Generated:** {_now()}",
        f"**Boss queue:** `~/.sina/healthy-queue-30-active.json`",
        f"**Goal 1:** {goal_pct}",
        f"",
        f"Paste **one block** per Worker turn · end with WORKER_ROUND_REPORT · STOP",
        f"",
        "---",
        f"",
    ]
    for i, (pos, item) in enumerate(pastes, 1):
        total = len(json.loads(QUEUE_HOME.read_text()).get("queue") or [])
        body = _paste_body(pos=pos, total=total or 30, item=item, goal_pct=goal_pct)
        lines.append(f"## PASTE {i:03d} — {item.get('sa_id')} · {item.get('queue_role')}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")
        lines.append("---")
        lines.append("")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(args.output), "count": len(pastes), "goal_pct": goal_pct}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
