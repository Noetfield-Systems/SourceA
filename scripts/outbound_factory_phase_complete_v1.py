#!/usr/bin/env python3
"""Auto smart loop — post outbound-factory completion (108/108).

When outbound upgrade plan is done, loop specialist owns next motion — not founder taps.
Receipt: ~/.sina/outbound-factory-phase-complete-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PLAN = ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
RECEIPT = SINA / "outbound-factory-phase-complete-v1.json"
PHASE = "phase-s6-outbound-factory-upgrade"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def outbound_plan_progress() -> dict:
    plan = _read(PLAN)
    upgrades = plan.get("upgrades") or []
    done = sum(1 for u in upgrades if u.get("status") == "done")
    total = len(upgrades)
    return {
        "done": done,
        "total": total,
        "complete": total > 0 and done >= total,
        "pct": round(100 * done / max(total, 1)),
    }


def mark_outbound_queue_exhausted(*, write: bool = True) -> dict:
    """Write exhausted outbound queue doc — stops stale head / founder deliver prompts."""
    prog = outbound_plan_progress()
    if not prog.get("complete"):
        return {"ok": False, "reason": "outbound_not_complete", "progress": prog}
    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": f"Outbound Factory Upgrade drain — complete ({prog['done']}/{prog['total']})",
        "thread": "OUTBOUND-FACTORY",
        "repo": "sourcea",
        "count": 0,
        "rhythm": "complete — loop specialist owns next phase",
        "law": "outbound_factory_phase_complete_v1 · loop auto smart loop",
        "generated_at": _now(),
        "phase_strict": False,
        "phase_strict_complete": True,
        "queue_exhausted": True,
        "stop_reason": "outbound_factory_complete",
        "pick_floor": None,
        "sa_range": [],
        "upgrade_plan_schema": _read(PLAN).get("schema"),
        "maturity_level": (_read(PLAN).get("maturity") or {}).get("current_level"),
        "active_wave": None,
        "queue": [],
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        QUEUE_HOME.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        repo = ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json"
        if repo.parent.is_dir():
            repo.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        STATE_HOME = SINA / "healthy-queue-state-v1.json"
        STATE_HOME.write_text(
            json.dumps(
                {
                    "next_pos": 1,
                    "queue_exhausted": True,
                    "last_advanced_at": _now(),
                    "last_completed_pos": prog["done"],
                    "reset_by": "outbound_factory_phase_complete_v1",
                    "phase": PHASE,
                    "stop_reason": "outbound_factory_complete",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return {"ok": True, "queue_exhausted": True, "progress": prog}


def enable_loop_auto(*, write: bool = True) -> dict:
    cfg_path = SINA / "loop-specialist-config-v1.json"
    cfg = _read(cfg_path)
    if not cfg:
        cfg = {"schema": "loop-specialist-config-v1"}
    cfg["loop_auto_dispatch_enabled"] = True
    cfg["loop_auto_observe_enabled"] = True
    cfg["loop_auto_mode"] = cfg.get("loop_auto_mode") or "shadow_auto"
    cfg["founder_motion"] = "Hub glance only · Loop specialist auto-tick · no RUN INBOX verb"
    cfg["outbound_complete_at"] = _now()
    if write:
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "loop_auto_dispatch_enabled": True}


def advance_next_phase_queue(*, write: bool = True) -> dict:
    """Try phase-s8 / phase-strict queue — loop owns motion even when idle."""
    sys.path.insert(0, str(SCRIPTS))
    cfg_path = SINA / "phase-strict-drain-v1.json"
    cfg = _read(cfg_path)
    result: dict = {"skipped": True, "reason": "no_phase_strict_config"}
    if cfg_path.is_file() and cfg.get("idle_reason") == "cycle3_h2_complete":
        result = {"ok": True, "advanced": False, "reason": "cycle3_h2_complete", "phase_s8": "done"}
    elif cfg_path.is_file():
        if not cfg.get("enabled") and write:
            cfg["enabled"] = True
            cfg["updated_at"] = _now()
            cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        try:
            from phase_strict_pack_advance_v1 import advance_exhausted_pack  # noqa: WPS433

            adv = advance_exhausted_pack(write=write)
            result = {"advance_pack": adv}
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
        try:
            from build_phase_strict_queue_v1 import build_queue  # noqa: WPS433

            built = build_queue(write=write, run_activate=True)
            result["build_queue"] = built
        except Exception as exc:
            result["build_error"] = str(exc)
    return result


def run_auto_transition(*, write: bool = True, dispatch: bool = False) -> dict:
    """Full auto smart loop handoff after outbound factory drain."""
    prog = outbound_plan_progress()
    if not prog.get("complete"):
        return {"ok": False, "error": "outbound_not_complete", "progress": prog}

    steps = {
        "exhausted_queue": mark_outbound_queue_exhausted(write=write),
        "loop_auto": enable_loop_auto(write=write),
        "next_phase": advance_next_phase_queue(write=write),
    }

    tick: dict = {"skipped": not dispatch}
    if dispatch:
        sys.path.insert(0, str(SCRIPTS))
        from loop_specialist_tick_v1 import run_tick  # noqa: WPS433

        tick = run_tick(write=write, dispatch=True)

    sys.path.insert(0, str(SCRIPTS))
    from execution_path_vocabulary_v1 import execute_line  # noqa: WPS433

    row = {
        "schema": "outbound-factory-phase-complete-v1",
        "ok": True,
        "at": _now(),
        "progress": prog,
        "steps": steps,
        "tick": tick,
        "machine_line": (
            f"smart-loop · outbound {prog['done']}/{prog['total']} complete · "
            f"{execute_line()}"
        ),
        "founder_facing": False,
        "command": "python3 scripts/outbound_factory_phase_complete_v1.py --run --dispatch",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        try:
            from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

            rebuild_factory_now(caller="outbound_factory_phase_complete_v1", force=True)
        except Exception:
            pass
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound factory → auto smart loop handoff")
    ap.add_argument("--run", action="store_true", help="Run full auto transition")
    ap.add_argument("--dispatch", action="store_true", help="Also run loop specialist tick dispatch")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.run:
        row = run_auto_transition(write=True, dispatch=args.dispatch)
    else:
        row = {"ok": True, "progress": outbound_plan_progress(), "receipt": str(RECEIPT)}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("machine_line") or row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
