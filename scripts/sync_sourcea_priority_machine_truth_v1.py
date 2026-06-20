#!/usr/bin/env python3
"""Sync SOURCEA-PRIORITY.md Machine truth table from live disk (factory-now + goal-progress).

Law: LOCKED doc must match factory-now — not stale FREEZE/sa-0779 ghosts.
Wired: factory_control rebuild · queue_ssot_unify · validate-anti-staleness (future).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def live_signals() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    fn = _read_json(SINA / "factory-now-v1.json")
    gp = _read_json(SINA / "goal-progress-v1.json")
    g1 = gp.get("goal_1") or {}
    crit = _read_json(SINA / "find-bugs" / "last-run.json")
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now() or fn
    except Exception:
        pass
    return {
        "honest_done": g1.get("honest_done", fn.get("valid_yes", "?")),
        "valid_yes": fn.get("valid_yes", g1.get("honest_done", "?")),
        "factory_mode": fn.get("mode", "?"),
        "kill_flag": fn.get("kill_flag"),
        "queue_sa": fn.get("queue_sa", "?"),
        "live_pick": (gp.get("live_pick") or {}).get("id") or fn.get("queue_sa", "?"),
        "find_critical_bugs": crit.get("critical_count", crit.get("critical", "?")),
        "dispatch_ready": (gp.get("gates") or {}).get("dispatch_ready", "?"),
        "eval_1b_gate_ok": (gp.get("gates") or {}).get("eval_1b_live", "?"),
        "at": _now(),
    }


def sync_priority_machine_truth(*, dry_run: bool = False) -> dict:
    if not PRIORITY.is_file():
        return {"ok": False, "error": "SOURCEA-PRIORITY.md missing"}

    sig = live_signals()
    text = PRIORITY.read_text(encoding="utf-8")
    if "## Machine truth" not in text:
        return {"ok": False, "error": "Machine truth section missing"}

    table = (
        "## Machine truth\n\n"
        "| Signal | Value |\n"
        "|--------|-------|\n"
        f"| honest_done | {sig['honest_done']} / 1000 |\n"
        f"| valid_yes | {sig['valid_yes']} |\n"
        f"| factory_mode | {sig['factory_mode']} |\n"
        f"| kill_flag | {sig['kill_flag']} |\n"
        f"| queue_sa | {sig['queue_sa']} (dual-pick law — wins over phase-first head) |\n"
        f"| live_pick | {sig['live_pick']} |\n"
        f"| find_critical_bugs | critical {sig['find_critical_bugs']} |\n"
        f"| dispatch_ready | {sig['dispatch_ready']} |\n"
        f"| eval_1b_gate_ok | {sig['eval_1b_gate_ok']} |\n"
        f"| synced_at | {sig['at']} |\n"
    )

    new_text, n = re.subn(
        r"## Machine truth\n\n\| Signal \| Value \|\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)+",
        table,
        text,
        count=1,
    )
    if n != 1:
        return {"ok": False, "error": "machine_truth_table_replace_failed", "signals": sig}

    if not dry_run:
        PRIORITY.write_text(new_text, encoding="utf-8")

    return {"ok": True, "dry_run": dry_run, "signals": sig, "path": str(PRIORITY)}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Sync SOURCEA-PRIORITY machine truth from disk")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = sync_priority_machine_truth(dry_run=args.dry_run)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
