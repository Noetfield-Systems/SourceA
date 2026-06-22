#!/usr/bin/env python3
"""Offline golden eval for Noetfield copilot runtime."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GOLDEN = ROOT / "data" / "noetfield-copilot-golden-v1.json"


def _eval_case(case: dict[str, Any], variation_key: str | None) -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from noetfield_copilot_runtime_v1 import evaluate_copilot_action  # noqa: WPS433

    return evaluate_copilot_action(
        action=str(case.get("action") or ""),
        payload=dict(case.get("payload") or {}),
        tenant=str(case.get("tenant") or "pilot-tenant-a"),
        variation_key=variation_key,
        write_receipt=False,
        allow_escalation=not bool(case.get("no_escalation")),
    )


def main() -> int:
    import argparse

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from agent_runtime_golden_eval_v1 import run_golden_batch  # noqa: WPS433

    ap = argparse.ArgumentParser()
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--require-escalation-case", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_golden_batch(
        golden_path=GOLDEN,
        eval_case=_eval_case,
        variation_key=args.variation_key or None,
        require_escalation_case=bool(args.require_escalation_case),
    )
    if args.json:
        import json

        print(json.dumps(row, indent=2))
    else:
        print(f"noetfield copilot golden {row.get('passed')}/{row.get('evaluated')} pass_rate={row.get('pass_rate')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
