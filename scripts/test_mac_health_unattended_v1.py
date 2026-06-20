#!/usr/bin/env python3
"""Simulate unattended prevention streak — dry-run proof (UPGR-032 / Step 7)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

STREAK_PATH = Path.home() / ".sina" / "mac-health" / "unattended-pulse-streak-v1.json"
DOC_PATH = Path.home() / ".sina" / "mac-health" / "unattended-prevention-doc-v1.json"
CONFIG_PATH = Path.home() / ".sina" / "config" / "mac-health-panic-v1.json"


def _load_config() -> dict:
    from mac_health_emergency_stop_v1 import _load_config  # noqa: WPS433

    return _load_config()


def simulate(*, execute: bool = False) -> dict:
    """Increment streak to threshold; optionally fire unattended panic (dry-run when execute)."""
    cfg = (_load_config().get("unattended") or {})
    threshold = int(cfg.get("consecutive_unhealthy_pulses") or 4)
    enabled = bool(cfg.get("auto_panic_on_runaway", True))

    doc = {
        "schema": "unattended-prevention-doc-v1",
        "auto_panic_on_runaway": enabled,
        "consecutive_unhealthy_pulses": threshold,
        "cursor_cpu_panic": cfg.get("cursor_cpu_panic", 90),
        "config_path": str(CONFIG_PATH),
        "note": "Off only when auto_panic_on_runaway=false in mac-health-panic-v1.json",
    }
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    if not enabled:
        return {"ok": True, "skipped": True, "reason": "auto_panic_off", "doc": str(DOC_PATH)}

    prevention = {"health": "unattended", "cursor": {"cpu_sum": 300}, "queue_zombies": 0}
    STREAK_PATH.parent.mkdir(parents=True, exist_ok=True)
    STREAK_PATH.write_text(json.dumps({"count": threshold - 1, "simulated": True}) + "\n")

    import mac_health_emergency_stop_v1 as m

    orig_run = m.run_mac_health_emergency_stop

    def patched_run(*args, **kwargs):
        kwargs.setdefault("dry_run", not execute)
        kwargs.setdefault("notify", False)
        return orig_run(*args, **kwargs)

    m.run_mac_health_emergency_stop = patched_run
    receipt = m.maybe_unattended_panic(prevention)
    m.run_mac_health_emergency_stop = orig_run

    row = {
        "ok": receipt is not None,
        "threshold": threshold,
        "receipt_trigger": (receipt or {}).get("trigger"),
        "unattended_streak": (receipt or {}).get("unattended_streak"),
        "dry_run": (receipt or {}).get("dry_run"),
        "doc": str(DOC_PATH),
        "streak_path": str(STREAK_PATH),
    }
    proof = Path.home() / ".sina" / "mac-health" / "unattended-test-proof-v1.json"
    proof.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["proof"] = str(proof)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Unattended prevention streak test")
    ap.add_argument("--execute", action="store_true", help="Real panic (default: dry-run only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = simulate(execute=args.execute)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
