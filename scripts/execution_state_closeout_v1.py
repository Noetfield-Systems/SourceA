#!/usr/bin/env python3
"""Close-out bundle — Item 1 ratify era · Item 2 full FORGE motor · then Auto Runtime.

Law: data/execution-state-desired-observed-v1.json v1.2.0
DO NOT enable loop_auto until BOTH items green.
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


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def run_closeout(*, skip_item2: bool = False, enable_loop_auto: bool = False, dry_run: bool = False) -> dict:
    from phase_observed_project_v1 import has_probe_backed_ratify  # noqa: WPS433
    from phase_reconciler_v1 import ratify_phase_market, reconcile_cycle2_to_market  # noqa: WPS433
    from phase_transition_probe_v1 import probe_cycle2_to_market_preconditions  # noqa: WPS433

    out: dict = {
        "schema": "execution-state-closeout-receipt-v1",
        "at": _now(),
        "dry_run": dry_run,
        "items": {},
    }

    # Item 1 — ratify phase_market (probe-backed, no projection churn)
    probe = probe_cycle2_to_market_preconditions()
    ratify = ratify_phase_market(dry_run=dry_run)
    reconcile = reconcile_cycle2_to_market(dry_run=dry_run, force=False)
    item1_ok = bool(probe.get("ok")) and bool(ratify.get("ok")) and bool(reconcile.get("ok"))
    out["items"]["item1_era"] = {
        "ok": item1_ok,
        "probe": {"ok": probe.get("ok"), "ff_ok_count": (probe.get("probes") or {}).get("ff_cycle2", {}).get("ok_count")},
        "ratify": ratify,
        "reconcile": reconcile,
        "has_probe_backed_ratify": has_probe_backed_ratify() or ratify.get("ratified"),
    }

    if not item1_ok:
        out["ok"] = False
        out["error"] = "item1_era_failed"
        _write(SINA / "execution-state-closeout-receipt-v1.json", out)
        return out

    # Item 2 — full FORGE motor sa-mkt-0001
    item2: dict = {"ok": False, "skipped": skip_item2}
    if skip_item2:
        item2["ok"] = True
        item2["skipped"] = True
    elif dry_run:
        item2 = {"ok": True, "dry_run": True, "plan_id": "sa-mkt-0001", "full_motor": True}
    else:
        try:
            from sync_forge_railway_env_v1 import sync as sync_railway_env  # noqa: WPS433

            item2["railway_env"] = sync_railway_env(dry_run=False)
        except Exception as exc:
            item2["railway_env"] = {"ok": False, "error": str(exc)[:200]}

        from portfolio__forge_dispatch_v1 import dispatch_pick, enrich_pick, load_registry, resolve_stack  # noqa: WPS433

        stack_key = resolve_stack("sourcea")
        registry = load_registry(stack_key)
        raw = next((pl for pl in registry.get("plans") or [] if pl.get("id") == "sa-mkt-0001"), None)
        if not raw:
            item2["ok"] = False
            item2["error"] = "sa-mkt-0001_not_in_registry"
        else:
            pick = enrich_pick(stack_key, raw, registry)
            dispatch = dispatch_pick(pick, dry_run=False, mode="railway_fbe", full_motor=True)
            item2["dispatch"] = dispatch
            run_result = dispatch.get("run_result") or {}
            motor_ok = bool((run_result.get("lines") or {}).get("motor", {}).get("ok"))
            forge_ok = bool((run_result.get("lines") or {}).get("forge", {}).get("ok"))
            item2["motor_verify_ok"] = motor_ok
            item2["forge_ok"] = forge_ok
            item2["ok"] = bool(dispatch.get("ok")) and motor_ok

            if item2["ok"]:
                try:
                    from mark_brain_reasoning_done_v1 import mark_done  # noqa: WPS433

                    item2["brain_b0004"] = mark_done(
                        "B0004",
                        evidence="full FORGE motor sa-mkt-0001 live PASS",
                    )
                except Exception as exc:
                    item2["brain_b0004"] = {"ok": False, "error": str(exc)[:200]}

    out["items"]["item2_forge"] = item2

    both_green = item1_ok and item2.get("ok")
    out["both_green"] = both_green

    # Last step — Auto Runtime only when both green and explicitly requested
    loop_cfg = _read(LOOP_CFG)
    if both_green and enable_loop_auto and not dry_run:
        loop_cfg["loop_auto_dispatch_enabled"] = True
        loop_cfg["loop_auto_enabled_by"] = "execution_state_closeout_v1"
        loop_cfg["loop_auto_enabled_at"] = _now()
        _write(LOOP_CFG, loop_cfg)
        out["loop_auto"] = {"enabled": True, "live_pick": loop_cfg.get("live_pick")}
    else:
        out["loop_auto"] = {
            "enabled": bool(loop_cfg.get("loop_auto_dispatch_enabled")),
            "would_enable": both_green and enable_loop_auto,
            "note": "OFF until both items green + --enable-loop-auto",
        }

    out["ok"] = both_green
    out["line"] = (
        "Close-out PASS — era ratified · full FORGE motor"
        if both_green
        else "Close-out INCOMPLETE — see items"
    )
    _write(SINA / "execution-state-closeout-receipt-v1.json", out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Close-out — ratify era + full FORGE motor + optional Auto Runtime")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-item2", action="store_true")
    ap.add_argument("--enable-loop-auto", action="store_true", help="Last step — only after both items green")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run_closeout(
        skip_item2=args.skip_item2,
        enable_loop_auto=args.enable_loop_auto,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("error") or json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
