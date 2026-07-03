#!/usr/bin/env bash
# validate-trigger-registry-v1.sh — L14/L15 pre-merge: trigger registry drift-clean
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-trigger-registry-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/trigger-registry-v1.json" ]] || fail "missing trigger-registry-v1.json"
[[ -f "$ROOT/data/github-automation-governance-v1.json" ]] || fail "missing github-automation-governance-v1.json"

grep -q 'SA-T-brain-loop' "$ROOT/data/trigger-registry-v1.json" && fail "SA-T-brain-loop must not be in registry"

SF_WR="$ROOT/cloud/workers/signal-factory-tick-v1/wrangler.toml"
if [[ -f "$SF_WR" ]] && grep -q '^\[triggers\]' "$SF_WR"; then
  fail "signal-factory-tick-v1 must not have [triggers] — piggyback only"
fi

grep -q '"kind": "piggyback"' "$ROOT/data/trigger-registry-v1.json" || fail "SA-T-signal-factory must be piggyback"

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"

STRICT=""
[[ -d "$ROOT/.github/workflows" ]] && STRICT="--strict"

SWEEP_OUT="$ROOT/receipts/proof/trigger-sweep-latest-v1.json"
mkdir -p "$ROOT/receipts/proof"
"$PY" "$ROOT/scripts/sandbox_health_sweep_v1.py" --json $STRICT > "$SWEEP_OUT" || {
  cat "$SWEEP_OUT" 2>/dev/null || true
  fail "sandbox sweep failed"
}
"$PY" -c "
import json, sys
row = json.load(open('$SWEEP_OUT'))
if not row.get('ok') and '$STRICT' == '--strict':
    print(json.dumps(row, indent=2))
    sys.exit(1)
print(row.get('report_line', 'trigger_sweep_ok'))
"

echo "PASS: validate-trigger-registry-v1.sh"
