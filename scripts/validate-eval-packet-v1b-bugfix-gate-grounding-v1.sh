#!/usr/bin/env bash
# sa-0153 — bugfix-gate grounding paths model_dispatch + gate_receipts + gate_receipt_lib
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    BUGFIX_GATE_PATHS,
    build_task_grounding,
    cross_check_bugfix_gate_grounding,
)

errs = cross_check_bugfix_gate_grounding()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g = build_task_grounding(
    task_id="bugfix-gate",
    prompt="Fix model_dispatch when gate_eligible is false in enforce mode",
    keywords=["gate_eligible", "enforce", "model_dispatch", "block"],
)
paths = list(g.get("expected_paths") or [])
for rel in BUGFIX_GATE_PATHS:
    assert rel in paths, paths

print(
    "OK: validate-eval-packet-v1b-bugfix-gate-grounding-v1 · "
    "model_dispatch gate_decision + gate_receipts + gate_receipt_lib (sa-0153)"
)
PY
