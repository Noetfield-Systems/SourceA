#!/usr/bin/env python3
"""Goal 1 progress — REGISTRY drain aligned to GOAL_HIERARCHY (machine truth for Brain/Worker)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"

PHASE_ORDER = (
    "phase-s0-ssot-alignment",
    "phase-s1-eval-dispatch",
    "phase-s2-hub-build-ci",
    "phase-s3-scoreboard-fleet",
    "phase-s4-spine-loop",
    "phase-s6-wtm-pre-llm",
    "phase-s5-commercial-lanes",
    "phase-s7-council-governance",
    "phase-s8-hub-ui-ux",
    "phase-s9-research-models",
)


def _load_registry() -> list[dict]:
    data = json.loads(REG.read_text(encoding="utf-8"))
    return data.get("plans") or []


def goal_progress(*, pick_script: bool = True) -> dict:
    import subprocess
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_pick_lib import pick_backlog_plans  # noqa: WPS433

    from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

    plans = _load_registry()
    audit = audit_registry_done()
    honest_ids = set(audit["honest_done_ids"])
    raw_done = audit["raw_done"]
    done = audit["honest_done"]
    backlog = sum(1 for p in plans if p.get("status") == "backlog")
    total = len(plans) or 1000
    pct = round(100.0 * done / total, 1)

    phases = []
    for ph in PHASE_ORDER:
        rows = [p for p in plans if p.get("phase") == ph]
        if not rows:
            continue
        d = sum(1 for p in rows if p.get("id") in honest_ids)
        b = sum(1 for p in rows if p.get("status") == "backlog")
        phases.append({"phase": ph, "done": d, "backlog": b, "total": len(rows), "pct": round(100 * d / len(rows), 1)})

    picked = pick_backlog_plans(plans, tiers=["T0", "T1", "T2", "T3"], limit=1, order="phase-first")
    fallback = picked[0] if picked else None
    from queue_sa_pick_lib_v1 import live_pick_aligned  # noqa: WPS433

    live = live_pick_aligned(plans, fallback_pick=fallback)
    if backlog == 0:
        sina = Path.home() / ".sina"
        fn_path = sina / "factory-now-v1.json"
        if fn_path.is_file():
            try:
                fn = json.loads(fn_path.read_text(encoding="utf-8"))
                queue_sa = str(fn.get("queue_sa") or "").strip()
                if queue_sa:
                    hq_path = sina / "healthy-queue-30-active.json"
                    hq = json.loads(hq_path.read_text(encoding="utf-8")) if hq_path.is_file() else {}
                    outbound = bool(hq.get("upgrade_plan_schema")) or str(hq.get("phase") or "") == (
                        "phase-s6-outbound-factory-upgrade"
                    )
                    if outbound:
                        head = (hq.get("queue") or [{}])[0] if hq.get("queue") else {}
                        live = {
                            "id": queue_sa,
                            "phase": str(head.get("phase") or hq.get("phase") or "phase-s6-outbound-factory-upgrade"),
                            "tier": str(head.get("sa_tier") or "P1"),
                            "status": "assigned",
                            "title": str(head.get("title") or head.get("sa_title") or "outbound factory upgrade"),
                            "path": str(head.get("sa_path") or "data/outbound-factory-100-upgrade-plan-v1.json"),
                        }
            except (OSError, json.JSONDecodeError, IndexError):
                pass

    return {
        "schema": "goal-progress-v1",
        "goal_1": {
            "name": "Controlled automation factory — sourcea-1000 REGISTRY",
            "done": done,
            "honest_done": done,
            "raw_done": raw_done,
            "unproven_done": audit["unproven_done"],
            "drift": audit["drift"],
            "backlog": backlog,
            "total": total,
            "pct": pct,
            "north_star": "GOAL_HIERARCHY_LOCKED_v1.md Goal 1",
            "law": "honest_done = receipt logged only — YAML restore illegal",
        },
        "live_pick": {
            "id": live.get("id") if live else None,
            "phase": live.get("phase") if live else None,
            "tier": live.get("tier") if live else None,
            "status": live.get("status") if live else None,
            "title": (live.get("title") or "")[:80] if live else None,
            "path": live.get("path") if live else None,
        },
        "phases": phases,
        "gates": {
            "dispatch_ready": False,
            "eval_1b_live": "structural_only_until_openrouter_credits",
        },
        "worker_paste_script": "bash scripts/generate-worker-drain-paste.sh",
        "e2e_validator": "bash scripts/validate-sourcea-e2e-full-v1.sh",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Goal 1 REGISTRY progress")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = goal_progress()
    cache = Path.home() / ".sina" / "goal-progress-v1.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
        return 0
    g = row["goal_1"]
    lp = row["live_pick"]
    drift = f" · DRIFT raw={g.get('raw_done')}" if g.get("drift") else ""
    print(f"GOAL_1: {g['done']}/{g['total']} ({g['pct']}%) honest · backlog {g['backlog']}{drift}")
    print(f"LIVE_PICK: {lp.get('id')} · {lp.get('phase')} · {lp.get('title')}")
    for ph in row["phases"]:
        if ph["backlog"]:
            print(f"  {ph['phase']}: {ph['done']}/{ph['total']} done · {ph['backlog']} backlog")
    print("GOAL-PROGRESS ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
