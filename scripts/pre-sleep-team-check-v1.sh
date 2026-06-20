#!/usr/bin/env bash
# Pre-sleep — verify Worker + API scout + CLI prep + orchestrator alignment.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

check() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "PASS  $name"
  else
    echo "FAIL  $name"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== PRE-SLEEP TEAM CHECK ==="
python3 scripts/brain_read_state_v1.py --caller pre_sleep_check | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('state  aligned=' + str(d.get('aligned')) + ' sa=' + str((d.get('heartbeat') or {}).get('sa_id')) + ' pos=' + str((d.get('heartbeat') or {}).get('queue_pos')))
if not d.get('aligned'):
    print('WARN  brain_read_state not aligned — sync ACTIVE_NOW')
"

check "gatekeeper" python3 scripts/gatekeeper_v1.py
check "api_scout_engine" python3 scripts/operating_mode_enforce_v1.py --check-engine --role check --engine api
check "worker_act_engine" python3 scripts/operating_mode_enforce_v1.py --check-engine --role act --engine worker

# CLI ACT must fail while awake (expected)
if python3 scripts/operating_mode_enforce_v1.py --check-engine --role act --engine cli >/dev/null 2>&1; then
  echo "FAIL  cli_act_blocked_while_awake (should be INVALID)"
  FAIL=$((FAIL + 1))
else
  echo "PASS  cli_act_blocked_while_awake"
fi

check "sidecar_api" python3 scripts/sidecar_scout_api_v1.py --json
check "sidecar_cli" python3 scripts/sidecar_prep_cli_v1.py --json

if [[ -f "$ROOT/.sina-loop/INBOX.md" ]] && grep -q 'pending=1' "$ROOT/.sina-loop/INBOX.md"; then
  echo "PASS  worker_inbox_pending"
else
  echo "WARN  worker_inbox_not_pending (deliver may be needed)"
fi

if [[ -f "$HOME/.sina/sidecar-engines-watch-v1.pid" ]] && kill -0 "$(cat "$HOME/.sina/sidecar-engines-watch-v1.pid")" 2>/dev/null; then
  echo "PASS  sidecar_watch_running (API+CLI Phase 1)"
else
  echo "FAIL  sidecar_watch_not_running — run start-sidecar-engines-watch-v1.sh"
  FAIL=$((FAIL + 1))
fi

if [[ -f "$HOME/.sina/overnight-3engine-v1.pid" ]] && kill -0 "$(cat "$HOME/.sina/overnight-3engine-v1.pid")" 2>/dev/null; then
  echo "WARN  overnight_already_running"
else
  echo "PASS  overnight_dispatcher_off (correct before arm sleep)"
fi

echo "=== DONE failures=$FAIL ==="
exit "$FAIL"
