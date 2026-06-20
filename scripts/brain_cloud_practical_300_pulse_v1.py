#!/usr/bin/env python3
"""Pulse brain-cloud-practical-300-plan — hub + brain + live surfaces."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "brain-cloud-practical-300-plan-v1.json"
RECEIPT = Path.home() / ".sina/brain-cloud-practical-300-pulse-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_pulse(*, write: bool = True) -> dict:
    if not PLAN.is_file():
        return {"ok": False, "error": "missing plan", "schema": "brain-cloud-practical-300-pulse-v1"}
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    plans = plan.get("plans") or []
    done = sum(1 for p in plans if p.get("status") == "done")
    total = int(plan.get("progress", {}).get("total") or len(plans))
    cloud_proven = int(plan.get("progress", {}).get("cloud_proven") or 0)
    head = next((p for p in plans if p.get("status") != "done"), {})
    version = str(plan.get("version") or "1.0.0")
    if done >= total and total > 0:
        head_id = "C300-300"
        head_goal = "complete"
        line = (
            f"cloud-300 · v{version} · {done}/{total} done · cloud_proven={cloud_proven} · "
            f"head={head_id} · {head_goal}"
        )
    else:
        line = (
            f"cloud-300 · v{version} · {done}/{total} done · cloud_proven={cloud_proven} · "
            f"head={head.get('id')} · {head.get('goal_alignment')}"
        )
    row = {
        "ok": True,
        "schema": "brain-cloud-practical-300-pulse-v1",
        "at": _now(),
        "plan_path": str(PLAN),
        "plan_version": version,
        "total": total,
        "done": done,
        "cloud_proven": cloud_proven,
        "unique_titles": plan.get("unique_titles"),
        "head_id": head.get("id") if done < total else "C300-300",
        "head_title": head.get("title") if done < total else "C300 plan 300/300 cloud_proven — migration complete",
        "head_phase": head.get("phase") if done < total else "P3-SCALE",
        "head_goal": head.get("goal_alignment") if done < total else "complete",
        "critical_path": plan.get("critical_path"),
        "north_star": plan.get("north_star"),
        "compile_order": plan.get("compile_order"),
        "cloud_practical_300_line": line,
    }
    if write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice(*, refresh: bool = False) -> dict:
    return run_pulse(write=refresh)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", default=True)
    args = ap.parse_args()
    row = run_pulse(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("cloud_practical_300_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
