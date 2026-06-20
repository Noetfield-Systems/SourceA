#!/usr/bin/env python3
"""G1.2 — single JSON truth bundle from ~/.sina + goal-progress (not stale command-data alone)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_agent_truth_bundle() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_control_v1 import load_factory_now  # noqa: WPS433

    import importlib.util

    spec = importlib.util.spec_from_file_location("goal_progress_v1", SCRIPTS / "goal-progress-v1.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    gp = mod.goal_progress()

    fn = load_factory_now()
    truth = _read(SINA / "run-inbox-disk-truth-v1.json")
    if isinstance(truth, dict) and truth.get("prompt_feed_lane"):
        truth = dict(truth)
        truth["next_steps_lane"] = truth.get("next_steps_lane") or truth.pop("prompt_feed_lane")
    stop = _read(SINA / "founder-stop-receipt-v1.json")
    resume = _read(SINA / "founder-resume-drain-v1.json")

    live_sa = (gp.get("live_pick") or {}).get("id") or ""
    queue_sa = (truth.get("queue") or {}).get("sa_id") or truth.get("queue_sa") or fn.get("queue_sa") or ""

    try:
        from agentic_pipeline_lib_v1 import dual_pick_check  # noqa: WPS433

        dual = dual_pick_check()
    except Exception:
        dual = {
            "live_pick_sa": live_sa,
            "queue_sa": queue_sa,
            "aligned": bool(live_sa and queue_sa and live_sa == queue_sa),
        }

    from execution_path_vocabulary_v1 import (  # noqa: WPS433
        factory_motion_line,
        founder_daily_ops_line,
        inject_execution_path,
    )

    factory_motion = factory_motion_line()
    daily_positive = [
        founder_daily_ops_line(),
        "Worker Hub Form official · H2 machines optional",
        "Quote factory_now_line from truth bundle",
    ]

    out = {
        "schema": "agent-truth-bundle-v1",
        "at": datetime.now(timezone.utc).isoformat(),
        "factory_now": fn,
        "factory_now_line": fn.get("line") or "",
        "run_inbox_truth": truth,
        "goal_progress": gp,
        "kill_flag": bool(fn.get("kill_flag")),
        "mode": fn.get("mode") or "FREEZE",
        "stop_receipt": stop,
        "resume_token": resume if resume else None,
        "dual_pick": dual,
        "law": {
            "cursor_autorun": "does_not_exist",
            "factory_motion": factory_motion,
        },
    }

    mirror_path = SINA / "agent-memory-mirror-v1.json"
    try:
        from agent_memory_mirror_v1 import INJECT_LAW, MANDATORY_INCIDENTS  # noqa: WPS433

        out["inject"] = INJECT_LAW
        out["mandatory_incidents"] = list(MANDATORY_INCIDENTS)
        out["inject"]["zone_spine_law"] = "SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md"
        out["inject"]["zone_a_only"] = True
        out["inject"]["forbidden_paths"] = [
            "agent-control-panel/command-data.json",
            "agent-control-panel/command-data-shell.json",
            "agent-control-panel/command-data-canonical.json",
        ]
        out["inject"]["daily_positive"] = daily_positive
        out["inject"]["daily_hub_url"] = "http://127.0.0.1:13020/"
        out["inject"]["execution_path"] = inject_execution_path()
    except Exception:
        out["inject"] = {}
    if mirror_path.is_file():
        try:
            mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
            out["memory_mirror"] = {
                "mirror_hash8": mirror.get("mirror_hash8"),
                "validation_ok": (mirror.get("validation") or {}).get("ok"),
                "synced_at": mirror.get("synced_at"),
            }
            mirror_inject = mirror.get("inject") or {}
            if mirror_inject.get("live_surfaces"):
                out["inject"]["live_surfaces"] = mirror_inject["live_surfaces"]
            if mirror_inject.get("daily_duty_card_detail"):
                out["inject"]["daily_duty_card_detail"] = mirror_inject["daily_duty_card_detail"]
            if mirror_inject.get("thread_room_detail"):
                out["inject"]["thread_room_detail"] = mirror_inject["thread_room_detail"]
        except (OSError, json.JSONDecodeError):
            pass

    try:
        from agent_daily_duty_card_v1 import inject_slice  # noqa: WPS433

        duty = inject_slice()
        if duty and isinstance(out.get("inject"), dict):
            out["inject"]["daily_duty_card_detail"] = duty
    except Exception:
        pass

    brain_wire_path = SINA / "governance-brain-wire-v1.json"
    if not brain_wire_path.is_file():
        brain_wire_path = SINA / "brain-wire-v1.json"
    brain_wire = _read(brain_wire_path)
    if brain_wire:
        out["brain_wire"] = {
            "path": str(brain_wire_path),
            "at": brain_wire.get("at"),
            "ok": brain_wire.get("ok"),
            "queue_head": brain_wire.get("queue_head") or {},
            "active_decisions": brain_wire.get("active_decisions") or [],
            "l2_wired": brain_wire.get("l2_wired") or {},
            "reconciled_stale": (brain_wire.get("reconciled_decision") or {}).get("stale"),
            "rule": "L2 agents MUST obey active_decisions[] — ignore stale reconciled_decision",
        }
    else:
        out["brain_wire"] = {"ok": False, "error": "missing governance-brain-wire-v1.json — run brain_governance_wire_v1.py"}

    l1_path = SINA / "l1-agent-pipeline-wire-v1.json"
    l1_pipe = _read(l1_path)
    if l1_pipe:
        wired = l1_pipe.get("l1_wired") or {}
        out["l1_pipeline"] = {
            "path": str(l1_path),
            "at": l1_pipe.get("at"),
            "ok": l1_pipe.get("ok"),
            "brain_hub": l1_pipe.get("brain_hub") or {},
            "l1_to_brain": l1_pipe.get("l1_to_brain") or {},
            "agents": [a.get("role") for a in (wired.get("agents") or [])],
            "shared": wired.get("shared") or {},
            "specialist_precedence": (wired.get("shared") or {}).get("specialist_precedence"),
            "rule": "ALL L1 wired TO Brain via Python pipeline — chat is input only",
        }
    else:
        out["l1_pipeline"] = {"ok": False, "error": "missing l1-agent-pipeline-wire-v1.json — run agentic_layer_pipeline_v2.py"}

    v2_path = SINA / "agentic-layer-pipeline-v2.json"
    v2 = _read(v2_path)
    if v2:
        out["agentic_pipeline_v2"] = {
            "path": str(v2_path),
            "at": v2.get("at"),
            "ok": v2.get("ok"),
            "version": v2.get("version"),
            "health_status": (v2.get("health") or {}).get("status"),
            "queue_head": (v2.get("brain_summary") or {}).get("queue_head"),
            "issues": v2.get("issues") or [],
            "factory_mode": v2.get("factory_mode"),
            "rule": "Upgraded pipeline v2 — L0–L3 stack · health · cross-ref",
        }
    else:
        out["agentic_pipeline_v2"] = {"ok": False, "error": "missing agentic-layer-pipeline-v2.json — run agentic_layer_pipeline_v2.py"}

    surfaces_path = SINA / "agent-live-surfaces-v1.json"
    if surfaces_path.is_file():
        surf = _read(surfaces_path)
        out["live_surfaces"] = surf
        if surf and isinstance(out.get("inject"), dict):
            ls = out["inject"].setdefault("live_surfaces", {})
            for key in (
                "synced_at",
                "zero_drift_line",
                "better_loop_line",
                "best_loop_oqg_line",
                "sascip_safety_line",
                "nerve_system_line",
            ):
                if surf.get(key):
                    ls[key] = surf.get(key)
            if surf.get("factory_now_line") and not out.get("factory_now_line"):
                ls["factory_now_line"] = surf.get("factory_now_line")
            if surf.get("queue_sa") is not None and not (out.get("factory_now") or {}).get("queue_sa"):
                ls["queue_sa"] = surf.get("queue_sa")

    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Agent truth bundle SSOT")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write-cache", action="store_true", help="Write ~/.sina/last-truth-bundle-v1.json")
    args = p.parse_args()
    out = build_agent_truth_bundle()
    if args.write_cache:
        cache = SINA / "last-truth-bundle-v1.json"
        cache.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
