#!/usr/bin/env bash
# n8n lane verify — tier-gated suite. Exit 0 = PASS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

for v in validate-n8n-tier0-v1.sh validate-n8n-tier1-v1.sh validate-n8n-tier2-v1.sh validate-n8n-tier3-v1.sh validate-n8n-tier4-v1.sh validate-n8n-tier5-v1.sh validate-n8n-full-manifest-v1.sh; do
  if bash "$ROOT/scripts/$v"; then
    echo "OK: $v"
  else
    echo "FAIL: $v"
    fail=1
  fi
done

python3 "$ROOT/scripts/n8n_automation.py" extended >/dev/null || fail=1
ext_ok=$(python3 -c "from n8n_automation import test_extended_flow; import json; print('true' if test_extended_flow(auto_start_n8n=False).get('ok') else 'false')")
check "$ext_ok" "n8n extended flow"

if [[ $fail -ne 0 ]]; then
  echo "validate-n8n.sh: FAIL"
  exit 1
fi
echo "validate-n8n.sh: PASS"
exit 0
