#!/usr/bin/env bash
# validate-agentic-enforcement-stack-v2-v1.sh — v2 conduct + spine + session gate wiring
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-agentic-enforcement-stack-v2-v1 — $*" >&2; exit 1; }

test -f "$ROOT/SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md" || fail "v2 law missing"
test -f "$ROOT/scripts/agentic_conduct_gate_v1.py" || fail "conduct gate script missing"

grep -q "AGENT_SESSION_GATE" "$ROOT/scripts/governance_event_spine_v1.py" || fail "spine event type missing"
grep -q "conduct_gate" "$ROOT/scripts/agent_session_gate_run_v1.py" || fail "session gate conduct step missing"
grep -q "agent-session-gate-receipt-v1.1" "$ROOT/scripts/agent_session_gate_run_v1.py" || fail "receipt schema v1.1 missing"

python3 scripts/agentic_conduct_gate_v1.py --role any --json | python3 -c "
import json,sys
t=sys.stdin.read()
r=json.loads(t[t.find('{'):])
assert r.get('schema')=='agentic-conduct-gate-v1', r
assert r.get('law','').endswith('v2.md')
print('OK: conduct gate any role')
"

gate_out="$(
  python3 scripts/agent_session_gate_run_v1.py --role any --json 2>&1 || true
)"
echo "$gate_out" | python3 -c "
import json,sys
t=sys.stdin.read()
r=json.loads(t[t.find('{'):])
assert r.get('ok'), r
assert r.get('stack_version')==2, r
assert r.get('schema')=='agent-session-gate-receipt-v1.1', r
steps=[s['step'] for s in r.get('steps',[])]
assert 'conduct_gate' in steps, steps
print('OK: session gate v2 stack_version=2 gate='+str(r.get('gate_id','?')))
"

test -f ~/.sina/agent_session_gate_receipt_v1.json || fail "receipt not written"

echo "OK: validate-agentic-enforcement-stack-v2-v1 · law · conduct · spine · receipt v1.1"
