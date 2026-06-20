#!/usr/bin/env python3
"""Overnight = ONE paid step (ACT) per sa. CHECK/VERIFY = $0 mechanical skip."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def is_overnight() -> bool:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433

    row = load_active_now()
    if not row.get("ok"):
        return False
    if row.get("stale"):
        return False
    return "absent" in (row.get("founder_mode") or "")


def is_free_slice(role: str) -> bool:
    r = (role or "").lower()
    return "check" in r or "verify" in r


def mechanical_verify_closeout(*, sa_id: str) -> dict:
    """$0 validators only — never mark REGISTRY done overnight (receipt gate)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "find_critical_bugs.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(ROOT),
    )
    return {
        "ok": proc.returncode == 0,
        "sa_id": sa_id,
        "registry_mark": "FORBIDDEN",
        "law": "Overnight VERIFY skip advances queue only — Worker receipt required for done",
        "steps": [{"cmd": "find_critical_bugs.py", "rc": proc.returncode}],
    }


def skip_free_slice(*, sa_id: str, role: str, pos: int) -> dict:
    """Advance queue $0 for CHECK/VERIFY overnight slices."""
    import subprocess as sp

    extra = {}
    if "verify" in (role or "").lower():
        extra["mechanical"] = mechanical_verify_closeout(sa_id=sa_id)

    proc = sp.run(
        [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        adv = json.loads(proc.stdout)
    except json.JSONDecodeError:
        adv = {"raw": proc.stdout, "stderr": proc.stderr}
    return {
        "ok": proc.returncode == 0,
        "skipped": True,
        "reason": "overnight_one_step_free_slice",
        "sa_id": sa_id,
        "role": role,
        "pos": pos,
        "cost_usd": 0,
        "advanced": adv,
        **extra,
    }


def build_slim_act_prompt(item: dict, *, pos: int, total: int) -> str:
    """ACT turn only — no multi-step contract, no inlined task dump."""
    from agent_turn_context_v1 import role_law_block  # noqa: WPS433

    sa_id = item.get("sa_id", "?")
    role = item.get("queue_role", "act")
    instr = item.get("instruction", "")
    verify = item.get("verify", "")
    sa_path = item.get("sa_path", "")
    forbidd = item.get("forbidden", "")
    if isinstance(forbidd, list):
        forbidd = "; ".join(str(x) for x in forbidd[:5])

    task_ref = f"brain-os/plan-registry/sourcea-1000/{sa_path}" if sa_path else "(see queue instruction)"
    scout = Path.home() / ".sina" / "sidecar" / "api-scout" / f"{sa_id}-scout.md"
    prep = Path.home() / ".sina" / "sidecar" / "cli-prep" / f"{sa_id}-prep.md"
    scout_ref = str(scout) if scout.is_file() else "(run Scout first)"
    prep_ref = str(prep) if prep.is_file() else "(run Prep first)"

    return f"""SourceA Worker CLI — ONE turn · ONE role · stop when done.
sa_id={sa_id} role={role} pos={pos}/{total}
Workspace: {ROOT}

{role_law_block(role)}

THIS TURN ONLY (do not run CHECK or VERIFY queue steps — already handled):
{instr}

Verify hint: {verify or "run §Verify from task file"}
Task file (Read if needed): {task_ref}
Scout CHECK (read first): {scout_ref}
CLI prep plan (read first): {prep_ref}

Write receipt: receipts/{sa_id}-receipt.json when DONE.
End with worker_round_report YAML (status PASS/FAIL/BLOCKED).
FORBIDDEN: {forbidd or "scope creep, batch, governance edits"}
"""
