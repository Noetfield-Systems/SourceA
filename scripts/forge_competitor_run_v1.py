#!/usr/bin/env python3
"""Hub chain: pick → task graph → FORGE dispatch → verify (founder no Terminal)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from portfolio_competitor_pick_lib import enrich_pick, load_registry, phase_order, pick_backlog_plans, resolve_stack  # noqa: E402
from portfolio_competitor_forge_dispatch_v1 import dispatch_pick  # noqa: E402


def run_competitor_forge(*, stack: str, dry_run: bool = False, plan_id: str = "") -> dict[str, Any]:
    stack_key = resolve_stack(stack)
    registry = load_registry(stack_key)
    if plan_id:
        raw = next((p for p in registry.get("plans") or [] if p.get("id") == plan_id), None)
        if not raw:
            return {"ok": False, "error": f"plan_not_found:{plan_id}"}
        pick = enrich_pick(stack_key, raw, registry)
    else:
        backlog = pick_backlog_plans(
            registry.get("plans") or [],
            phases=phase_order(registry),
            tiers=("T0", "T1", "T2", "T3"),
            limit=1,
        )
        if not backlog:
            return {"ok": False, "error": "no_backlog"}
        pick = enrich_pick(stack_key, backlog[0], registry)

    dispatch = dispatch_pick(pick, dry_run=dry_run, mode="railway_fbe")
    verify: dict[str, Any] = {}
    if not dry_run and dispatch.get("ok"):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/fbe_verify_forge_v1.py"), "--bay", "forge-bay", "--json"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=120,
        )
        try:
            verify = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            verify = {"ok": False, "raw": proc.stdout[:400]}

    ok = bool(dispatch.get("ok")) and (dry_run or verify.get("ok", False))
    show = (
        f"{pick.get('stack')} · {pick.get('id')} · {pick.get('competitor')} — "
        f"FORGE {'dry-run' if dry_run else 'cloud'} · verify={'PASS' if verify.get('ok') else 'pending' if dry_run else 'FAIL'}"
    )
    return {
        "ok": ok,
        "schema": "forge-competitor-run-v1",
        "stack": pick.get("stack"),
        "plan_id": pick.get("id"),
        "competitor": pick.get("competitor"),
        "dry_run": dry_run,
        "dispatch": dispatch,
        "verify": verify,
        "for_founder": {"show_this": show, "why": dispatch.get("for_founder", {}).get("show_this", "")},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", required=True)
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_competitor_forge(stack=args.stack, dry_run=args.dry_run, plan_id=args.plan_id)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("for_founder", {}).get("show_this", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
