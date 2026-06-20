#!/usr/bin/env bash
# validate-founder-signal-impact-v1.sh — founder intake → impact machine exists and runs
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-founder-signal-impact-v1 — $*" >&2; exit 1; }

[[ -f scripts/founder_signal_impact_v1.py ]] || fail "missing founder_signal_impact_v1.py"

python3 scripts/founder_signal_impact_v1.py \
  --text "ASF ORDER: test founder signal intake machine" \
  --write --json >/tmp/founder-signal-test.json \
  || fail "analyze run failed"

python3 -c "
import json, sys
from pathlib import Path
d=json.loads(Path('/tmp/founder-signal-test.json').read_text())
assert d.get('schema')=='founder-signal-impact-v1', d
assert d.get('signal_class'), 'no class'
assert d.get('threat',{}).get('level'), 'no threat level'
latest=Path.home()/'.sina/founder-signal-impact-latest-v1.json'
assert latest.is_file(), 'missing latest receipt'
"

grep -q 'FOUNDER_SIGNAL' scripts/governance_event_spine_v1.py \
  || fail "spine missing FOUNDER_SIGNAL event type"

[[ -f scripts/governance_signal_regulator_v1.py ]] || fail "missing governance_signal_regulator_v1.py"

python3 scripts/governance_signal_regulator_v1.py \
  --text "INCIDENT brain-incident governance regulation 13 layers locked law" \
  --json >/tmp/gov-signal-reg-test.json \
  || fail "regulator run failed"

python3 -c "
import json
from pathlib import Path
d=json.loads(Path('/tmp/gov-signal-reg-test.json').read_text())
assert d.get('schema')=='governance-signal-regulator-v1'
assert len(d.get('layers_13') or [])==14, len(d.get('layers_13') or [])
assert d.get('composite_risk',{}).get('score') is not None
assert d.get('discuss_gate',{}).get('rule')
"

echo "OK: validate-founder-signal-impact-v1 · intake + 13-layer regulator wired"
