#!/usr/bin/env bash
# Cross-check classifier LOW_RISK action_ids vs allowlist ACTION_TO_TASK_CLASS.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from runtime.dispatch_policy.classifier import (
    LOW_RISK_ACTIONS,
    LOW_RISK_TASK_CLASS,
    cross_check_classifier_task_ids,
)
from runtime.dispatch_policy.policy_engine import dispatch_policy_payload

errs = cross_check_classifier_task_ids()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

payload = dispatch_policy_payload()
alignment = payload.get("alignment") or {}
assert alignment.get("mapping_ok") is True, alignment

print(
    f"OK: validate-dispatch-classifier-task-ids-v1 · "
    f"{len(LOW_RISK_ACTIONS)} low-risk actions · "
    f"tasks={sorted(LOW_RISK_TASK_CLASS.values())}"
)
PY
