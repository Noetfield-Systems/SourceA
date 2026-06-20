#!/usr/bin/env python3
"""Mark competitor plan done in REGISTRY + append PRIORITY evidence row."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from portfolio_competitor_pick_lib import STACKS, load_registry, resolve_stack  # noqa: E402


def closeout_plan(*, stack_key: str, plan_id: str, evidence_path: str = "") -> dict:
    cfg = STACKS[stack_key]
    registry = load_registry(stack_key)
    plans = registry.get("plans") or []
    target = next((p for p in plans if p.get("id") == plan_id), None)
    if not target:
        return {"ok": False, "error": f"plan_not_found:{plan_id}"}
    target["status"] = "done"
    target["closed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if evidence_path:
        target["evidence_path"] = evidence_path
    reg_path = cfg["pack_root"] / "REGISTRY.json"
    reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    priority_rel = {
        "sourcea": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
        "witnessbc": "witnessbc-site/content/pricing.html",
        "noetfield": "os/plan-library/NOETFIELD-PRIORITY.md",
        "trustfield": "prompts/future-plans-1000.json",
        "virlux": "os/plan-library/VIRLUX-PRIORITY.md",
    }.get(stack_key, "")
    priority_path = cfg["repo_root"] / priority_rel if priority_rel else None
    line = (
        f"| {plan_id} | done | {target.get('competitor')} | {target.get('workstream')} | "
        f"{evidence_path or 'forge-bay trace'} |"
    )
    if priority_path and priority_path.suffix == ".md" and priority_path.parent.exists():
        with priority_path.open("a", encoding="utf-8") as f:
            f.write(f"\n<!-- forge-competitor-closeout {target['closed_at']} -->\n{line}\n")

    return {"ok": True, "plan_id": plan_id, "stack": cfg["stack"], "registry": str(reg_path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", required=True)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--evidence", default="receipts/bays/forge-bay/trace/")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = closeout_plan(stack_key=resolve_stack(args.stack), plan_id=args.plan_id, evidence_path=args.evidence)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
