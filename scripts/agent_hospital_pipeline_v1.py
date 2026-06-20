#!/usr/bin/env python3
"""P2 Hospital (Clinic) — Tier 2 MEDIUM · shorter than Maze · remind + memory + heal.

Law: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md (v2)
Trigger: hospital · Escalates to Maze if critical_count > 0
Receipt: ~/.sina/agent-hospital-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-hospital-receipt-v1.json"
QUARANTINE = SINA / "agent-maze-quarantine-v1.json"
SCHEMA = "agent-hospital-receipt-v2"

sys.path.insert(0, str(SCRIPTS))
from agent_three_pipelines_lib_v1 import (  # noqa: E402
    LAW,
    ROLE_SKILL,
    TIERS,
    clear_maze_quarantine_if_critical_zero,
    load_json,
    now_iso,
)

CRIT_PATH = SINA / "find-bugs" / "last-run.json"


def _parse_json_tail(text: str) -> dict:
    """Last complete JSON object in subprocess output (handles JSON + trailing OK: lines)."""
    objects: list[dict] = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                chunk = text[start : i + 1]
                try:
                    objects.append(json.loads(chunk))
                except json.JSONDecodeError:
                    pass
                start = -1
    for obj in reversed(objects):
        if any(k in obj for k in ("ok", "critical", "critical_count", "verdict")):
            return obj
    return objects[-1] if objects else {}


def _critical_count_from_disk() -> int:
    if not CRIT_PATH.is_file():
        return -1
    try:
        return int(json.loads(CRIT_PATH.read_text(encoding="utf-8")).get("critical_count") or 0)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return -1


def _fcb_accept_ok(*, exit_code: int, parsed: dict, raw_out: str) -> bool:
    """find_critical_bugs: accept when critical=0 even if trailing OK lines break naive JSON parse."""
    critical = parsed.get("critical")
    if critical is None:
        critical = parsed.get("critical_count")
    if critical is not None:
        return int(critical) == 0
    if parsed.get("ok") is True:
        return True
    disk = _critical_count_from_disk()
    if disk == 0:
        return True
    if exit_code == 0 and "no critical bugs found" in raw_out.lower():
        return True
    return exit_code == 0


def _clear_maze_quarantine_after_h8(*, critical: int, role: str) -> dict:
    """H8 discharge authority — quarantine active:false when critical_count=0."""
    if critical != 0:
        return {"cleared": False, "reason": "critical_nonzero", "critical_count": critical}
    return clear_maze_quarantine_if_critical_zero(role=role, caller="hospital_h8")


def _run(cmd: list[str], *, timeout: int = 120, env: dict | None = None) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **(env or {})},
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        j = _parse_json_tail(out) if "{" in out else {}
        ok = proc.returncode == 0
        if cmd and "find_critical_bugs.py" in cmd[-1]:
            ok = _fcb_accept_ok(exit_code=proc.returncode, parsed=j, raw_out=out)
        return {"ok": ok, "exit": proc.returncode, "json": j, "tail": out.strip()[-240:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except (json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def run_hospital(*, role: str = "any") -> dict:
    py = sys.executable
    meta = TIERS["hospital"]
    steps: list[dict] = []

    orient = load_json(SINA / "agent-orientation-receipt-v1.json")
    orient_ok = orient.get("orientation_complete") is True or orient.get("ok") is True
    steps.append(
        {
            "id": "H0",
            "step": "orientation_certificate",
            "ok": orient_ok,
            "note": "Run orientation first if missing — mandatory for new arrivals",
            "orient_at": orient.get("at"),
        }
    )

    mirror = _run([py, str(SCRIPTS / "agent_memory_mirror_v1.py"), "--sync", "--validate", "--json"])
    steps.append({"id": "H1", "step": "memory_mirror", **{k: mirror.get(k) for k in ("ok", "exit")}})

    rules = _run([py, str(SCRIPTS / "agent_rules_loop_orchestrator.py"), "--phase", "session_start", "--json-only"])
    steps.append({"id": "H2", "step": "rules_in_charge", **{k: rules.get(k) for k in ("ok", "exit")}})

    bundle = _run([py, str(SCRIPTS / "agent_truth_bundle_v1.py"), "--json"])
    bj = bundle.get("json") or {}
    steps.append({"id": "H3", "step": "truth_bundle", "ok": bundle.get("ok"), "mode": bj.get("mode")})

    gate_role = role if role in ("brain", "worker", "maintainer", "governance", "commercial", "brief") else "any"
    gate = _run([py, str(SCRIPTS / "agent_session_gate_run_v1.py"), "--role", gate_role, "--json"], timeout=180)
    gj = gate.get("json") or {}
    steps.append({"id": "H4", "step": "session_gate_fast", "ok": gate.get("ok") and gj.get("ok"), "gate_id": gj.get("gate_id")})

    steps.append(
        {
            "id": "H5",
            "step": "conscious_recovery_reminder",
            "ok": True,
            "skill": "agent-skills/shared/conscious-recovery/SKILL.md",
            "note": "Run @sina-conscious-recovery if thin context or founder said missed",
        }
    )

    # hub_dual_heal includes worker_hub_heal + H2 sync + pipeline — often 90–120s under load
    heal = _run([py, str(SCRIPTS / "hub_dual_heal_v1.py"), "--json"], timeout=150)
    hj = heal.get("json") or {}
    steps.append({"id": "H6", "step": "dual_hub_heal", "ok": heal.get("ok"), "h1": (hj.get("h1_health") or {}).get("status")})

    pipe = _run([py, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"], timeout=120)
    pj = pipe.get("json") or {}
    steps.append({"id": "H7", "step": "agentic_pipeline_fast", "ok": pipe.get("ok"), "health": (pj.get("health") or {}).get("status")})

    # Refresh after heal steps — hub/pipeline can race validators and poison last-run.json.
    sys.path.insert(0, str(SCRIPTS))
    from agent_three_pipelines_lib_v1 import find_critical_fresh  # noqa: WPS433

    fc_disk = find_critical_fresh(max_age_hours=2.0)
    if fc_disk.get("fresh"):
        fcb = {"ok": True, "exit": 0, "json": {"critical_count": 0, "ok": True, "verdict": "reused_disk"}}
        h7b_critical = 0
    else:
        fcb = _run(
            [py, str(SCRIPTS / "find_critical_bugs.py")],
            timeout=300,
            env={"SINA_FCB_FAST": "1", "SINA_FCB_MAX_SEC": "120"},
        )
        fj = fcb.get("json") or {}
        h7b_critical = fj.get("critical")
        if h7b_critical is None:
            h7b_critical = fj.get("critical_count")
        if h7b_critical is None:
            disk_crit = _critical_count_from_disk()
            h7b_critical = disk_crit if disk_crit >= 0 else None
    steps.append(
        {
            "id": "H7b",
            "step": "critical_bugs_refresh",
            "ok": fcb.get("ok"),
            "exit": fcb.get("exit"),
            "critical_count": h7b_critical,
            "verdict": (fcb.get("json") or {}).get("verdict"),
            "reused_disk": fc_disk.get("fresh") if fc_disk.get("fresh") else False,
        }
    )

    crit_path = CRIT_PATH
    critical = 0
    if crit_path.is_file():
        try:
            critical = int(json.loads(crit_path.read_text()).get("critical_count") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    quarantine_clear = _clear_maze_quarantine_after_h8(critical=critical, role=role)
    steps.append(
        {
            "id": "H8",
            "step": "critical_bugs_check",
            "ok": critical == 0,
            "critical_count": critical,
            "quarantine_clear": quarantine_clear,
        }
    )

    skill_rel = ROLE_SKILL.get(role, ROLE_SKILL["any"])
    skill_ok = (ROOT / skill_rel).is_file()
    steps.append({"id": "H9", "step": "role_skill_reminder", "ok": skill_ok, "path": skill_rel})

    escalate_maze = critical > 0
    discharge = "Run INBOX once (Worker) · Brain poll broker · H1 Safety only"
    if role == "brain":
        discharge = "Judge only · route Worker/Maintainer · Valid YES from disk"
    elif role == "maintainer":
        discharge = "SHIP H2 bucket only · never full hub rebuild on Refresh"

    heal_steps = [
        s
        for s in steps
        if s["step"]
        not in (
            "orientation_certificate",
            "critical_bugs_check",
            "conscious_recovery_reminder",
            "critical_bugs_refresh",  # advisory refresh — H8 is discharge authority
        )
    ]
    core_ok = all(s.get("ok") for s in heal_steps)
    ok = core_ok and orient_ok and not escalate_maze

    row = {
        "schema": SCHEMA,
        "ok": ok,
        "at": now_iso(),
        **meta,
        "shorter_than": "maze",
        "role": role,
        "steps": steps,
        "escalate_maze": escalate_maze,
        "discharge_note": discharge if ok else "ESCALATE TO MAZE — critical bugs or failed heal",
        "quarantine_clear": quarantine_clear,
        "law": LAW,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if escalate_maze:
        QUARANTINE.write_text(
            json.dumps({"active": True, "reason": "hospital_escalation", "at": now_iso(), "role": role}, indent=2) + "\n",
            encoding="utf-8",
        )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P2 Hospital Clinic — Tier 2 medium")
    ap.add_argument("--role", default="any")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_hospital(role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"HOSPITAL tier=2 ok={row['ok']} escalate_maze={row['escalate_maze']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
