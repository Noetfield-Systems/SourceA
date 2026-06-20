#!/usr/bin/env bash
# P0 operational closure — substrate + WF1 passes + WF8 webhook + cooldown receipt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$SINA/n8n-receipts/health/tier0-pass.json" ]] && check true "tier0-pass.json" || check false "tier0-pass.json"
[[ -f "$SINA/n8n-receipts/health/p0-operational-pass.json" ]] && check true "p0-operational-pass.json" || check false "p0-operational-pass.json"

if [[ -f "$SINA/n8n-receipts/health/p0-operational-pass.json" ]]; then
  python3 -c "
import json
from pathlib import Path
g = json.loads(Path('$SINA/n8n-receipts/health/p0-operational-pass.json').read_text())
items = g.get('items') or {}
assert g.get('ok'), 'gate ok false'
assert items.get('substrate'), 'substrate'
assert items.get('wf1_manual_passes', 0) >= 2, 'wf1 passes'
assert items.get('wf8_webhook_active'), 'wf8 active'
assert items.get('cooldown_receipt'), 'cooldown receipt'
overall = items.get('health_ping_overall', 'red')
assert overall in ('green', 'yellow'), overall
print('PASS: p0 gate schema')
" && check true "p0 gate fields" || check false "p0 gate fields"
fi

[[ -f "$SINA/n8n-receipts/mac-health/cooldown.jsonl" ]] && check true "cooldown.jsonl" || check false "cooldown.jsonl"

export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
overall=$(python3 -c "from n8n_automation import test_health_ping_dry_run; print(test_health_ping_dry_run().get('overall',''))")
[[ "$overall" == "green" || "$overall" == "yellow" ]] && check true "health_ping $overall" || check false "health_ping ($overall)"

sqlite3 "${HOME}/.n8n/database.sqlite" "SELECT name FROM workflow_entity WHERE name LIKE '%Stack Health%' OR name='wf-mac-health-cooldown-v1';" 2>/dev/null | grep -q . \
  && check true "WF1+WF8 in n8n db" || check false "WF1+WF8 in n8n db"

if [[ $fail -eq 0 ]]; then
  echo "validate-n8n-p0-operational-v1: PASS"
  exit 0
fi
echo "validate-n8n-p0-operational-v1: FAIL"
exit 1
