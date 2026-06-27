#!/usr/bin/env python3
"""Light smoke — ZCP bridge parse + ingest (no server required for parse)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from zcp.zcp_ingest_v1 import ingest, parse_only  # noqa: E402


def main() -> int:
    fix = """FIX:
target: apps/diff-engine/src/applier.ts
issue: unified diff not applied atomically"""
    parsed = parse_only(fix)
    if not parsed.get("ok"):
        print(json.dumps({"ok": False, "step": "parse", "row": parsed}, indent=2))
        return 1
    row = ingest(input_text=fix, plane="parse_only", dry_run=True)
    if not row.get("ok"):
        print(json.dumps({"ok": False, "step": "ingest", "row": row}, indent=2))
        return 1
    print(json.dumps({"ok": True, "schema": "zcp-bridge-smoke-v1", "mode": row.get("zcp", {}).get("mode"), "task_id": row.get("task_id")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
