#!/usr/bin/env python3
"""Offline golden eval batch for comprehension bay — benchmark before config promotion."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GOLDEN_PATH = ROOT / "data/comprehension-golden-v1.json"
RECEIPTS_DIR = ROOT / "receipts" / "comprehension-eval"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _eval_mode(variation_key: str | None) -> str:
    return str(variation_key or "default").strip() or "default"


def _case_runs_in_mode(case: dict[str, Any], mode: str) -> bool:
    modes = case.get("run_modes") or ["default", "strong"]
    if not isinstance(modes, list):
        modes = ["default", "strong"]
    if bool(case.get("expect_escalated")) and mode == "strong":
        return False
    return mode in modes


def _dump_failures(results: list[dict[str, Any]]) -> None:
    for row in results:
        if row.get("ok") and not row.get("skipped"):
            continue
        if row.get("skipped"):
            continue
        print(
            f"FAIL case {row.get('id')}: expect={row.get('expect_verdict')} "
            f"actual={row.get('actual_verdict')} escalated={row.get('escalated')}",
            file=sys.stderr,
        )


def run_eval_batch(
    *,
    variation_key: str | None = None,
    write_receipt: bool = True,
    require_escalation_case: bool = False,
) -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from fbe_comprehension_bay_v1 import run_comprehension_bay  # noqa: WPS433
    from agent_runtime_config_v1 import load_bay_config  # noqa: WPS433

    doc = _read_json(GOLDEN_PATH)
    cases = doc.get("cases") or []
    gate = doc.get("promotion_gate") or {}
    min_rate = float(gate.get("min_pass_rate") or 0.875)
    mode = _eval_mode(variation_key)

    cfg = load_bay_config("comprehension-loop-bay", variation_key=variation_key)
    results: list[dict[str, Any]] = []
    passed = 0
    failed = 0
    skipped = 0
    escalation_cases = 0
    escalation_ok = 0

    for case in cases:
        cid = str(case.get("id") or "")
        if not _case_runs_in_mode(case, mode):
            skipped += 1
            results.append(
                {
                    "id": cid,
                    "skipped": True,
                    "reason": f"not_applicable_in_mode_{mode}",
                    "ok": True,
                }
            )
            continue

        expect = str(case.get("expect_verdict") or "ACCEPT")
        expect_escalated = bool(case.get("expect_escalated"))
        row = run_comprehension_bay(
            draft=str(case.get("draft") or ""),
            founder_message=str(case.get("founder_message") or ""),
            variation_key=variation_key or cfg.get("variation_key"),
        )
        actual = str(row.get("verdict") or "")
        escalated = bool(row.get("escalated"))
        ok = actual == expect
        if expect_escalated:
            escalation_cases += 1
            if escalated and actual == "ACCEPT":
                escalation_ok += 1
            elif not escalated or actual != "ACCEPT":
                ok = False
        if ok:
            passed += 1
        else:
            failed += 1
        results.append(
            {
                "id": cid,
                "expect_verdict": expect,
                "expect_escalated": expect_escalated,
                "actual_verdict": actual,
                "escalated": escalated,
                "attempts": row.get("attempts") or [],
                "ok": ok,
                "meaning_score": row.get("meaning_score"),
                "variation_key": row.get("variation_key"),
            }
        )

    evaluated = passed + failed
    pass_rate = (passed / evaluated) if evaluated else 0.0
    batch_ok = evaluated > 0 and pass_rate >= min_rate
    if require_escalation_case and mode == "default" and escalation_cases and escalation_ok < escalation_cases:
        batch_ok = False

    batch_id = f"comprehension-eval-{uuid.uuid4().hex[:12]}"
    receipt = {
        "schema": "comprehension-eval-batch-receipt-v1",
        "receipt_id": batch_id,
        "at": _now(),
        "eval_mode": mode,
        "variation_key": cfg.get("variation_key"),
        "config_version": cfg.get("config_version"),
        "total": len(cases),
        "evaluated": evaluated,
        "skipped": skipped,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 4),
        "min_pass_rate": min_rate,
        "escalation_cases": escalation_cases,
        "escalation_ok": escalation_ok,
        "ok": batch_ok,
        "results": results,
        "for_founder": {
            "show_this": (
                f"Golden eval · {cfg.get('variation_key')} · {passed}/{evaluated} pass "
                f"({pass_rate:.0%}) · skipped {skipped} · {'PASS' if batch_ok else 'FAIL'}"
            )
        },
    }

    if not batch_ok:
        _dump_failures(results)

    if write_receipt:
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RECEIPTS_DIR / f"{batch_id}.json"
        receipt["receipt_path"] = str(path)
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--require-escalation-case", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_eval_batch(
        variation_key=args.variation_key or None,
        write_receipt=not args.no_write,
        require_escalation_case=bool(args.require_escalation_case),
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print((row.get("for_founder") or {}).get("show_this") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
