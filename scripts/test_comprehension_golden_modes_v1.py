#!/usr/bin/env python3
"""Unit expectations for comprehension golden modes — default vs strong vs escalation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GOLDEN = ROOT / "data" / "comprehension-golden-v1.json"


def main() -> int:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))

    from fbe_comprehension_eval_batch_v1 import _case_runs_in_mode, run_eval_batch  # noqa: WPS433

    doc = json.loads(GOLDEN.read_text(encoding="utf-8"))
    cases = doc.get("cases") or []
    escalation_ids = {c["id"] for c in cases if c.get("expect_escalated")}

    for case in cases:
        cid = str(case.get("id") or "")
        if case.get("expect_escalated"):
            assert not _case_runs_in_mode(case, "strong"), f"{cid} must skip in strong mode"
            assert _case_runs_in_mode(case, "default"), f"{cid} must run in default mode"

    default_batch = run_eval_batch(write_receipt=False, require_escalation_case=True)
    assert default_batch.get("evaluated") == len(cases), default_batch
    assert default_batch.get("escalation_ok", 0) >= 1, default_batch

    strong_batch = run_eval_batch(variation_key="strong", write_receipt=False)
    assert strong_batch.get("skipped") == len(escalation_ids), strong_batch
    assert strong_batch.get("evaluated") == len(cases) - len(escalation_ids), strong_batch

    print(
        f"OK: golden modes default {default_batch.get('passed')}/{default_batch.get('evaluated')} "
        f"strong {strong_batch.get('passed')}/{strong_batch.get('evaluated')} "
        f"escalation_cases={list(escalation_ids)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
