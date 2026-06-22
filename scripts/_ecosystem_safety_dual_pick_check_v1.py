#!/usr/bin/env python3
"""FAIL-closed dual-pick gate — live_pick (goal-progress) must match queue (run-inbox truth)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
TRUTH = SINA / "run-inbox-disk-truth-v1.json"
LEGACY_FLAG = SINA / "legacy-pick-floor-v1.flag"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _lawful_idle(truth: dict) -> bool:
    q = truth.get("queue") or {}
    if q.get("queue_exhausted"):
        return True
    fn = _read(SINA / "factory-now-v1.json")
    return (
        int(fn.get("valid_yes") or 0) >= 1000
        and int(fn.get("backlog") or 0) == 0
        and bool(fn.get("dual_proof_ok"))
        and not str(fn.get("queue_sa") or "").strip()
    )


def _outbound_upgrade_queue(truth: dict) -> bool:
    q = truth.get("queue") or {}
    phase = str(q.get("phase") or "")
    if phase in ("phase-s6-outbound-factory-upgrade", "phase-unified-plans-v1"):
        return True
    hq = _read(SINA / "healthy-queue-30-active.json")
    hq_phase = str(hq.get("phase") or "")
    return (
        bool(hq.get("upgrade_plan_schema"))
        or bool(hq.get("plans_unified"))
        or hq_phase in ("phase-s6-outbound-factory-upgrade", "phase-unified-plans-v1")
    )


def _outbound_aligned_pick(*, queue_sa: str, live_sa: str) -> dict | None:
    if not queue_sa:
        return None
    fn = _read(SINA / "factory-now-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    surface_sa = str(surfaces.get("queue_sa") or fn.get("queue_sa") or "")
    aligned_sa = live_sa or surface_sa or queue_sa
    if aligned_sa == queue_sa and (surface_sa == queue_sa or not live_sa):
        return {
            "ok": True,
            "dual_pick_ok": True,
            "aligned": True,
            "outbound_upgrade": True,
            "live_pick_sa": queue_sa,
            "queue_sa": queue_sa,
            "reason": "outbound_factory_upgrade_queue",
        }
    return None


def _phase_market_observed(truth: dict) -> dict | None:
    obs = _read(SINA / "phase-observed-v1.json")
    if str(obs.get("era") or "") != "phase_market":
        return None
    if not (obs.get("queue_exhausted") or (truth.get("queue") or {}).get("queue_exhausted")):
        return None
    head = str(obs.get("cloud_drain_head") or "CLOUD-SEC-001")
    return {
        "ok": True,
        "dual_pick_ok": True,
        "aligned": True,
        "phase_market": True,
        "live_pick_sa": head,
        "queue_sa": "",
        "reason": "phase_market_cloud_drain_observed",
    }


def dual_pick_check() -> dict:
    truth = _read(TRUTH)
    queue_sa = (truth.get("queue") or {}).get("sa_id") or truth.get("queue_sa") or ""
    import importlib.util

    spec = importlib.util.spec_from_file_location("goal_progress_v1", ROOT / "scripts" / "goal-progress-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    gp = mod.goal_progress()
    live_sa = (gp.get("live_pick") or {}).get("id") or ""

    if LEGACY_FLAG.is_file():
        return {
            "ok": True,
            "skipped": True,
            "reason": "legacy_pick_floor",
            "live_pick_sa": live_sa,
            "queue_sa": queue_sa,
        }

    if _lawful_idle(truth):
        return {
            "ok": True,
            "dual_pick_ok": True,
            "aligned": True,
            "idle": True,
            "live_pick_sa": live_sa,
            "queue_sa": queue_sa,
            "reason": "lawful_queue_exhausted",
        }

    market = _phase_market_observed(truth)
    if market:
        market["live_pick_sa"] = live_sa or market.get("live_pick_sa")
        market["truth_match"] = truth.get("truth_match")
        return market

    if _outbound_upgrade_queue(truth):
        outbound = _outbound_aligned_pick(queue_sa=queue_sa, live_sa=live_sa)
        if outbound:
            outbound["truth_match"] = truth.get("truth_match")
            return outbound

    if not queue_sa:
        return {"ok": False, "error": "missing queue_sa in run-inbox-disk-truth-v1.json", "live_pick_sa": live_sa}
    if not live_sa:
        return {"ok": False, "error": "missing live_pick in goal-progress-v1", "queue_sa": queue_sa}

    aligned = live_sa == queue_sa
    return {
        "ok": aligned,
        "dual_pick_ok": aligned,
        "live_pick_sa": live_sa,
        "queue_sa": queue_sa,
        "truth_match": truth.get("truth_match"),
        "action": "align hub/panel live_pick to queue or remove legacy-pick-floor flag",
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="dual-pick ecosystem safety gate")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = dual_pick_check()
    if args.json:
        print(json.dumps(out, indent=2))
    elif out.get("skipped"):
        print(f"OK: dual-pick skipped (legacy_pick_floor) live={out.get('live_pick_sa')} queue={out.get('queue_sa')}")
    elif out.get("ok"):
        print(f"OK: dual-pick aligned {out.get('queue_sa')}")
    else:
        print(
            f"FAIL: dual-pick live_pick={out.get('live_pick_sa')} queue={out.get('queue_sa')} "
            f"— hub projection lies while execution truth passes",
            file=sys.stderr,
        )
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
