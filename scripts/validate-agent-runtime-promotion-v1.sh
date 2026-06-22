#!/usr/bin/env bash
# validate-agent-runtime-promotion-v1.sh — golden promotion gate (read-only, no SSOT auto-promote)
set -euo pipefail
cd "$(dirname "$0")/.."

test -f scripts/agent_runtime_promotion_report_v1.py || { echo "FAIL missing promotion report"; exit 1; }
test -f data/cloud-comprehension-bay-v1.json || { echo "FAIL missing bay SSOT"; exit 1; }

SSOT_BEFORE=$(python3 -c "import json; print(json.dumps(json.load(open('data/cloud-comprehension-bay-v1.json')), sort_keys=True))")

python3 scripts/agent_runtime_promotion_report_v1.py --no-write --json | python3 -c "
import json,sys
from pathlib import Path

r=json.load(sys.stdin)
for key in ('schema','promotion_ready','default_pass_rate','strong_pass_rate','active_variation_key','for_founder'):
    assert key in r, f'missing {key}'

default_rate=float(r.get('default_pass_rate') or 0)
strong_rate=float(r.get('strong_pass_rate') or 0)
min_rate=float(r.get('min_pass_rate') or 0.875)

assert default_rate >= 1.0, f'default must be 100% got {default_rate}'
if strong_rate < 1.0 and strong_rate >= min_rate:
    print(f'WARN: strong golden {strong_rate:.0%} below 100% but above gate')
assert strong_rate >= min_rate, r
print('OK: promotion report fields + pass rates')
"

p="$HOME/.sina/agent-runtime-promotion-report-v1.json"
if [[ -f "$p" ]]; then
  python3 -c "
import json
from pathlib import Path
receipt=json.loads(Path('$p').read_text())
assert receipt.get('schema')=='agent-runtime-promotion-report-v1', receipt
print('OK: promotion receipt on disk')
"
else
  echo "WARN: promotion receipt missing at $p (run report without --no-write to materialize)"
fi

SSOT_AFTER=$(python3 -c "import json; print(json.dumps(json.load(open('data/cloud-comprehension-bay-v1.json')), sort_keys=True))")
if [[ "$SSOT_BEFORE" != "$SSOT_AFTER" ]]; then
  echo "FAIL: promotion report mutated cloud-comprehension-bay SSOT"
  exit 1
fi
echo "OK: SSOT active_variation_key unchanged after promotion report"

echo "PASS: validate-agent-runtime-promotion-v1"
