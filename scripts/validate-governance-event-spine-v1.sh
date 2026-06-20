#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governance-event-spine-v1 — $*" >&2; exit 1; }

SCHEMA="$ROOT/SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md"
GOLDEN="$ROOT/brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md"
[[ -f "$SCHEMA" ]] || fail "missing spine schema law"
[[ -f "$GOLDEN" ]] || fail "missing golden rule law"
grep -q "State is canonical" "$GOLDEN" || fail "golden rule text"
grep -q "governance-event-spine-v1.1" "$SCHEMA" || fail "spine v1.1 schema"
grep -q "GOV_EVENT_SPINE" "$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md" || fail "authority row"
grep -q "governance_event_spine" "$ROOT/scripts/governance_propagation_cascade_v1.py" || fail "cascade not wired"
grep -q "governance_event_spine" "$ROOT/scripts/goal1_lane_broker.py" || fail "broker not wired"

python3 "$ROOT/scripts/governance_reference_graph_v1.py" --build >/dev/null || fail "graph build"
[[ -f "$HOME/.sina/governance-reference-graph-v1.json" ]] || fail "missing reference graph"
python3 -c "
import json,sys
g=json.load(open('$HOME/.sina/governance-reference-graph-v1.json'))
assert g.get('node_count',0)>=50, g.get('node_count')
assert g.get('knowledge_edges'), 'missing knowledge_edges'
" || fail "graph node_count or knowledge_edges"

python3 "$ROOT/scripts/governance_event_spine_v1.py" --append-probe >/dev/null || fail "spine append"
[[ -f "$HOME/.sina/governance-event-spine-v1.jsonl" ]] || fail "missing spine ledger"
python3 -c "
import json
from pathlib import Path
p=Path.home()/'.sina'/'governance-event-spine-v1.jsonl'
last=[l for l in p.read_text().splitlines() if l.strip()][-1]
row=json.loads(last)
assert row.get('schema')=='governance-event-spine-v1.1', row.get('schema')
for k in ('replay_pointer','validator_set','affected_objects','projection_version','status'):
    assert k in row, k
" || fail "spine v1.1 row fields"

python3 "$ROOT/scripts/governance_reference_graph_v1.py" --impact GOV_EVENT_SPINE | grep -q '"ok": true' || fail "impact scan"

bash "$ROOT/scripts/validate-governance-replay-v1.sh"
bash "$ROOT/scripts/validate-governance-projection-g3-v1.sh"
bash "$ROOT/scripts/validate-governance-self-heal-g7-v1.sh"
bash "$ROOT/scripts/validate-broker-spine-v1.sh"

echo "OK: validate-governance-event-spine-v1"
