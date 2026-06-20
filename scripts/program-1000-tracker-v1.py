#!/usr/bin/env python3
"""Live 1000-step tracker — disk SSOT for founder, Brain, Claude, monitor."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = Path.home() / ".sina" / "PROGRAM_1000_TRACKER.json"
HISTORY = Path.home() / ".sina" / "PROGRAM_1000_TRACKER_HISTORY.jsonl"
CSV = Path.home() / ".sina" / "audits" / "PROGRAM_1000_TRACKER_LIVE.csv"

GOAL_TOTAL = 1000
PLAN_START = datetime(2026, 6, 9, tzinfo=timezone.utc)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _categorize_backlog() -> dict:
    import re

    reg = json.loads((ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text())
    logs = ROOT / "REPO_EXECUTION_LOGS/sourcea"
    quar = logs / "QUARANTINE_BATCH_YAML"
    q_sas = set()
    if quar.is_dir():
        for p in quar.glob("*.yaml"):
            m = re.search(r"(sa-\d{4})", p.name)
            if m:
                q_sas.add(m.group(1))

    never, attempted = [], []
    for p in reg.get("plans") or []:
        if p.get("status") != "backlog":
            continue
        sa = p.get("id") or ""
        if sa in q_sas:
            attempted.append(sa)
        else:
            never.append(sa)
    return {"never_touched": never, "validate_first": attempted}


def build_tracker(*, note: str = "") -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

    audit = audit_registry_done()
    cats = _categorize_backlog()
    honest = int(audit["honest_done"])
    backlog = GOAL_TOTAL - honest
    day = min(3, max(1, (datetime.now(timezone.utc) - PLAN_START).days + 1))

    # 3-day plan: reconcile B first, then phase-first drain
    day_plans = {
        1: {
            "label": "Day 1 — Validate-first (bucket B)",
            "action": "Hub: Reconcile 1000 (validator PASS) — repeat until count stops rising",
            "target_honest": min(honest + 80, GOAL_TOTAL),
            "focus": "478 tasks with quarantined YAML — verify only, no rebuild",
        },
        2: {
            "label": "Day 2 — Phase s0 drain",
            "action": "Worker: run inbox — one turn per sa (CHECK→ACT→VERIFY)",
            "target_honest": min(honest + 150, GOAL_TOTAL),
            "focus": "phase-s0-ssot-alignment backlog + remaining B failures",
        },
        3: {
            "label": "Day 3 — Phase s0 + s2 continue",
            "action": "Worker drain + reconcile batches",
            "target_honest": min(honest + 220, GOAL_TOTAL),
            "focus": "Never-touched bucket A — one sa at a time",
        },
    }
    plan = day_plans[day]
    remaining_to_target = max(0, plan["target_honest"] - honest)
    per_day_pace = round(remaining_to_target / max(1, 4 - day), 1)

    row = {
        "schema": "program-1000-tracker-v1",
        "updated_at": _now(),
        "plan_start": PLAN_START.strftime("%Y-%m-%d"),
        "current_day": day,
        "honest_done": honest,
        "backlog": backlog,
        "pct": round(100.0 * honest / GOAL_TOTAL, 2),
        "unproven_done": audit["unproven_done"],
        "buckets": {
            "done": honest,
            "never_touched": len(cats["never_touched"]),
            "validate_first": len(cats["validate_first"]),
        },
        "law": "done = verify PASS + receipt only — never rebuild from scratch",
        "today": plan,
        "pace": {
            "need_per_day_to_hit_today_target": per_day_pace,
            "remaining_to_today_target": remaining_to_target,
        },
        "next_tap": [
            "Refresh monitor — http://127.0.0.1:13021/monitor",
            "Hub: Reconcile 1000 (validator PASS)" if day == 1 else "Worker: run inbox once",
        ],
        "verify_paths": {
            "tracker_json": str(TRACKER),
            "tracker_csv": str(CSV),
            "history_jsonl": str(HISTORY),
            "step_matrix_json": str(Path.home() / ".sina" / "PROGRAM_1000_STEP_MATRIX.json"),
            "step_matrix_csv": str(Path.home() / ".sina" / "audits" / "PROGRAM_1000_STEP_MATRIX_LIVE.csv"),
            "honest_gate": "bash scripts/validate-registry-honest-gate-v1.sh",
            "monitor_steps": "http://127.0.0.1:13021/monitor#matrix",
        },
        "note": note,
    }
    return row


def write_tracker(*, note: str = "") -> dict:
    row = build_tracker(note=note)
    TRACKER.parent.mkdir(parents=True, exist_ok=True)
    TRACKER.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "at": row["updated_at"],
                    "honest_done": row["honest_done"],
                    "backlog": row["backlog"],
                    "day": row["current_day"],
                }
            )
            + "\n"
        )
    CSV.parent.mkdir(parents=True, exist_ok=True)
    CSV.write_text(
        "at,honest_done,backlog,pct,never_touched,validate_first,current_day,target_honest\n"
        f"{row['updated_at']},{row['honest_done']},{row['backlog']},{row['pct']},"
        f"{row['buckets']['never_touched']},{row['buckets']['validate_first']},"
        f"{row['current_day']},{row['today']['target_honest']}\n",
        encoding="utf-8",
    )
    repo_csv = ROOT / "REPO_EXECUTION_LOGS/sourcea/PROGRAM_1000_TRACKER_LIVE.csv"
    repo_csv.write_text(CSV.read_text(encoding="utf-8"), encoding="utf-8")
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--note", default="")
    args = p.parse_args()
    row = write_tracker(note=args.note)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        t = row["today"]
        print(
            f"TRACKER: {row['honest_done']}/{GOAL_TOTAL} honest · day {row['current_day']}/3 · "
            f"target today {t['target_honest']} · {t['action']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
