#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governance-self-heal-g7-v1 — $*" >&2; exit 1; }

LAW="$ROOT/brain-os/law/GOVERNANCE_SELF_HEAL_G7_LOCKED_v1.md"
[[ -f "$LAW" ]] || fail "missing G7 law"
[[ -f "$ROOT/scripts/governance_self_heal_daemon_v1.py" ]] || fail "missing G7 daemon"
grep -q "s10_eternal_audit_loop" "$ROOT/scripts/governance_self_heal_daemon_v1.py" || fail "S10 delegate missing"
grep -q "governance_projection_g3" "$ROOT/scripts/governance_self_heal_daemon_v1.py" || fail "G3 delegate missing"
grep -q "maybe_run_heal_from_monitor" "$ROOT/scripts/monitor_live_sync_v1.py" || fail "monitor hook missing"
[[ -f "$ROOT/scripts/com.sourcea.g7-governance-self-heal.plist" ]] || fail "missing launchd plist"
[[ -f "$ROOT/scripts/install-g7-self-heal-launchd.sh" ]] || fail "missing launchd installer"

python3 "$ROOT/scripts/governance_self_heal_daemon_v1.py" --scan --json >/dev/null || fail "scan"
python3 "$ROOT/scripts/governance_self_heal_daemon_v1.py" --heal --dry-run --json >/dev/null || fail "heal dry-run"
[[ -f "$HOME/.sina/governance-self-heal-receipt-v1.json" ]] || fail "missing receipt"

python3 -c "
import json
from pathlib import Path
r=json.loads(Path.home().joinpath('.sina/governance-self-heal-receipt-v1.json').read_text())
assert r.get('schema')=='governance-self-heal-receipt-v1', r.get('schema')
assert r.get('findings'), 'no findings'
assert r.get('delegates',{}).get('g3')
assert r.get('delegates',{}).get('s10')
ids={f.get('id') for f in r.get('findings',[])}
for need in ('spine_ledger','reference_graph','canonical_hub','projection_queue','monitor_mirror'):
    assert need in ids, need
" || fail "receipt shape"

echo "OK: validate-governance-self-heal-g7-v1"
