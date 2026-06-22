#!/usr/bin/env python3
"""Read-only promotion gate report — golden eval for default + strong (founder manual bump only).

Never writes active_variation_key or config_version to SSOT.
Receipt: ~/.sina/agent-runtime-promotion-report-v1.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
BAY_SSOT = ROOT / "data" / "cloud-comprehension-bay-v1.json"
RECEIPT = SINA / "agent-runtime-promotion-report-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_report(*, write_receipt: bool = True) -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from fbe_comprehension_eval_batch_v1 import run_eval_batch  # noqa: WPS433

    ssot = _read_json(BAY_SSOT)
    gate = ssot.get("promotion_gate") or {}
    min_rate = float(gate.get("min_pass_rate") or 0.875)
    active = str(ssot.get("active_variation_key") or "default")

    default_batch = run_eval_batch(
        variation_key="default",
        write_receipt=False,
        require_escalation_case=True,
    )
    strong_batch = run_eval_batch(variation_key="strong", write_receipt=False)

    default_rate = float(default_batch.get("pass_rate") or 0.0)
    strong_rate = float(strong_batch.get("pass_rate") or 0.0)
    default_ok = bool(default_batch.get("ok"))
    strong_ok = bool(strong_batch.get("ok"))
    promotion_ready = default_ok and strong_ok

    if promotion_ready:
        show = (
            f"Golden eval ready — default {default_batch.get('passed')}/{default_batch.get('total')} "
            f"({default_rate:.0%}) · strong {strong_batch.get('passed')}/{strong_batch.get('total')} "
            f"({strong_rate:.0%}). Active variation is `{active}`. Manual SSOT bump only if you choose."
        )
    else:
        failed = (default_batch.get("failed") or 0) + (strong_batch.get("failed") or 0)
        show = (
            f"Not ready for promotion — default {default_rate:.0%} · strong {strong_rate:.0%} "
            f"(need {min_rate:.0%} each). {failed} case(s) failed. Fix bay or golden set before any bump."
        )

    row: dict[str, Any] = {
        "schema": "agent-runtime-promotion-report-v1",
        "at": _now(),
        "ok": promotion_ready,
        "promotion_ready": promotion_ready,
        "active_variation_key": active,
        "min_pass_rate": min_rate,
        "default_pass_rate": default_rate,
        "strong_pass_rate": strong_rate,
        "default_batch": {
            "passed": default_batch.get("passed"),
            "failed": default_batch.get("failed"),
            "total": default_batch.get("total"),
            "escalation_ok": default_batch.get("escalation_ok"),
        },
        "strong_batch": {
            "passed": strong_batch.get("passed"),
            "failed": strong_batch.get("failed"),
            "total": strong_batch.get("total"),
        },
        "for_founder": {"show_this": show, "blocked": not promotion_ready},
        "note": "Read-only — agents must not auto-promote active_variation_key",
    }

    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Agent runtime promotion report v1 (read-only)")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_report(write_receipt=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print((row.get("for_founder") or {}).get("show_this") or row)
    return 0 if row.get("promotion_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
