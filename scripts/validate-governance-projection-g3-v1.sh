#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governance-projection-g3-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/governance_projection_g3_v1.py" ]] || fail "missing G3 module"
grep -q "LAW_TOUCHED" "$ROOT/SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md" || fail "schema LAW_TOUCHED"
grep -q "governance_projection_g3" "$ROOT/scripts/align_command_data_ui_v1.py" || fail "align not wired"
grep -q "assert_projection_write_allowed" "$ROOT/scripts/sina_command_lib.py" || fail "hub write gate missing"

python3 "$ROOT/scripts/governance_projection_g3_v1.py" \
  --law-touched GOV_EVENT_SPINE --reason g3_validator_probe --drain --json >/dev/null \
  || fail "law_touched drain"

[[ -f "$HOME/.sina/governance-projection-g3-receipt-v1.json" ]] || fail "missing g3 receipt"
[[ -f "$HOME/.sina/governance-projection-queue-v1.jsonl" ]] || fail "missing projection queue"
[[ -f "$HOME/.sina/governance-projection-gate-v1.json" ]] || fail "missing projection gate"

python3 -c "
import json
from pathlib import Path
r=json.loads(Path.home().joinpath('.sina/governance-projection-g3-receipt-v1.json').read_text())
assert r.get('schema')=='governance-projection-g3-receipt-v1', r.get('schema')
assert r.get('law_row_id')=='GOV_EVENT_SPINE'
assert r.get('event_id')
assert r.get('impact_ok')
q=Path.home().joinpath('.sina/governance-projection-queue-v1.jsonl').read_text().strip().splitlines()
assert q, 'empty queue'
last=json.loads(q[-1])
assert last.get('status')=='done', last.get('status')
" || fail "g3 receipt or queue shape"

python3 -c "
import json
from pathlib import Path
p=Path.home()/'.sina/governance-event-spine-v1.jsonl'
rows=[json.loads(l) for l in p.read_text().splitlines() if l.strip()]
assert any(r.get('event_type')=='LAW_TOUCHED' for r in rows[-12:]), 'no LAW_TOUCHED'
" || fail "spine LAW_TOUCHED row"

bash "$ROOT/scripts/validate-truth-bundle-registry-v1.sh"

echo "OK: validate-governance-projection-g3-v1"
