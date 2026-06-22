#!/usr/bin/env python3
"""Three-machine bundle — Fix 1 → Fix 2 → Fix 3 in strict order.

Law: data/execution-state-desired-observed-v1.json
  Fix 1: hub_single_owner_v1
  Fix 2: phase_reconciler_v1 (read desired · probe · project observed)
  Fix 3: phase_cloud_execute_v1 (live cloud + brain cloud_proof)

Hard gates:
  - Founder alone authors desired — reconciler never writes assignment
  - Preconditions probe ff-001..ff-010 live — closeout not authoritative
  - loop_auto_dispatch stays OFF until dual-pick landed (verified, never enabled here)
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
LOOP_CFG = SINA / "loop-specialist-config-v1.json"

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def assert_loop_auto_off() -> dict:
    cfg = _read(LOOP_CFG)
    auto = bool(cfg.get("loop_auto_dispatch_enabled"))
    dual = {}
    try:
        from _ecosystem_safety_dual_pick_check_v1 import dual_pick_check  # noqa: WPS433

        dual = dual_pick_check()
    except Exception as exc:
        dual = {"ok": False, "error": str(exc)[:120]}
    return {
        "loop_auto_dispatch_enabled": auto,
        "auto_forbidden": True,
        "ok": not auto,
        "dual_pick": dual,
        "note": "Bundle never enables loop auto — dual-pick must pass before ASF enables manually",
    }


def run_bundle(*, dry_run: bool = False, skip_fix3: bool = False, force_reconcile: bool = False) -> dict:
    from hub_single_owner_v1 import ensure_hub, probe_health  # noqa: WPS433
    from phase_reconciler_v1 import reconcile_cycle2_to_market  # noqa: WPS433
    from phase_cloud_execute_v1 import run_fix3  # noqa: WPS433

    loop_gate = assert_loop_auto_off()
    results: dict = {
        "schema": "execution-state-bundle-receipt-v1",
        "at": _now(),
        "dry_run": dry_run,
        "loop_gate": loop_gate,
        "fixes": {},
    }

    # Fix 1 — Hub single owner
    fix1 = ensure_hub() if not dry_run else {"ok": probe_health().get("ok"), "dry_run": True}
    results["fixes"]["fix1_hub"] = fix1
    if not fix1.get("ok"):
        results["ok"] = False
        results["error"] = "fix1_hub_failed"
        return results

    # Fix 2 — Reconcile observed to founder desired (read-only desired)
    fix2 = reconcile_cycle2_to_market(dry_run=dry_run, force=force_reconcile)
    results["fixes"]["fix2_reconcile"] = fix2
    if not fix2.get("ok"):
        results["ok"] = False
        results["error"] = "fix2_reconcile_failed"
        return results

    # Fix 3 — Live cloud + brain cloud_proof (separate machine)
    if skip_fix3:
        results["fixes"]["fix3_cloud"] = {"ok": True, "skipped": True}
    else:
        fix3 = run_fix3(dry_run=dry_run)
        results["fixes"]["fix3_cloud"] = fix3
        if not fix3.get("ok"):
            results["ok"] = False
            results["error"] = "fix3_cloud_failed"
            return results

    results["ok"] = True
    results["line"] = "Fix1 Hub · Fix2 reconcile · Fix3 cloud — bundle PASS"
    out = SINA / "execution-state-bundle-receipt-v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Execution state bundle Fix1→Fix2→Fix3")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-fix3", action="store_true")
    ap.add_argument("--force-reconcile", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run_bundle(dry_run=args.dry_run, skip_fix3=args.skip_fix3, force_reconcile=args.force_reconcile)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("error") or json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
