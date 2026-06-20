#!/usr/bin/env python3
"""SSOT: 1000-step program honest status for hub/monitor (not raw REGISTRY)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
OUT = Path.home() / ".sina" / "PROGRAM_1000_HONEST_STATUS.json"

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


def build_status() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from registry_honest_lib_v1 import audit_registry_done, honest_receipt_ids  # noqa: WPS433

    audit = audit_registry_done()
    honest = set(honest_receipt_ids())
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg.get("plans") or []

    phases = []
    for ph in PHASE_ORDER:
        rows = [p for p in plans if p.get("phase") == ph]
        if not rows:
            continue
        phases.append(
            {
                "phase": ph,
                "total": len(rows),
                "honest_done": sum(1 for p in rows if p.get("id") in honest),
                "backlog": sum(1 for p in rows if p.get("status") == "backlog"),
                "raw_done": sum(1 for p in rows if p.get("status") == "done"),
            }
        )

    return {
        "schema": "program-1000-honest-status-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": 1000,
        "honest_done": audit["honest_done"],
        "backlog": 1000 - audit["honest_done"],
        "unproven_done": audit["unproven_done"],
        "drift": audit["drift"],
        "pct": round(100.0 * audit["honest_done"] / 1000, 2),
        "phases": phases,
        "law": "done = receipt only; reconcile closes backlog when verify PASS",
        "next": "healthy-queue drain + machine reconcile for validator-pass backlog",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true")
    args = p.parse_args()
    row = build_status()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json or not args.write:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
