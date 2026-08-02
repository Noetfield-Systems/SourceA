#!/usr/bin/env bash
# validate-commercial-sender-guard-v1.sh — official FROM only; block personal Mail open
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-commercial-sender-guard-v1 — $*" >&2; exit 1; }

[[ -f scripts/commercial_mail_draft_v1.py ]] || fail "missing commercial_mail_draft_v1.py"

python3 - <<'PY' || fail "sender guard import"
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'scripts/commercial_mail_draft_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.is_personal_from("sina.kazemnezhad@icloud.com")
assert not mod.is_personal_from("hello@sourcea.app")
name, email = mod.lane_from("AB1")
assert email == "hello@sourcea.app"
print("OK: sender guard module")
PY

# open-mail must refuse when official account missing from Mail.app
if python3 scripts/commercial_eval_booking_agent_v1.py \
    --row-id cp-32ddb1794d --to prospect@agency.com --open-mail 2>/dev/null; then
  fail "open-mail should refuse without hello@sourcea.app in Mail.app"
fi
echo "OK: open-mail blocked until official Mail account configured"

python3 scripts/commercial_mail_draft_v1.py --lane AB1 --check-mail --json >/dev/null || true
echo "PASS: validate-commercial-sender-guard-v1"
