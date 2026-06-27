#!/usr/bin/env bash
# validate-commercial-recipient-guard-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-commercial-recipient-guard-v1 — $*" >&2; exit 1; }

[[ -f scripts/commercial_recipient_guard_v1.py ]] || fail "missing guard module"

python3 - <<'PY' || fail "guard import"
import importlib.util
spec = importlib.util.spec_from_file_location('g', 'scripts/commercial_recipient_guard_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.is_placeholder_to("PASTE_RECIPIENT@company.com")
assert mod.is_blocked_recipient("hello@sourcea.app")[0]
print("OK: guard module")
PY

# All outbound to.txt must be placeholder OR valid prospect — never founder personal
python3 scripts/commercial_recipient_guard_v1.py --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
if d.get('localhost_urls'):
    print('LOCALHOST in packs:', d.get('issues'))
    raise SystemExit(1)
if not d.get('ok'):
    print('BLOCKED:', d.get('blocked'))
    raise SystemExit(1)
print('OK:', d.get('placeholders',0), 'draft placeholder(s) · no founder/personal/localhost in packs')
"

# open-mail without --to must fail
if python3 scripts/commercial_eval_booking_agent_v1.py --row-id cp-32ddb1794d --open-mail 2>/dev/null; then
  fail "open-mail should refuse without --to"
fi
echo "OK: open-mail blocked without prospect --to"

echo "PASS: validate-commercial-recipient-guard-v1"
