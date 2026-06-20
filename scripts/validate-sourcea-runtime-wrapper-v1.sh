#!/usr/bin/env bash
# validate-sourcea-runtime-wrapper-v1.sh — Runtime Wrapper v1 smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
SINA="${HOME}/.sina"
fail=0

check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

check test -f data/sourcea-runtime-profiles-v1.json
check test -f scripts/sourcea_runtime_wrapper_v1.py
check grep -q 'governance' data/sourcea-runtime-profiles-v1.json
check grep -q 'agency' data/sourcea-runtime-profiles-v1.json
check grep -q 'finance' data/sourcea-runtime-profiles-v1.json

python3 scripts/sourcea_runtime_wrapper_v1.py profile list --json >/dev/null
echo "PASS: profile list CLI"

block="$(python3 scripts/sourcea_runtime_wrapper_v1.py dispatch --action outreach.send --profile governance --context '{"approval_ref":"x"}' --dry-run --json || true)"
echo "$block" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('verdict')=='BLOCK', d
assert d.get('schema')=='sourcea-runtime-wrapper-receipt-v1'
print('PASS: governance blocks dispatch (profile or global gate)')
" || fail=1

pass="$(python3 scripts/sourcea_runtime_wrapper_v1.py dispatch --action validate.run --profile agency --context '{"validator":"smoke"}' --dry-run --json || true)"
echo "$pass" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('schema')=='sourcea-runtime-wrapper-receipt-v1'
assert d.get('verdict') in ('PASS','BLOCK'), d
print('PASS: agency validate.run receipt · verdict', d.get('verdict'))
" || fail=1

check test -f "${SINA}/runtime-wrapper/latest-v1.json"

if grep -q 'runtime-wrapper/v1' scripts/sina-command-server.py; then
  echo "PASS: hub API route wired"
else
  echo "FAIL: hub API route missing"
  fail=1
fi

if grep -q 'Governed Runtime' SourceA-landing/green-unified/pricing.html; then
  echo "PASS: pricing row present"
else
  echo "FAIL: pricing row missing"
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo "=== ALL CHECKS PASSED ==="
else
  echo "=== VALIDATOR FAILED ==="
fi
exit "$fail"
