#!/usr/bin/env python3
"""Shared golden eval helpers for agent runtime factories."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def case_runs_in_mode(case: dict[str, Any], mode: str) -> bool:
    modes = case.get("run_modes") or ["default", "strong"]
    if not isinstance(modes, list):
        modes = ["default", "strong"]
    if bool(case.get("expect_escalated")) and mode == "strong":
        return False
    return mode in modes


def run_golden_batch(
    *,
    golden_path: Path,
    eval_case: Callable[[dict[str, Any], str | None], dict[str, Any]],
    variation_key: str | None = None,
    require_escalation_case: bool = False,
) -> dict[str, Any]:
    doc = json.loads(golden_path.read_text(encoding="utf-8"))
    cases = doc.get("cases") or []
    gate = doc.get("promotion_gate") or {}
    min_rate = float(gate.get("min_pass_rate") or 0.875)
    mode = str(variation_key or "default").strip() or "default"

    results: list[dict[str, Any]] = []
    passed = failed = skipped = escalation_cases = escalation_ok = 0

    for case in cases:
        cid = str(case.get("id") or "")
        if not case_runs_in_mode(case, mode):
            skipped += 1
            results.append({"id": cid, "skipped": True, "ok": True})
            continue

        row = eval_case(case, variation_key)
        actual = str(row.get("verdict") or ("ALLOW" if row.get("ok") else "BLOCKED"))
        if "expect_verdict" in case:
            expect = str(case.get("expect_verdict"))
            ok = actual == expect
        elif "expect_ok" in case:
            ok = bool(row.get("ok")) == bool(case.get("expect_ok"))
            if ok and case.get("expect_step"):
                ok = str(row.get("current_step") or "") == str(case.get("expect_step"))
        else:
            ok = bool(row.get("ok"))

        if case.get("expect_escalated"):
            escalation_cases += 1
            if row.get("escalated") and ok:
                escalation_ok += 1
            elif not row.get("escalated"):
                ok = False

        if ok:
            passed += 1
        else:
            failed += 1
            print(
                f"FAIL case {cid}: expect={case.get('expect_verdict') or case.get('expect_ok')} "
                f"actual={actual} ok={row.get('ok')} escalated={row.get('escalated')}",
                file=sys.stderr,
            )
        results.append({"id": cid, "ok": ok, **{k: row.get(k) for k in ("verdict", "escalated", "current_step")}})

    evaluated = passed + failed
    pass_rate = (passed / evaluated) if evaluated else 0.0
    batch_ok = evaluated > 0 and pass_rate >= min_rate
    if require_escalation_case and mode == "default" and escalation_cases and escalation_ok < escalation_cases:
        batch_ok = False

    return {
        "factory_id": doc.get("factory_id"),
        "eval_mode": mode,
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
    }
