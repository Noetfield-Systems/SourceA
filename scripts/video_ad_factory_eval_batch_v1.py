#!/usr/bin/env python3
"""Offline golden eval for video-ad-factory runtime."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GOLDEN = ROOT / "data" / "video-ad-factory-golden-v1.json"
FACTORY_ID = "video-ad-factory-v1"


def _eval_case(case: dict[str, Any], variation_key: str | None) -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from agent_runtime_config_v1 import load_factory_runtime_config  # noqa: WPS433
    from video_ad_factory_orchestrate_v1 import preview_orchestration  # noqa: WPS433

    cfg = load_factory_runtime_config(FACTORY_ID, variation_key=variation_key)
    raw_brief = str(case.get("raw_brief") or "")
    if not raw_brief.strip():
        return {"ok": False, "verdict": "BLOCKED", "error": "empty_brief"}
    return preview_orchestration(raw_brief, cfg=cfg)


def main() -> int:
    import argparse

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from agent_runtime_golden_eval_v1 import run_golden_batch  # noqa: WPS433

    ap = argparse.ArgumentParser()
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_golden_batch(
        golden_path=GOLDEN,
        eval_case=_eval_case,
        variation_key=args.variation_key or None,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"video-ad golden {row.get('passed')}/{row.get('evaluated')} pass_rate={row.get('pass_rate')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
