#!/usr/bin/env bash
# INCIDENT-014 — every honest-count mutation path must call brain_sync_lib_v1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"

test -f "$SCRIPTS/brain_sync_lib_v1.py"
test -f "$SCRIPTS/validate-brain-snapshot-sync-v1.sh"

HOOKS=(
  "closeout_sa_task.py:sync_brain_snapshot"
  "advance-healthy-queue-v1.py:sync_brain_snapshot"
  "healthy-drain-orchestrator-v1.py:sync_brain_snapshot"
  "worker_healthy_pack_autodrain_v1.py:sync_brain_snapshot"
  "goal1_worker_batch_loop_v1.py:sync_brain_snapshot"
  "hub_self_refresh_v1.py:brain_sync_lib_v1"
  "enforce-registry-hygiene-v1.sh:brain_sync_lib_v1"
  "sina_command_lib.py:brain_sync_lib_v1"
  "sync_founder_missed_actions_v1.py:brain_snapshot_status"
  "monitor.html:Brain sync"
)

missing=0
for entry in "${HOOKS[@]}"; do
  file="${entry%%:*}"
  needle="${entry#*:}"
  path="$SCRIPTS/$file"
  if [ "$file" = "monitor.html" ]; then
    path="$ROOT/monitor.html"
  fi
  if ! grep -q "$needle" "$path" 2>/dev/null; then
    echo "FAIL: missing $needle in $file" >&2
    missing=$((missing + 1))
  fi
done

# Hub action id must exist for founder ↺ repair
grep -q 'founder-brain-sync-monitor' "$SCRIPTS/sina_command_lib.py"
grep -q 'brain_sync_monitor' "$SCRIPTS/sina_command_lib.py"

if [ "$missing" -ne 0 ]; then
  exit 1
fi

echo "OK: validate-brain-sync-hooks-v1 · ${#HOOKS[@]} hook sites wired"
