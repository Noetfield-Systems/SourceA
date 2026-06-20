#!/usr/bin/env python3
"""Agentic layer wire sync — delegates to pipeline v2 (backward-compatible wrapper).

Law: SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md
Receipt: ~/.sina/agentic-layer-wire-sync-v1.json · ~/.sina/agentic-layer-pipeline-v2.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def sync_agentic_layer_wire(*, sync_brain: bool = True, self_heal: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from agentic_layer_pipeline_v2 import run_agentic_pipeline_v2  # noqa: WPS433

    tier = "full" if sync_brain else "fast"
    v2 = run_agentic_pipeline_v2(sync_brain=sync_brain, self_heal=self_heal, tier=tier)
    return {
        "ok": v2.get("ok"),
        "schema": "agentic-layer-wire-sync-v1",
        "at": v2.get("at"),
        "ms": v2.get("ms"),
        "pipeline_v2": str(Path.home() / ".sina" / "agentic-layer-pipeline-v2.json"),
        "queue_head": (v2.get("brain_summary") or {}).get("queue_head"),
        "health_status": (v2.get("health") or {}).get("status"),
        "issues_count": len(v2.get("issues") or []),
        "l1_to_brain": (v2.get("l1_summary") or {}).get("l1_to_brain"),
        "l2_wired": (v2.get("brain_summary") or {}).get("l2_wired"),
        "delegates_to": "agentic_layer_pipeline_v2.py",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync all agentic layer wires (v2 wrapper)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-sync", action="store_true")
    ap.add_argument("--self-heal", action="store_true")
    args = ap.parse_args()
    row = sync_agentic_layer_wire(sync_brain=not args.no_sync, self_heal=args.self_heal)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
