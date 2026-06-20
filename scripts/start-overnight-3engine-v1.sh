#!/bin/bash
# Overnight 3-engine team — API (CHECK/VERIFY) + CLI (ACT) + orchestrator watch.
# Executor only. Law: founder_absent + ACTIVE_NOW overnight sprint.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="$HOME/.sina/overnight-3engine-v1.log"
PIDFILE="$HOME/.sina/overnight-3engine-v1.pid"
MAX_TURNS="${SINA_OVERNIGHT_MAX_TURNS:-29}"
SLEEP_SEC="${SINA_OVERNIGHT_SLEEP_SEC:-30}"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }

if [[ -f "$PIDFILE" ]]; then
  old=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    log "ALREADY_RUNNING pid=$old"
    exit 0
  fi
fi

log "=== OVERNIGHT 3-ENGINE START ==="

# Cost-smart gate — expensive engines only with sleep escalation ON
if ! python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from active_now_v1 import load_active_now
a = load_active_now()
if not a.get("sleep_escalation"):
    print("ABORT: Sleep Escalation off — COST_SMART_ENGINE_SSOT")
    raise SystemExit(1)
if "absent" not in (a.get("founder_mode") or ""):
    print("ABORT: founder_busy — use Worker paste")
    raise SystemExit(1)
print("OK: sleep escalation allowed")
PY
then
  log "ABORT cost-smart gate — set ACTIVE_NOW Sleep Escalation: on + founder_absent"
  exit 1
fi

# ONE boss loop only — kill sidecar watch + worker batch before overnight
python3 "$ROOT/scripts/single_boss_loop_v1.py" claim --mode overnight --kill-others 2>&1 | tee -a "$LOG" || true
python3 "$ROOT/scripts/cleanup-goal1-leftovers-v1.py" --json 2>/dev/null | tee -a "$LOG" || true
python3 "$ROOT/scripts/healthy-drain-orchestrator-v1.py" reset 2>/dev/null | tee -a "$LOG" || true

# Boss queue must match repo before reconcile (stale ~/.sina caused sa-0184 drift)
python3 - <<'PY' | tee -a "$LOG" || true
import sys
sys.path.insert(0, "scripts")
from healthy_queue_ssot_lib import sync_home_queue_from_repo
print(sync_home_queue_from_repo())
PY

# Pointer → first non-done sa in REGISTRY (never re-burn done tasks)
python3 "$ROOT/scripts/reconcile-queue-from-registry-v1.py" --apply 2>/dev/null | tee -a "$LOG" || true

# Broker idle
python3 - <<'PY' | tee -a "$LOG"
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / ".sina/goal1-lane-broker-v1.json"
st = {
    "schema": "goal1-lane-broker-v1",
    "status": "idle",
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "overnight_reset": True,
    "note": "start-overnight-3engine-v1",
}
p.write_text(json.dumps(st, indent=2) + "\n")
print("broker_reset ok")
PY

# Law: never clear kill flag on overnight start — ASF resume token only (Phase 1)
if [[ -f "$HOME/.sina/auto-run-disabled-v1.flag" ]]; then
  log "FREEZE: kill flag ON — overnight loop will exit on first turn"
fi

python3 "$ROOT/scripts/generate-worker-100-paste-queue-v1.py" -n 100 | tee -a "$LOG"

log "gatekeeper preflight:"
python3 "$ROOT/scripts/gatekeeper_v1.py" 2>&1 | tee -a "$LOG" || true

# Scout+Prep run INLINE inside autorun_dispatcher (no second while-true loop)

(
  log "dispatcher watch loop max_turns=$MAX_TURNS sleep=$SLEEP_SEC"
  turn=0
  while [[ "$turn" -lt "$MAX_TURNS" ]]; do
    turn=$((turn + 1))
    log "--- turn $turn/$MAX_TURNS ---"
    if [[ -f "$HOME/.sina/auto-run-disabled-v1.flag" ]]; then
      log "STOP kill flag restored"
      break
    fi
    python3 "$ROOT/scripts/autorun_dispatcher_v1.py" 2>&1 | tee -a "$LOG" || log "dispatcher turn $turn non-zero"
    sleep "$SLEEP_SEC"
  done
  log "=== OVERNIGHT LOOP DONE turns=$turn ==="
) &

echo $! > "$PIDFILE"
log "background pid=$(cat "$PIDFILE") log=$LOG"
log "paste queue: $ROOT/.sina-loop/WORKER-OVERNIGHT-100-PASTE-QUEUE.md"
