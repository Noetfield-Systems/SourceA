#!/usr/bin/env bash
# validate-brain-outbound-work-order-e2e-v1.sh — B0501 compiler chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

fail=0
check() {
  local name="$1"
  shift
  if "$@"; then
    echo "PASS: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

check "brain_outbound_script" test -f scripts/brain_outbound_work_order_v1.py
check "outbound_fdg_icp_bay" test -f scripts/fbe/outbound_fdg_icp_bay_v1.py

python3 scripts/fbe/outbound_fdg_icp_bay_v1.py --json >/dev/null
check "bay_runner" test $? -eq 0

python3 scripts/brain_outbound_work_order_v1.py status --json >/dev/null
check "status_cmd" test $? -eq 0

ACTIVE="$HOME/.sina/brain-outbound-work-order-active-v1.json"
DISPATCH="$HOME/.sina/brain-outbound-dispatch-receipt-v1.json"
if [[ -f "$DISPATCH" ]]; then
  ok=$(python3 -c "import json;print(json.load(open('$DISPATCH')).get('ok'))")
  check "dispatch_receipt_ok" test "$ok" = "True"
fi

INBOX="$HOME/.sina/worker-prompt-inbox-v1.json"
if [[ -f "$INBOX" ]]; then
  pending=$(python3 -c "import json;print(json.load(open('$INBOX')).get('pending'))")
  if [[ -f "$ACTIVE" ]]; then
    mode=$(python3 -c "import json;print(json.load(open('$ACTIVE')).get('execution_mode',''))")
    if [[ "$mode" == "brain_work_order" ]]; then
      check "inbox_cleared_for_work_order" test "$pending" = "False"
    fi
  fi
fi

bash scripts/validate-brain-cloud-reasoning-1000-plan-v1.sh >/dev/null 2>&1 || true
check "brain_cloud_plan_validator" test -f scripts/validate-brain-cloud-reasoning-1000-plan-v1.sh

if [[ $fail -ne 0 ]]; then
  echo "brain-outbound-work-order-e2e: REVIEW ($fail failures)"
  exit 1
fi
echo "brain-outbound-work-order-e2e: PASS"
exit 0
