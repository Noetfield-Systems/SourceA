#!/usr/bin/env python3
"""SourceA agent orient — session brief + receipt cascade + role routing + node mesh.

Like Wil `npm run agent:orient` — read-only orientation bundle logged.

Usage:
  python3 scripts/agent_orient_v1.py --json
  python3 scripts/agent_orient_v1.py --role worker
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from orient_routing_v1 import build_orient_report, load_ssot  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA agent orient — routing + cascade")
    ap.add_argument("--role", default="any", choices=["any", "brain", "worker", "governance"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_orient_report(role=args.role)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        ssot = load_ssot()
        print(f"ORIENT ok={row.get('ok')} role={args.role}")
        print(f"  factory: {row.get('factory_now_line', '')[:90]}")
        print(f"  cascade: {row.get('cascade_line')}")
        print(f"  mesh: {row.get('node_mesh_brief')}")
        print(f"  next: {(row.get('role_routing') or {}).get('next_tap', 'RUN INBOX')}")
        print(f"  report: ~/.sina/orient-routing-report-v1.json")
        print(f"  law: {ssot.get('session_start_rule')}")
    return 0 if row.get("schema") == "orient-routing-report-v1" else 1


if __name__ == "__main__":
    raise SystemExit(main())
