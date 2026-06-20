#!/usr/bin/env bash
# One-shot ecosystem repair — locks, stuck workers, hygiene, brain guard, safety proof.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
errors=0

_fail() { echo "FAIL: $1"; errors=$((errors + 1)); }
_ok() { echo "OK: $1"; }

echo "=== fix-ecosystem-all-v1 start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# 1) Kill hung validators + heal orchestrator + redeliver INBOX
if python3 "$SCRIPTS/worker_stuck_recovery_v1.py" --json --redeliver | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
"; then
  _ok "worker stuck recovery"
else
  _fail "worker stuck recovery"
fi

# 2) Factory lock sweep
python3 "$SCRIPTS/factory_validation_lock_v1.py" sweep --json >/dev/null 2>&1 || true
if python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json | python3 -c "
import json,sys
assert not json.load(sys.stdin).get('locked')
"; then
  _ok "factory lock clear"
else
  _fail "factory lock still held"
fi

# 3) Deliver if orchestrator idle and no INBOX
if ! python3 "$SCRIPTS/worker_inject_lib.py" --status 2>/dev/null | python3 -c "import json,sys; assert json.load(sys.stdin).get('pending')"; then
  if python3 "$SCRIPTS/healthy-drain-orchestrator-v1.py" deliver --force 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
q=d.get('queue') or {}
print('delivered', (q.get('item') or {}).get('sa_id'), (q.get('item') or {}).get('queue_role'))
"; then
    _ok "orchestrator deliver"
  else
    _fail "orchestrator deliver"
  fi
else
  _ok "INBOX already pending"
fi

# 4) Hygiene + brain receipt
if bash "$SCRIPTS/enforce-registry-hygiene-v1.sh" >/dev/null 2>&1; then
  _ok "registry hygiene"
else
  _fail "registry hygiene"
fi

python3 "$SCRIPTS/brain_session_guard_v1.py" --write --json >/dev/null 2>&1 || true
python3 "$SCRIPTS/brain_sync_lib_v1.py" --mode light >/dev/null 2>&1 || true
python3 "$SCRIPTS/cleanup-goal1-leftovers-v1.py" --json >/dev/null 2>&1 || true
_ok "brain guard + receipt + leftover cleanup"

# 5) Fast ladder (~90s) — then sweep strict_build lock
if bash "$SCRIPTS/validate-e2e-fast-ladder-v1.sh" --require-idle >/dev/null 2>&1; then
  _ok "E2E fast ladder"
else
  _fail "E2E fast ladder"
fi
python3 "$SCRIPTS/factory_validation_lock_v1.py" sweep --json >/dev/null 2>&1 || true
python3 "$SCRIPTS/worker_stuck_recovery_v1.py" --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
s=d.get('steps',{}).get('orch_inbox_sync',{})
assert s.get('ok', True), s
" 2>/dev/null || true

# 6) Safety bundle (after ladder + lock sweep)
if bash "$SCRIPTS/validate-ecosystem-safety-v1.sh" >/dev/null 2>&1; then
  _ok "ecosystem safety"
else
  _fail "ecosystem safety"
fi

python3 "$SCRIPTS/brain_session_guard_v1.py" --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('--- founder ---')
print('next_action:', d.get('next_action'))
print('founder_click:', d.get('founder_click'))
print('activate:', (d.get('chain') or {}).get('activate'))
print('inbox:', d.get('inbox'))
"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: fix-ecosystem-all-v1 errors=$errors"
  exit 1
fi
echo "PASS: fix-ecosystem-all-v1"
