#!/usr/bin/env bash
# validate-factory-spawn-gate-v1.sh — drain entrypoints must call exit_if_spawn_blocked (AS-04)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"

fail() { echo "FAIL: validate-factory-spawn-gate-v1 — $*" >&2; exit 1; }

grep -q "def exit_if_spawn_blocked" "$SCRIPTS/factory_control_v1.py" || fail "missing exit_if_spawn_blocked"

for file in \
  worker_healthy_pack_loop_v1.py \
  worker_healthy_pack_autodrain_v1.py \
  goal1_unified_autorun_v1.py; do
  grep -q "exit_if_spawn_blocked" "$SCRIPTS/$file" \
    || fail "$file must call exit_if_spawn_blocked at entry"
done

echo "OK: validate-factory-spawn-gate-v1"
