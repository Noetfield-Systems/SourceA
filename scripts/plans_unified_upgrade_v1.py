#!/usr/bin/env python3
"""Unified plan upgrade — sync all 100-step plans to disk truth.

Plans: outbound-factory-100 · full-stack-100-fix · brain-cloud-reasoning-1000
Receipt: ~/.sina/plans-unified-upgrade-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUTBOUND = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
FULL_STACK = ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"
BRAIN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
ECOSYSTEM_111 = ROOT / "data" / "ecosystem-mac-health-111-upgrade-plan-v1.json"
RECEIPT = SINA / "plans-unified-upgrade-receipt-v1.json"

UNIFIED_CROSS_REF = {
    "ecosystem_mac_health_111": "data/ecosystem-mac-health-111-upgrade-plan-v1.json",
    "outbound_factory_100": "data/outbound-factory-100-upgrade-plan-v1.json",
    "full_stack_100_fix": "data/sourcea-full-stack-100-fix-plan-v1.json",
    "brain_cloud_1000": "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
    "mcp_stack": "data/mcp-stack-free-tier-v1.json",
    "tool_pick_two_phase": "data/tool-pick-two-phase-v1.json",
    "trust_center": "data/trust-center-v1.json",
    "disclosure_ladder": "data/disclosure-ladder-v1.json",
    "tier_policy": "docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md",
    "platform_neutral_world_model": "data/platform-neutral-world-model-v1.json",
    "phase0_freemium_sandbox": "data/phase0-freemium-sandbox-reference-v1.json",
    "anti_theater_loop": "data/anti-theater-validator-loop-v1.json",
    "orchestrator": "scripts/plans_unified_upgrade_v1.py",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _wave_status(wave: dict, items: list[dict], id_key: str = "id") -> str:
    ids = set(wave.get("upgrade_ids") or wave.get("plan_ids") or [])
    if not ids:
        return str(wave.get("status") or "pending")
    rows = [x for x in items if x.get(id_key) in ids]
    if not rows:
        return str(wave.get("status") or "pending")
    done = sum(1 for x in rows if x.get("status") == "done")
    pending = sum(1 for x in rows if x.get("status") not in ("done",))
    if pending == 0:
        return "complete"
    if done > 0:
        return "active"
    return "pending"


def upgrade_outbound_plan(plan: dict) -> dict:
    upgrades = plan.get("upgrades") or []
    done = sum(1 for u in upgrades if u.get("status") == "done")
    p0_done = sum(1 for u in upgrades if u.get("status") == "done" and u.get("tier") == "P0")
    p1_done = sum(1 for u in upgrades if u.get("status") == "done" and u.get("tier") == "P1")
    for w in plan.get("waves") or []:
        w["status"] = _wave_status(w, upgrades, "id")
    active = "W1"
    for w in plan.get("waves") or []:
        if w.get("status") == "active":
            active = str(w.get("id"))
            break
    plan["active_wave"] = active
    plan["next_wave"] = active
    plan["progress"] = {
        "done_total": done,
        "planned_total": sum(1 for u in upgrades if u.get("status") != "done"),
        "p0_done": p0_done,
        "p1_done": p1_done,
        "pct": round(100 * done / len(upgrades)) if upgrades else 0,
    }
    plan["cross_ref"] = {**(plan.get("cross_ref") or {}), **UNIFIED_CROSS_REF}
    plan["saved_at"] = _now()
    plan["upgrade_policy"] = {
        "phase_1": "exhaust free-tier tools first",
        "phase_2": "affordable AI tools — founder approval before wire",
        "ssot": "data/tool-pick-two-phase-v1.json",
    }
    return {"done": done, "total": len(upgrades), "active_wave": active}


def upgrade_full_stack_plan(plan: dict) -> dict:
    fixes = plan.get("fixes") or []
    for w in plan.get("waves") or []:
        w["status"] = _wave_status(w, fixes, "id")
    done = sum(1 for f in fixes if f.get("status") == "done")
    plan["progress"] = {
        "total": len(fixes),
        "done": done,
        "in_progress": sum(1 for f in fixes if f.get("status") == "in_progress"),
        "planned": sum(1 for f in fixes if f.get("status") == "planned"),
        "blocked": sum(1 for f in fixes if f.get("status") == "blocked"),
        "pct": round(100 * done / len(fixes)) if fixes else 0,
    }
    plan["cross_ref"] = {**(plan.get("cross_ref") or {}), **UNIFIED_CROSS_REF}
    plan["saved_at"] = _now()
    active = next((w["id"] for w in (plan.get("waves") or []) if w.get("status") == "active"), "W1")
    plan["active_wave"] = active
    return {"done": done, "total": len(fixes), "active_wave": active}


def upgrade_brain_plan(plan: dict) -> dict:
    upgrades = plan.get("upgrades") or []
    tp = _read(SINA / "tool-pick-two-phase-receipt-v1.json")
    mcp = _read(SINA / "mcp-stack-free-tier-receipt-v1.json")

    mac_proof_rules: dict[str, bool] = {
        "B0702": bool(tp.get("wired")),
        "B0706": bool(mcp.get("wired")),
    }
    newly_marked: set[str] = set()
    reset_ids: set[str] = set()

    for u in upgrades:
        uid = str(u.get("id") or "")
        if u.get("status") == "done" and u.get("mac_proof") and not u.get("brain_proof"):
            if uid not in mac_proof_rules or not mac_proof_rules[uid]:
                u["status"] = "planned"
                u.pop("mac_proof", None)
                reset_ids.add(uid)
        if uid in mac_proof_rules and mac_proof_rules[uid]:
            if u.get("status") != "done":
                newly_marked.add(uid)
            u["status"] = "done"
            u["mac_proof"] = True

    for w in plan.get("waves") or []:
        w["status"] = _wave_status(w, upgrades, "id")

    done = sum(1 for u in upgrades if u.get("status") == "done")
    plan["progress"] = {
        "total": len(upgrades),
        "done": done,
        "planned": sum(1 for u in upgrades if u.get("status") != "done"),
        "pct": round(100 * done / len(upgrades), 2) if upgrades else 0,
        "mac_proven": sum(1 for u in upgrades if u.get("status") == "done" and u.get("mac_proof")),
    }
    plan["tool_pick_ssot"] = "data/tool-pick-two-phase-v1.json"
    plan["cross_ref"] = {**(plan.get("cross_ref") or {}), **UNIFIED_CROSS_REF}
    plan["saved_at"] = _now()
    active = next((w["id"] for w in (plan.get("waves") or []) if w.get("status") == "active"), "E01")
    plan["active_epic"] = active
    return {
        "done": done,
        "total": len(upgrades),
        "active_epic": active,
        "newly_marked": sorted(newly_marked),
        "reset_ids": sorted(reset_ids),
    }


def _sync_phase0_on_plans(ob: dict, fs: dict, br: dict) -> None:
    ssot = "data/phase0-freemium-sandbox-reference-v1.json"
    pulse = "scripts/phase0_freemium_sandbox_pulse_v1.py"
    block = {
        "ssot": ssot,
        "pulse": pulse,
        "validator": "scripts/validate-phase0-freemium-sandbox-v1.sh",
        "one_law": "Phase 0 = $0 reference surfaces that attract users before paid conversion",
    }
    for plan in (ob, fs, br):
        plan["cross_ref"] = {**(plan.get("cross_ref") or {}), **UNIFIED_CROSS_REF, "phase0_freemium_sandbox": ssot}
        plan["phase0_reference"] = block
        up = plan.get("upgrade_policy") or {}
        up["phase_0"] = "improve sandboxes · trials · freemium to reference + attract"
        plan["upgrade_policy"] = up


def run_upgrade(*, write: bool = True) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from full_stack_fix_plan_pulse_v1 import run_pulse as full_stack_pulse  # noqa: WPS433
    from outbound_factory_upgrade_pulse_v1 import run_pulse as outbound_pulse  # noqa: WPS433
    from brain_cloud_reasoning_plan_pulse_v1 import run_pulse as brain_pulse  # noqa: WPS433
    from phase0_freemium_sandbox_pulse_v1 import run_pulse as phase0_pulse  # noqa: WPS433
    from ecosystem_mac_health_111_plan_pulse_v1 import pulse as ecosystem_111_pulse  # noqa: WPS433

    full_stack_pulse(write=write, sync_plan=write)
    outbound_pulse(write=write)
    brain_pulse(write=write)
    phase0_row = phase0_pulse(write=write)
    eco111_row = ecosystem_111_pulse(sync_plan=write)

    ob = _read(OUTBOUND)
    fs = _read(FULL_STACK)
    br = _read(BRAIN)
    ob_sum = upgrade_outbound_plan(ob)
    fs_sum = upgrade_full_stack_plan(fs)
    br_sum = upgrade_brain_plan(br)
    _sync_phase0_on_plans(ob, fs, br)

    if write:
        _write(OUTBOUND, ob)
        _write(FULL_STACK, fs)
        _write(BRAIN, br)

    wtm_check: dict = {}
    try:
        from world_model_plan_check_v1 import run_check as wtm_run  # noqa: WPS433

        wtm_check = wtm_run(write=True)
    except Exception as exc:
        wtm_check = {"ok": False, "error": str(exc)}

    validators: list[tuple[str, list[str]]] = [
        ("outbound_proof", ["python3", "scripts/validate_outbound_plan_execution_proof_v1.py"]),
        ("full_stack_plan", ["bash", "scripts/validate-full-stack-100-fix-plan-v1.sh"]),
        ("brain_cloud_plan", ["bash", "scripts/validate-brain-cloud-reasoning-1000-plan-v1.sh"]),
        ("mcp_stack", ["bash", "scripts/validate-mcp-stack-free-tier-v1.sh"]),
        ("tool_pick", ["bash", "scripts/validate-tool-pick-two-phase-v1.sh"]),
        ("platform_neutral", ["bash", "scripts/validate-platform-neutral-world-model-v1.sh"]),
        ("phase0_reference", ["bash", "scripts/validate-phase0-freemium-sandbox-v1.sh"]),
        ("outbound_forbidden", ["bash", "scripts/validate-outbound-forbidden-sources-v1.sh"]),
    ]
    val_results: dict[str, bool] = {}
    for name, cmd in validators:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        val_results[name] = r.returncode == 0

    anti_theater_row: dict = {}
    try:
        from anti_theater_validator_loop_v1 import run_loop as anti_theater_run  # noqa: WPS433

        anti_theater_row = anti_theater_run(write=True)
    except Exception as exc:
        anti_theater_row = {"ok": False, "error": str(exc)}

    task_priority_row: dict = {}
    try:
        from task_plan_priority_v1 import refresh as task_priority_refresh  # noqa: WPS433

        task_priority_row = task_priority_refresh(write=True)
    except Exception as exc:
        task_priority_row = {"ok": False, "error": str(exc)}

    sync_ok = True
    row = {
        "schema": "plans-unified-upgrade-receipt-v1",
        "saved_at": _now(),
        "ok": (
            sync_ok
            and val_results.get("full_stack_plan", False)
            and val_results.get("brain_cloud_plan", False)
            and val_results.get("platform_neutral", False)
            and val_results.get("outbound_proof", False)
            and val_results.get("outbound_forbidden", False)
            and bool(anti_theater_row.get("ok"))
        ),
        "sync_ok": sync_ok,
        "world_model_check": {
            "ok": bool(wtm_check.get("ok")),
            "line": wtm_check.get("world_model_line"),
            "advisory_count": wtm_check.get("advisory_count"),
        },
        "plans_unified_line": (
            f"Plans · outbound {ob_sum['done']}/{ob_sum['total']} {ob_sum['active_wave']} · "
            f"full-stack {fs_sum['done']}/{fs_sum['total']} {fs_sum['active_wave']} · "
            f"brain {br_sum['done']}/{br_sum['total']} {br_sum['active_epic']} · "
            f"M111 {eco111_row.get('progress', {}).get('done', '?')}/{eco111_row.get('progress', {}).get('total', 111)}"
        ),
        "task_plan_priority": {
            "ok": bool(task_priority_row.get("ok")),
            "line": task_priority_row.get("task_plan_priority_line"),
            "smart_pick": task_priority_row.get("smart_pick"),
            "top_ranked": (task_priority_row.get("ranked") or [])[:5],
            "ssot": "data/sourcea-task-plan-priority-v1.json",
        },
        "one_law": "Phase 0 reference + attract · Phase 1 free-tier exhaust · Phase 2 founder approval",
        "phase0_check": {
            "ok": bool(phase0_row.get("ok")),
            "line": phase0_row.get("phase0_line"),
            "progress": phase0_row.get("progress"),
        },
        "outbound": ob_sum,
        "full_stack": fs_sum,
        "brain_cloud": br_sum,
        "ecosystem_mac_health_111": eco111_row.get("progress") or {},
        "ecosystem_mac_health_111_line": eco111_row.get("line"),
        "validators": val_results,
        "anti_theater_check": {
            "ok": bool(anti_theater_row.get("ok")),
            "line": anti_theater_row.get("anti_theater_line"),
            "passed": anti_theater_row.get("passed"),
            "total": anti_theater_row.get("total"),
            "sina_pending": anti_theater_row.get("sina_pending"),
        },
        "advisory_validators": {
            "note": "outbound_proof and outbound_forbidden now gate plans_unified ok",
        },
        "cross_ref": UNIFIED_CROSS_REF,
        "hub_api": "POST /api/plans-unified/tick/v1",
        "task_plan_priority_line": task_priority_row.get("task_plan_priority_line"),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def handle_hub_post(_body: dict | None = None) -> dict:
    row = run_upgrade(write=True)
    return {**row, "ok": bool(row.get("ok"))}


def hub_slice() -> dict:
    row = _read(RECEIPT)
    if not row:
        row = run_upgrade(write=True)
    return {
        "schema": "worker-hub-plans-unified-v1",
        "ok": bool(row.get("ok")),
        "plans_unified_line": row.get("plans_unified_line"),
        "outbound": row.get("outbound"),
        "full_stack": row.get("full_stack"),
        "brain_cloud": row.get("brain_cloud"),
        "phase0_reference": row.get("phase0_check"),
        "anti_theater": row.get("anti_theater_check"),
        "task_plan_priority": row.get("task_plan_priority"),
        "task_plan_priority_line": row.get("task_plan_priority_line"),
        "hub_api": row.get("hub_api"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified plan upgrade")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_upgrade(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("plans_unified_line") or "—")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
