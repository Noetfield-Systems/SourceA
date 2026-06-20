#!/usr/bin/env bash
# validate-founder-close-line-gate-v1.sh — INCIDENT-028 mechanical block
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-founder-close-line-gate-v1 — $*" >&2; exit 1; }

# Must reject stale phrase (capture JSON — gate exits 1 on hit; pipefail would false-fail)
stale_json="$(python3 scripts/founder_close_line_gate_v1.py --text "Open Prompt feed and tap Confirm auto-send 10 prompts" --json || true)"
python3 -c "
import json,sys
r=json.loads(sys.argv[1])
assert not r.get('ok'), r
assert r.get('hits'), r
" "$stale_json" || fail "gate did not reject stale auto-send phrase"

# Must allow correct phrase
python3 scripts/founder_close_line_gate_v1.py --text "Hub Safety check — live next 10 from machine queue" --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok'), r
" || fail "gate rejected valid close-line"

conduct_json="$(python3 scripts/agentic_conduct_gate_v1.py --role worker --task-text "review the 10 steps and tap Confirm" --json || true)"
python3 -c "
import json,sys
r=json.loads(sys.argv[1])
assert not r.get('ok'), r
assert any('founder_close_line' in v for v in (r.get('violations') or [])), r
" "$conduct_json" || fail "conduct gate did not fail on stale close-line"

session_json="$(python3 scripts/agent_session_gate_run_v1.py --role worker --scan-text "review the 10 steps tap Confirm auto-send" --json || true)"
python3 -c "
import json,sys
r=json.loads(sys.argv[1])
assert not r.get('ok'), r
viol=r.get('conduct',{}).get('violations') or []
assert any('founder_close_line' in v for v in viol), r
" "$session_json" || fail "session gate did not fail closed on stale reply"

echo "OK: validate-founder-close-line-gate-v1"
