#!/usr/bin/env python3
"""ZCP bridge — thin CLI + forge_terminal import surface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zcp.zcp_ingest_v1 import critic_gate, ingest, list_receipts, parse_only  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="ZCP bridge — Forge Terminal")
    ap.add_argument("command", choices=["parse", "ingest", "critic", "receipts"], nargs="?", default="parse")
    ap.add_argument("--input", "-i", default="", help="TASK | FIX | CRITIC block or JSON")
    ap.add_argument("--text", "-t", default="", help="alias for --input")
    ap.add_argument("--plane", choices=["parse_only", "cursor", "cloud", "auto"], default="auto")
    ap.add_argument("--dispatch", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = args.input or args.text or sys.stdin.read()
    if args.command == "parse":
        row = parse_only(text)
    elif args.command == "ingest":
        row = ingest(input_text=text, plane=args.plane, dispatch=args.dispatch, dry_run=args.dry_run)
    elif args.command == "critic":
        try:
            output = json.loads(text)
        except json.JSONDecodeError:
            output = {"risk": ["invalid json"], "fix_priority": [], "drift_score": 10}
        row = critic_gate(output if isinstance(output, dict) else {})
    else:
        row = {"ok": True, "receipts": list_receipts()}
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
