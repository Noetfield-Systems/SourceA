#!/usr/bin/env bash
# CRITICAL — prompt_router dry-run + JSON envelope + governance event
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
EVENTS="${HOME}/.sina/agent-governance-events.jsonl"
before=0
if [[ -f "$EVENTS" ]]; then
  before=$(wc -l < "$EVENTS" | tr -d ' ')
fi

for kw in implement fix debug 10loop "PLAN WITH NO ASF"; do
  out=$(python3 prompt_router.py --keyword "$kw" --lane sourcea --dry-run 2>&1) || {
    echo "FAIL: dry-run keyword=$kw exit=$?"
    echo "$out" | tail -5
    exit 1
  }
  if [[ -z "$out" ]]; then
    echo "FAIL: empty dry-run for keyword=$kw"
    exit 1
  fi
done

json=$(python3 prompt_router.py --keyword implement --lane sourcea --json 2>&1) || {
  echo "FAIL: --json implement"
  exit 1
}
python3 -c "
import json, sys
d=json.loads(sys.argv[1])
assert d.get('ok') is True, d
assert d.get('meta', {}).get('pick_id'), 'missing pick_id'
assert d.get('prompt'), 'missing prompt'
print('OK: json envelope pick_id=', d['meta']['pick_id'])
" "$json"

python3 prompt_router.py --keyword implement --lane sourcea --dry-run >/dev/null
after=0
if [[ -f "$EVENTS" ]]; then
  after=$(wc -l < "$EVENTS" | tr -d ' ')
fi
if [[ "$after" -le "$before" ]]; then
  echo "FAIL: governance event not appended ($before -> $after)"
  exit 1
fi

echo "OK: validate-prompt-router-v1 · keywords=5 · pick_id present · event logged"
