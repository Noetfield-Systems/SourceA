#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governance-replay-v1 — $*" >&2; exit 1; }

grep -q "G4" "$ROOT/SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md" || fail "schema G4 section"
[[ -f "$ROOT/scripts/governance_replay_worker_v1.py" ]] || fail "missing replay worker"
grep -q "context-aware" "$ROOT/scripts/governance_replay_worker_v1.py" || fail "replay worker doc"

python3 "$ROOT/scripts/governance_replay_worker_v1.py" --last --event-type WORKER_ROUND --json >/dev/null \
  || fail "replay dry-run"
[[ -f "$HOME/.sina/governance-replay-receipt-v1.json" ]] || fail "missing replay receipt"

python3 -c "
import json
from pathlib import Path
r=json.loads(Path.home().joinpath('.sina/governance-replay-receipt-v1.json').read_text())
assert r.get('schema')=='governance-replay-receipt-v1', r.get('schema')
assert r.get('dry_run') is True
assert r.get('snapshot',{}).get('schema')=='governance-object-snapshot-v1'
assert 'impact_ok' in (r.get('graph_context') or {})
assert r.get('replay_pointer') or r.get('event_id')
" || fail "replay receipt shape"

echo "OK: validate-governance-replay-v1"
